"""
Security utilities for the Okta CLI tool.
"""

import os
import json
import time
import base64
import hashlib
import getpass
import shutil
from typing import Dict, List, Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests
from .errors import APIError, ConfigurationError


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive an encryption key from a password and salt.
    
    Args:
        password: The password to derive key from
        salt: Random salt bytes
        
    Returns:
        The derived key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_token(token: str, password: str) -> str:
    """
    Encrypt a token using a password.
    
    Args:
        token: The token to encrypt
        password: The password to use for encryption
        
    Returns:
        The encrypted token as a base64 string
    """
    # Generate a random salt
    salt = os.urandom(16)
    
    # Derive key from password
    key = derive_key(password, salt)
    
    # Encrypt the token
    f = Fernet(key)
    encrypted_token = f.encrypt(token.encode())
    
    # Combine salt and encrypted token
    combined = salt + encrypted_token
    
    # Return as base64 string
    return base64.urlsafe_b64encode(combined).decode()


def decrypt_token(encrypted_token: str, password: str) -> str:
    """
    Decrypt a token using a password.
    
    Args:
        encrypted_token: The encrypted token as a base64 string
        password: The password to use for decryption
        
    Returns:
        The decrypted token
        
    Raises:
        Exception: If decryption fails
    """
    try:
        # Decode from base64
        combined = base64.urlsafe_b64decode(encrypted_token.encode())
        
        # Extract salt and encrypted token
        salt = combined[:16]
        encrypted_data = combined[16:]
        
        # Derive key from password
        key = derive_key(password, salt)
        
        # Decrypt the token
        f = Fernet(key)
        decrypted_token = f.decrypt(encrypted_data)
        
        return decrypted_token.decode()
    except Exception as e:
        raise Exception(f"Failed to decrypt token: {e}")


