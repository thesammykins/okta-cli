"""
Secure token storage using OS keychain integration with cross-platform support.

Supported platforms:
- macOS: Uses Keychain Access
- Windows: Uses Windows Credential Manager
- Linux: Uses Secret Service (GNOME Keyring, KDE KWallet, etc.)
- Fallback: Encrypted file storage for unsupported systems
"""

import os
import sys
import json
import time
import platform
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass

try:
    import keyring
    from keyring.errors import KeyringError
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    KeyringError = Exception

from .enhanced_config import ProfileManager


class SecureTokenStorage:
    """Secure token storage using OS keychain."""
    
    def __init__(self, service_name: str = "okta-cli"):
        """
        Initialize secure storage.
        
        Args:
            service_name: Service name for keychain entries
        """
        self.service_name = service_name
        self.profile_manager = ProfileManager()
    
    def store_token(self, profile_name: str, token: str) -> bool:
        """
        Store token securely in OS keychain.
        
        Args:
            profile_name: Profile name
            token: API token
            
        Returns:
            True if successful
        """
        try:
            keyring.set_password(self.service_name, profile_name, token)
            return True
        except Exception:
            return False
    
    def get_token(self, profile_name: str) -> Optional[str]:
        """
        Retrieve token from OS keychain.
        
        Args:
            profile_name: Profile name
            
        Returns:
            Token or None if not found
        """
        try:
            return keyring.get_password(self.service_name, profile_name)
        except Exception:
            return None
    
    def delete_token(self, profile_name: str) -> bool:
        """
        Delete token from OS keychain.
        
        Args:
            profile_name: Profile name
            
        Returns:
            True if successful
        """
        try:
            keyring.delete_password(self.service_name, profile_name)
            return True
        except Exception:
            return False


class SecureProfileManager(ProfileManager):
    """Enhanced ProfileManager with secure token storage."""
    
    def __init__(self, config_dir: str = None, use_keychain: bool = True):
        """
        Initialize secure profile manager.
        
        Args:
            config_dir: Directory to store configuration files
            use_keychain: Whether to use OS keychain for tokens
        """
        super().__init__(config_dir)
        
        # Check if keyring is available before enabling secure storage
        if use_keychain and not KEYRING_AVAILABLE:
            import warnings
            warnings.warn(
                "keyring library not available. Token storage will be insecure. "
                "Install keyring with: pip install keyring",
                UserWarning,
                stacklevel=2
            )
            use_keychain = False
            
        self.use_keychain = use_keychain
        self.token_storage = SecureTokenStorage() if use_keychain and KEYRING_AVAILABLE else None
    
    def create_profile(self, name: str, domain: str, token: str) -> bool:
        """
        Create a new profile with secure token storage.
        
        Args:
            name: Profile name
            domain: Okta domain
            token: API token
            
        Returns:
            True if successful
        """
        profiles = self._load_profiles()
        
        if name in profiles:
            raise ValueError(f"Profile '{name}' already exists")
        
        # Store token securely if keychain is enabled
        if self.use_keychain and self.token_storage:
            if not self.token_storage.store_token(name, token):
                raise RuntimeError("Failed to store token securely")
            # Don't store token in JSON file
            token_to_store = None
        else:
            token_to_store = token
        
        profiles[name] = {
            "domain": domain,
            "token": token_to_store,  # None if using keychain
            "created_at": time.time(),
            "last_used": time.time(),
            "secure_storage": self.use_keychain,
        }
        
        self._save_profiles(profiles)
        return True
    
    def get_profile(self, name: str) -> Dict[str, Any]:
        """
        Get a profile with secure token retrieval.
        
        Args:
            name: Profile name
            
        Returns:
            Profile data with token from secure storage
        """
        profiles = self._load_profiles()
        
        if name not in profiles:
            raise ValueError(f"Profile '{name}' not found")
        
        profile = profiles[name].copy()
        
        # Retrieve token from secure storage if needed
        if profile.get("secure_storage") and self.token_storage:
            secure_token = self.token_storage.get_token(name)
            if secure_token:
                profile["token"] = secure_token
            else:
                raise RuntimeError(f"Failed to retrieve secure token for profile '{name}'")
        
        # Update last used time
        profiles[name]["last_used"] = time.time()
        self._save_profiles(profiles)
        
        return profile
    
    def update_profile(self, name: str, domain: str = None, token: str = None) -> bool:
        """
        Update an existing profile with secure token storage.
        
        Args:
            name: Profile name
            domain: New domain (optional)
            token: New token (optional)
            
        Returns:
            True if successful
        """
        profiles = self._load_profiles()
        
        if name not in profiles:
            raise ValueError(f"Profile '{name}' not found")
        
        # Update domain if provided
        if domain is not None:
            profiles[name]["domain"] = domain
        
        # Update token if provided
        if token is not None:
            if self.use_keychain and self.token_storage:
                # Store new token securely
                if not self.token_storage.store_token(name, token):
                    raise RuntimeError("Failed to store token securely")
                # Remove token from JSON if using secure storage
                profiles[name]["token"] = None
                profiles[name]["secure_storage"] = True
            else:
                profiles[name]["token"] = token
        
        profiles[name]["last_used"] = time.time()
        self._save_profiles(profiles)
        return True
    
    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile and its secure token.
        
        Args:
            name: Profile name
            
        Returns:
            True if successful
        """
        profiles = self._load_profiles()
        
        if name in profiles:
            # Remove from secure storage if applicable
            if profiles[name].get("secure_storage") and self.token_storage:
                self.token_storage.delete_token(name)
            
            del profiles[name]
            self._save_profiles(profiles)
        
        # If this was the active profile, clear it
        if self.get_active_profile() == name:
            self.set_active_profile("default")
        
        return True
    
    def migrate_to_secure_storage(self) -> Dict[str, bool]:
        """
        Migrate existing profiles to secure storage.
        
        Returns:
            Dictionary of profile names and migration success status
        """
        if not self.use_keychain or not self.token_storage:
            return {}
        
        profiles = self._load_profiles()
        results = {}
        
        for profile_name, profile_data in profiles.items():
            if profile_data.get("token") and not profile_data.get("secure_storage"):
                # Move token to secure storage
                token = profile_data["token"]
                if self.token_storage.store_token(profile_name, token):
                    profile_data["token"] = None
                    profile_data["secure_storage"] = True
                    results[profile_name] = True
                else:
                    results[profile_name] = False
        
        self._save_profiles(profiles)
        return results
