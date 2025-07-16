"""
Enhanced configuration management for the Okta CLI tool.
"""

import os
import json
import time
import re
import shutil
from typing import Dict, List, Optional, Any, Tuple
import requests
from .errors import ConfigurationError, ValidationError


class ProfileManager:
    """
    Enhanced profile management with support for multiple profiles,
    environment variables, and configuration validation.
    """

    def __init__(self, config_dir: str = None):
        """
        Initialize profile manager.

        Args:
            config_dir: Directory to store configuration files
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.okta")

        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "profiles.json")
        self.profiles_file = os.path.join(config_dir, "profiles.json")
        self.active_profile_file = os.path.join(config_dir, "active_profile")

        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        os.chmod(config_dir, 0o700)

        # Initialize profiles file if it doesn't exist
        if not os.path.exists(self.profiles_file):
            self._save_profiles({})

    def _load_profiles(self) -> Dict[str, Any]:
        """Load profiles from file."""
        try:
            with open(self.profiles_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_profiles(self, profiles: Dict[str, Any]) -> None:
        """Save profiles to file."""
        with open(self.profiles_file, "w") as f:
            json.dump(profiles, f, indent=2)
        os.chmod(self.profiles_file, 0o600)

    def create_profile(self, name: str, domain: str, token: str) -> bool:
        """
        Create a new profile.

        Args:
            name: Profile name
            domain: Okta domain
            token: API token

        Returns:
            True if successful

        Raises:
            ValueError: If profile already exists
        """
        profiles = self._load_profiles()

        if name in profiles:
            raise ValueError(f"Profile '{name}' already exists")

        profiles[name] = {
            "domain": domain,
            "token": token,
            "created_at": time.time(),
            "last_used": time.time(),
        }

        self._save_profiles(profiles)
        return True

    def get_profile(self, name: str) -> Dict[str, Any]:
        """
        Get a profile by name.

        Args:
            name: Profile name

        Returns:
            Profile data

        Raises:
            ValueError: If profile not found
        """
        profiles = self._load_profiles()

        if name not in profiles:
            raise ValueError(f"Profile '{name}' not found")

        # Update last used time
        profiles[name]["last_used"] = time.time()
        self._save_profiles(profiles)

        return profiles[name]

    def update_profile(self, name: str, domain: str = None, token: str = None) -> bool:
        """
        Update an existing profile.

        Args:
            name: Profile name
            domain: New domain (optional)
            token: New token (optional)

        Returns:
            True if successful

        Raises:
            ValueError: If profile not found
        """
        profiles = self._load_profiles()

        if name not in profiles:
            raise ValueError(f"Profile '{name}' not found")

        if domain is not None:
            profiles[name]["domain"] = domain
        if token is not None:
            profiles[name]["token"] = token

        profiles[name]["last_used"] = time.time()
        self._save_profiles(profiles)
        return True

    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile.

        Args:
            name: Profile name

        Returns:
            True if successful
        """
        profiles = self._load_profiles()

        if name in profiles:
            del profiles[name]
            self._save_profiles(profiles)

        # If this was the active profile, clear it
        if self.get_active_profile() == name:
            self.set_active_profile("default")

        return True

    def list_profiles(self) -> Dict[str, Any]:
        """
        List all profiles.

        Returns:
            Dictionary of profiles
        """
        return self._load_profiles()

    def set_active_profile(self, name: str) -> bool:
        """
        Set the active profile.

        Args:
            name: Profile name

        Returns:
            True if successful
        """
        with open(self.active_profile_file, "w") as f:
            f.write(name)
        os.chmod(self.active_profile_file, 0o600)
        return True

    def get_active_profile(self) -> str:
        """
        Get the active profile name.

        Returns:
            Active profile name (defaults to "default")
        """
        try:
            with open(self.active_profile_file, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "default"

    def clear_all_profiles(self) -> bool:
        """
        Clear all profiles (for testing/migration).

        Returns:
            True if successful
        """
        self._save_profiles({})
        return True

    def migrate_legacy_config(self, legacy_path: str) -> bool:
        """
        Migrate legacy configuration format.

        Args:
            legacy_path: Path to legacy config file

        Returns:
            True if successful
        """
        try:
            with open(legacy_path, "r") as f:
                legacy_config = json.load(f)

            # Create default profile from legacy config
            if "domain" in legacy_config and "token" in legacy_config:
                self.create_profile(
                    "default", legacy_config["domain"], legacy_config["token"]
                )
                return True
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            pass

        return False

    def create_backup(self) -> str:
        """
        Create a backup of the current configuration.

        Returns:
            Path to backup file
        """
        timestamp = int(time.time())
        backup_path = os.path.join(self.config_dir, f"profiles_backup_{timestamp}.json")

        if os.path.exists(self.profiles_file):
            shutil.copy2(self.profiles_file, backup_path)
            os.chmod(backup_path, 0o600)

        return backup_path

    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore configuration from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            True if successful
        """
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, self.profiles_file)
            os.chmod(self.profiles_file, 0o600)
            return True
        return False

    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to file.

        Args:
            export_path: Path to export file

        Returns:
            True if successful
        """
        profiles = self._load_profiles()

        with open(export_path, "w") as f:
            json.dump(profiles, f, indent=2)

        return True

    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from file.

        Args:
            import_path: Path to import file

        Returns:
            True if successful
        """
        try:
            with open(import_path, "r") as f:
                profiles = json.load(f)

            self._save_profiles(profiles)
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False


class EnvironmentConfig:
    """
    Environment variable configuration support.
    """

    def __init__(self, prefix: str = "OKTA_"):
        """
        Initialize environment configuration.

        Args:
            prefix: Environment variable prefix
        """
        self.prefix = prefix

    def get_domain(self, profile: str = None) -> Optional[str]:
        """
        Get domain from environment variable.

        Args:
            profile: Profile name for profile-specific variables

        Returns:
            Domain from environment or None
        """
        if profile:
            var_name = f"{self.prefix}{profile.upper()}_DOMAIN"
            return os.getenv(var_name)

        return os.getenv(f"{self.prefix}DOMAIN")

    def get_token(self, profile: str = None) -> Optional[str]:
        """
        Get token from environment variable.

        Args:
            profile: Profile name for profile-specific variables

        Returns:
            Token from environment or None
        """
        if profile:
            var_name = f"{self.prefix}{profile.upper()}_TOKEN"
            return os.getenv(var_name)

        return os.getenv(f"{self.prefix}TOKEN")

    def get_profile(self) -> Optional[str]:
        """
        Get profile name from environment variable.

        Returns:
            Profile name from environment or None
        """
        return os.getenv(f"{self.prefix}PROFILE")

    def has_complete_config(self, profile: str = None) -> bool:
        """
        Check if environment has complete configuration.

        Args:
            profile: Profile name for profile-specific variables

        Returns:
            True if both domain and token are available
        """
        domain = self.get_domain(profile)
        token = self.get_token(profile)

        return domain is not None and token is not None


class ConfigValidator:
    """
    Configuration validation utilities.
    """

    def __init__(self):
        """Initialize configuration validator."""
        self.domain_pattern = re.compile(r"^[a-zA-Z0-9-]+\.(okta|oktapreview)\.com$")
        self.profile_pattern = re.compile(r"^[a-zA-Z0-9_-]+$")

    def validate_domain(self, domain: str) -> bool:
        """
        Validate Okta domain format.

        Args:
            domain: Domain to validate

        Returns:
            True if valid
        """
        if not domain:
            return False

        return bool(self.domain_pattern.match(domain))

    def validate_token(self, token: str) -> bool:
        """
        Validate API token format.

        Args:
            token: Token to validate

        Returns:
            True if valid
        """
        if not token:
            return False

        # Basic token validation (length check)
        return len(token) >= 20

    def validate_profile(self, profile: str) -> bool:
        """
        Validate profile name format.

        Args:
            profile: Profile name to validate

        Returns:
            True if valid
        """
        if not profile:
            return False

        return bool(self.profile_pattern.match(profile))

    def validate_connectivity(self, domain: str, token: str) -> bool:
        """
        Validate connectivity to Okta API.

        Args:
            domain: Okta domain
            token: API token

        Returns:
            True if connectivity is successful
        """
        try:
            headers = {
                "Authorization": f"SSWS {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            response = requests.get(
                f"https://{domain}/api/v1/users/me", headers=headers, timeout=10
            )

            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate complete configuration.

        Args:
            config: Configuration dictionary

        Returns:
            True if configuration is valid
        """
        required_fields = ["domain", "token"]

        for field in required_fields:
            if field not in config:
                return False

        if not self.validate_domain(config["domain"]):
            return False

        if not self.validate_token(config["token"]):
            return False

        if "profile" in config and not self.validate_profile(config["profile"]):
            return False

        return True


def get_effective_config(profile: str = None) -> Tuple[str, str]:
    """
    Get effective configuration considering environment variables and profiles.

    Args:
        profile: Profile name

    Returns:
        Tuple of (domain, token)

    Raises:
        ConfigurationError: If configuration is not found or invalid
    """
    env_config = EnvironmentConfig()

    # Check environment variables first (highest priority)
    env_domain = env_config.get_domain(profile)
    env_token = env_config.get_token(profile)

    if env_domain and env_token:
        return env_domain, env_token

    # Fall back to profile configuration
    profile_manager = ProfileManager()

    if profile is None:
        profile = env_config.get_profile() or profile_manager.get_active_profile()

    try:
        profile_data = profile_manager.get_profile(profile)
        domain = env_domain or profile_data["domain"]
        token = env_token or profile_data["token"]

        return domain, token
    except ValueError:
        raise ConfigurationError(
            f"Profile '{profile}' not found and no environment configuration available"
        )


def health_check(domain: str, token: str) -> Dict[str, Any]:
    """
    Perform health check on configuration.

    Args:
        domain: Okta domain
        token: API token

    Returns:
        Health check results
    """
    result = {
        "status": "unknown",
        "connectivity": False,
        "authentication": False,
        "response_time": None,
        "errors": [],
    }

    try:
        start_time = time.time()

        headers = {
            "Authorization": f"SSWS {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"https://{domain}/api/v1/users/me", headers=headers, timeout=10
        )

        end_time = time.time()
        result["response_time"] = end_time - start_time
        result["connectivity"] = True

        if response.status_code == 200:
            result["authentication"] = True
            result["status"] = "healthy"
        else:
            result["authentication"] = False
            result["status"] = "unhealthy"
            result["errors"].append(
                f"Authentication failed: HTTP {response.status_code}"
            )

    except Exception as e:
        result["connectivity"] = False
        result["authentication"] = False
        result["status"] = "unhealthy"
        result["errors"].append(f"Connectivity failed: {e}")

    return result


# CLI Helper Functions
def get_active_profile() -> str:
    """Get the active profile name."""
    manager = ProfileManager()
    return manager.get_active_profile()


def set_active_profile(name: str) -> bool:
    """Set the active profile."""
    manager = ProfileManager()
    return manager.set_active_profile(name)


def list_profiles() -> Dict[str, Any]:
    """List all profiles."""
    manager = ProfileManager()
    return manager.list_profiles()


def delete_profile(name: str) -> bool:
    """Delete a profile."""
    manager = ProfileManager()
    return manager.delete_profile(name)


def validate_profile(name: str) -> Dict[str, Any]:
    """Validate a profile configuration."""
    try:
        manager = ProfileManager()
        profile_data = manager.get_profile(name)

        validator = ConfigValidator()
        is_valid = validator.validate_config(profile_data)

        result = {"profile": name, "valid": is_valid, "issues": []}

        if not validator.validate_domain(profile_data["domain"]):
            result["issues"].append("Invalid domain format")

        if not validator.validate_token(profile_data["token"]):
            result["issues"].append("Invalid token format")

        # Test connectivity
        if is_valid:
            connectivity_result = validator.validate_connectivity(
                profile_data["domain"], profile_data["token"]
            )

            if not connectivity_result:
                result["issues"].append("Cannot connect to Okta API")
                result["valid"] = False

        return result

    except ValueError as e:
        return {"profile": name, "valid": False, "issues": [str(e)]}