class SecureConfig:
    """
    Secure configuration manager with encrypted credential storage.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize secure configuration manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.okta")
        
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "secure_config.json")
        self.master_key_file = os.path.join(config_dir, "master.key")
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Set restrictive permissions on config directory
        os.chmod(config_dir, 0o700)
    
    def _get_master_password(self) -> str:
        """
        Get or create the master password.
        
        Returns:
            The master password
        """
        if os.path.exists(self.master_key_file):
            # Use existing master key
            with open(self.master_key_file, 'r') as f:
                key_hash = f.read().strip()
            
            # Prompt for password
            password = getpass.getpass("Enter master password: ")
            
            # Verify password
            if hashlib.sha256(password.encode()).hexdigest() != key_hash:
                raise ConfigurationError("Invalid master password")
            
            return password
        else:
            # Create new master password
            password = getpass.getpass("Create master password: ")
            confirm = getpass.getpass("Confirm master password: ")
            
            if password != confirm:
                raise ConfigurationError("Passwords do not match")
            
            if len(password) < 8:
                raise ConfigurationError("Password must be at least 8 characters")
            
            # Store password hash
            key_hash = hashlib.sha256(password.encode()).hexdigest()
            with open(self.master_key_file, 'w') as f:
                f.write(key_hash)
            
            # Set restrictive permissions
            os.chmod(self.master_key_file, 0o600)
            
            return password
    
    def save_profile(self, profile: str, domain: str, token: str) -> None:
        """
        Save a profile with encrypted credentials.
        
        Args:
            profile: The profile name
            domain: The Okta domain
            token: The API token
        """
        # Get master password
        password = self._get_master_password()
        
        # Load existing config or create new
        config_data = {}
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
        
        # Encrypt the token
        encrypted_token = encrypt_token(token, password)
        
        # Save profile
        config_data[profile] = {
            "domain": domain,
            "encrypted_token": encrypted_token,
            "created_at": time.time(),
            "last_used": time.time()
        }
        
        # Write config file
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(self.config_file, 0o600)
    
    def load_profile(self, profile: str) -> Tuple[str, str]:
        """
        Load a profile and decrypt credentials.
        
        Args:
            profile: The profile name
            
        Returns:
            Tuple of (domain, token)
            
        Raises:
            ValueError: If profile is not found
        """
        if not os.path.exists(self.config_file):
            raise ValueError(f"Profile '{profile}' not found")
        
        with open(self.config_file, 'r') as f:
            config_data = json.load(f)
        
        if profile not in config_data:
            raise ValueError(f"Profile '{profile}' not found")
        
        profile_data = config_data[profile]
        
        # Get master password
        password = self._get_master_password()
        
        # Decrypt token
        token = decrypt_token(profile_data["encrypted_token"], password)
        
        # Update last used time
        profile_data["last_used"] = time.time()
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return profile_data["domain"], token
    
    def list_profiles(self) -> List[str]:
        """
        List all available profiles.
        
        Returns:
            List of profile names
        """
        if not os.path.exists(self.config_file):
            return []
        
        with open(self.config_file, 'r') as f:
            config_data = json.load(f)
        
        return list(config_data.keys())
    
    def delete_profile(self, profile: str) -> None:
        """
        Delete a profile.
        
        Args:
            profile: The profile name
        """
        if not os.path.exists(self.config_file):
            return
        
        with open(self.config_file, 'r') as f:
            config_data = json.load(f)
        
        if profile in config_data:
            del config_data[profile]
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
    
    def create_backup(self) -> str:
        """
        Create a backup of the configuration.
        
        Returns:
            Path to the backup file
        """
        timestamp = int(time.time())
        backup_file = os.path.join(self.config_dir, f"config_backup_{timestamp}.json")
        
        if os.path.exists(self.config_file):
            shutil.copy2(self.config_file, backup_file)
            os.chmod(backup_file, 0o600)
        
        return backup_file
    
    def restore_from_backup(self, backup_file: str) -> None:
        """
        Restore configuration from a backup.
        
        Args:
            backup_file: Path to the backup file
        """
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, self.config_file)
            os.chmod(self.config_file, 0o600)


class TokenValidator:
    """
    Token validation and permission checking.
    """
    
    def __init__(self, domain: str, token: str):
        """
        Initialize token validator.
        
        Args:
            domain: The Okta domain
            token: The API token
        """
        self.domain = domain
        self.token = token
        self.base_url = f"https://{domain}/api/v1"
        self.headers = {
            "Authorization": f"SSWS {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def is_valid(self) -> bool:
        """
        Check if the token is valid.
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_permissions(self) -> Dict[str, bool]:
        """
        Get token permissions.
        
        Returns:
            Dictionary of permissions
        """
        permissions = {
            "users:read": False,
            "users:write": False,
            "groups:read": False,
            "groups:write": False,
            "apps:read": False,
            "apps:write": False
        }
        
        # Test users read permission
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers,
                timeout=10
            )
            permissions["users:read"] = response.status_code == 200
        except requests.exceptions.RequestException:
            pass
        
        # Test groups read permission
        try:
            response = requests.get(
                f"{self.base_url}/groups?limit=1",
                headers=self.headers,
                timeout=10
            )
            permissions["groups:read"] = response.status_code == 200
        except requests.exceptions.RequestException:
            pass
        
        # Test apps read permission
        try:
            response = requests.get(
                f"{self.base_url}/apps?limit=1",
                headers=self.headers,
                timeout=10
            )
            permissions["apps:read"] = response.status_code == 200
        except requests.exceptions.RequestException:
            pass
        
        return permissions
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if token has specific permission.
        
        Args:
            permission: The permission to check
            
        Returns:
            True if permission is granted, False otherwise
        """
        endpoint_map = {
            "users:read": "/users/me",
            "groups:read": "/groups?limit=1",
            "apps:read": "/apps?limit=1"
        }
        
        endpoint = endpoint_map.get(permission)
        if not endpoint:
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


class RateLimiter:
    """
    Client-side rate limiter to prevent API rate limit violations.
    """
    
    def __init__(self, max_requests: int = 1000, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self) -> bool:
        """
        Check if a request can be made without exceeding rate limit.
        
        Returns:
            True if request can be made, False otherwise
        """
        current_time = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        # Check if we're under the limit
        return len(self.requests) < self.max_requests
    
    def record_request(self) -> None:
        """
        Record a request for rate limiting.
        """
        self.requests.append(time.time())
    
    def get_reset_time(self) -> Optional[float]:
        """
        Get the time when rate limit will reset.
        
        Returns:
            Unix timestamp when rate limit resets, or None if not rate limited
        """
        if not self.requests:
            return None
        
        oldest_request = min(self.requests)
        return oldest_request + self.time_window
    
    def wait_for_reset(self) -> None:
        """
        Wait until rate limit resets.
        """
        reset_time = self.get_reset_time()
        if reset_time:
            wait_time = reset_time - time.time()
            if wait_time > 0:
                time.sleep(wait_time)
    
    def get_remaining_requests(self) -> int:
        """
        Get the number of remaining requests in the current window.
        
        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        return max(0, self.max_requests - len(self.requests))


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """
    Get the global rate limiter instance.
    
    Returns:
        The global rate limiter
    """
    return _rate_limiter


def with_rate_limiting(func):
    """
    Decorator to add rate limiting to functions.
    
    Args:
        func: The function to wrap with rate limiting
        
    Returns:
        The wrapped function with rate limiting
    """
    def wrapper(*args, **kwargs):
        limiter = get_rate_limiter()
        
        if not limiter.can_make_request():
            reset_time = limiter.get_reset_time()
            if reset_time:
                wait_time = reset_time - time.time()
                raise APIError(f"Rate limit exceeded. Please wait {wait_time:.1f} seconds before making another request.")
            else:
                raise APIError("Rate limit exceeded. Please wait before making another request.")
        
        limiter.record_request()
        return func(*args, **kwargs)
    
    return wrapper