import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from click.testing import CliRunner
from okta_cli.main import configure
from okta_cli.users import list_users
from okta_cli.enhanced_config import (
    ProfileManager,
    ConfigValidator,
    EnvironmentConfig,
    get_active_profile,
    set_active_profile,
    list_profiles,
    delete_profile,
    validate_profile,
    health_check,
)


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


# Multiple Profile Management Tests
def test_profile_manager_initialization(temp_config_dir):
    """Test ProfileManager initialization."""
    manager = ProfileManager(temp_config_dir)
    assert manager.config_dir == temp_config_dir
    assert os.path.exists(manager.config_file)
    assert os.path.exists(manager.profiles_file)


def test_profile_manager_create_profile(temp_config_dir):
    """Test creating a new profile."""
    manager = ProfileManager(temp_config_dir)

    result = manager.create_profile("dev", "dev.okta.com", "dev-token")
    assert result is True

    profiles = manager.list_profiles()
    assert "dev" in profiles
    assert profiles["dev"]["domain"] == "dev.okta.com"
    assert profiles["dev"]["token"] == "dev-token"


def test_profile_manager_create_duplicate_profile(temp_config_dir):
    """Test creating a profile that already exists."""
    manager = ProfileManager(temp_config_dir)

    manager.create_profile("dev", "dev.okta.com", "dev-token")

    with pytest.raises(ValueError, match="Profile 'dev' already exists"):
        manager.create_profile("dev", "dev2.okta.com", "dev2-token")


def test_profile_manager_get_profile(temp_config_dir):
    """Test retrieving a profile."""
    manager = ProfileManager(temp_config_dir)

    manager.create_profile("test", "test.okta.com", "test-token")

    profile = manager.get_profile("test")
    assert profile["domain"] == "test.okta.com"
    assert profile["token"] == "test-token"
    assert "created_at" in profile
    assert "last_used" in profile


def test_profile_manager_get_nonexistent_profile(temp_config_dir):
    """Test retrieving a non-existent profile."""
    manager = ProfileManager(temp_config_dir)

    with pytest.raises(ValueError, match="Profile 'nonexistent' not found"):
        manager.get_profile("nonexistent")


def test_profile_manager_update_profile(temp_config_dir):
    """Test updating an existing profile."""
    manager = ProfileManager(temp_config_dir)

    manager.create_profile("dev", "dev.okta.com", "dev-token")

    result = manager.update_profile("dev", domain="dev2.okta.com", token="new-token")
    assert result is True

    profile = manager.get_profile("dev")
    assert profile["domain"] == "dev2.okta.com"
    assert profile["token"] == "new-token"


def test_profile_manager_delete_profile(temp_config_dir):
    """Test deleting a profile."""
    manager = ProfileManager(temp_config_dir)

    manager.create_profile("temp", "temp.okta.com", "temp-token")

    result = manager.delete_profile("temp")
    assert result is True

    profiles = manager.list_profiles()
    assert "temp" not in profiles


def test_profile_manager_set_active_profile(temp_config_dir):
    """Test setting active profile."""
    manager = ProfileManager(temp_config_dir)

    manager.create_profile("dev", "dev.okta.com", "dev-token")
    manager.create_profile("prod", "prod.okta.com", "prod-token")

    result = manager.set_active_profile("dev")
    assert result is True

    active = manager.get_active_profile()
    assert active == "dev"


def test_profile_manager_get_active_profile_default(temp_config_dir):
    """Test getting active profile when none is set."""
    manager = ProfileManager(temp_config_dir)

    # Should return "default" when no active profile is set
    active = manager.get_active_profile()
    assert active == "default"


def test_profile_manager_list_profiles_empty(temp_config_dir):
    """Test listing profiles when none exist."""
    manager = ProfileManager(temp_config_dir)

    profiles = manager.list_profiles()
    assert profiles == {}


def test_profile_manager_list_profiles_with_data(temp_config_dir):
    """Test listing profiles with existing data."""
    manager = ProfileManager(temp_config_dir)

    manager.create_profile("dev", "dev.okta.com", "dev-token")
    manager.create_profile("prod", "prod.okta.com", "prod-token")

    profiles = manager.list_profiles()
    assert len(profiles) == 2
    assert "dev" in profiles
    assert "prod" in profiles


# Environment Variable Configuration Tests
def test_environment_config_initialization():
    """Test EnvironmentConfig initialization."""
    env_config = EnvironmentConfig()
    assert env_config.prefix == "OKTA_"


def test_environment_config_get_domain():
    """Test getting domain from environment variable."""
    with patch.dict(os.environ, {"OKTA_DOMAIN": "env.okta.com"}):
        env_config = EnvironmentConfig()
        assert env_config.get_domain() == "env.okta.com"


def test_environment_config_get_token():
    """Test getting token from environment variable."""
    with patch.dict(os.environ, {"OKTA_TOKEN": "env-token"}):
        env_config = EnvironmentConfig()
        assert env_config.get_token() == "env-token"


def test_environment_config_get_profile():
    """Test getting profile from environment variable."""
    with patch.dict(os.environ, {"OKTA_PROFILE": "env-profile"}):
        env_config = EnvironmentConfig()
        assert env_config.get_profile() == "env-profile"


def test_environment_config_get_missing_values():
    """Test getting missing environment variables."""
    with patch.dict(os.environ, {}, clear=True):
        env_config = EnvironmentConfig()
        assert env_config.get_domain() is None
        assert env_config.get_token() is None
        assert env_config.get_profile() is None


def test_environment_config_has_complete_config():
    """Test checking if environment has complete configuration."""
    with patch.dict(
        os.environ, {"OKTA_DOMAIN": "env.okta.com", "OKTA_TOKEN": "env-token"}
    ):
        env_config = EnvironmentConfig()
        assert env_config.has_complete_config() is True


def test_environment_config_incomplete_config():
    """Test checking incomplete environment configuration."""
    with patch.dict(os.environ, {"OKTA_DOMAIN": "env.okta.com"}):
        env_config = EnvironmentConfig()
        assert env_config.has_complete_config() is False


def test_environment_config_profile_specific():
    """Test getting profile-specific environment variables."""
    with patch.dict(
        os.environ, {"OKTA_DEV_DOMAIN": "dev.okta.com", "OKTA_DEV_TOKEN": "dev-token"}
    ):
        env_config = EnvironmentConfig()
        assert env_config.get_domain("dev") == "dev.okta.com"
        assert env_config.get_token("dev") == "dev-token"


# Configuration Validation Tests
def test_config_validator_initialization():
    """Test ConfigValidator initialization."""
    validator = ConfigValidator()
    assert validator is not None


def test_config_validator_validate_domain():
    """Test domain validation."""
    validator = ConfigValidator()

    # Valid domains
    assert validator.validate_domain("test.okta.com") is True
    assert validator.validate_domain("dev.oktapreview.com") is True

    # Invalid domains
    assert validator.validate_domain("invalid.domain.com") is False
    assert validator.validate_domain("") is False
    assert validator.validate_domain(None) is False


def test_config_validator_validate_token():
    """Test token validation."""
    validator = ConfigValidator()

    # Valid tokens
    assert validator.validate_token("a" * 30) is True
    assert validator.validate_token("valid-token-123456789012345") is True

    # Invalid tokens
    assert validator.validate_token("short") is False
    assert validator.validate_token("") is False
    assert validator.validate_token(None) is False


def test_config_validator_validate_profile():
    """Test profile validation."""
    validator = ConfigValidator()

    # Valid profiles
    assert validator.validate_profile("dev") is True
    assert validator.validate_profile("production") is True
    assert validator.validate_profile("test-123") is True

    # Invalid profiles
    assert validator.validate_profile("") is False
    assert validator.validate_profile(None) is False
    assert validator.validate_profile("invalid profile") is False  # spaces not allowed


@patch("requests.get")
def test_config_validator_validate_connectivity(mock_get):
    """Test connectivity validation."""
    validator = ConfigValidator()

    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "test-user"}
    mock_get.return_value = mock_response

    result = validator.validate_connectivity("test.okta.com", "valid-token")
    assert result is True


@patch("requests.get")
def test_config_validator_validate_connectivity_failure(mock_get):
    """Test connectivity validation failure."""
    validator = ConfigValidator()

    # Mock failed response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    result = validator.validate_connectivity("test.okta.com", "invalid-token")
    assert result is False


def test_config_validator_validate_complete_config():
    """Test complete configuration validation."""
    validator = ConfigValidator()

    config_data = {
        "domain": "test.okta.com",
        "token": "valid-token-123456789012345",
        "profile": "test",
    }

    result = validator.validate_config(config_data)
    assert result is True


def test_config_validator_validate_incomplete_config():
    """Test incomplete configuration validation."""
    validator = ConfigValidator()

    config_data = {
        "domain": "test.okta.com"
        # Missing token
    }

    result = validator.validate_config(config_data)
    assert result is False


# CLI Integration Tests
def test_configure_with_profile_option(temp_config_dir):
    """Test configure command with profile option."""
    runner = CliRunner()

    result = runner.invoke(
        configure,
        ["--profile", "dev"],
        input="dev.okta.com\ndev-token-that-is-long-enough\n",
    )

    assert result.exit_code == 0
    assert "Configuration saved for profile 'dev'" in result.output


def test_list_users_with_profile_option(temp_config_dir):
    """Test list users command with profile option."""
    runner = CliRunner()

    # First configure a profile using ProfileManager
    with runner.isolated_filesystem():
        manager = ProfileManager(temp_config_dir)
        manager.create_profile("dev", "dev.okta.com", "dev-token")
        
        with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
            def create_manager(*args, **kwargs):
                return manager
            mock_profile_class.side_effect = create_manager
            
            with patch("requests.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = [
                    {"profile": {"login": "dev-user@test.com"}}
                ]
                mock_get.return_value = mock_response

                result = runner.invoke(list_users, ["--profile", "dev"])

                assert result.exit_code == 0
                assert "dev-user@test.com" in result.output


def test_environment_variable_precedence(temp_config_dir):
    """Test that environment variables take precedence over config file."""
    runner = CliRunner()

    with patch.dict(
        os.environ, {"OKTA_DOMAIN": "env.okta.com", "OKTA_TOKEN": "env-token"}
    ):
        with runner.isolated_filesystem():
            # Create config file with different values using ProfileManager
            manager = ProfileManager(temp_config_dir)
            manager.create_profile("default", "file.okta.com", "file-token")
            
            with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
                def create_manager(*args, **kwargs):
                    return manager
                mock_profile_class.side_effect = create_manager
                
                with patch("requests.get") as mock_get:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = [
                        {"profile": {"login": "env-user@test.com"}}
                    ]
                    mock_get.return_value = mock_response

                    result = runner.invoke(list_users)

                    # Should use environment values
                    mock_get.assert_called_with(
                        "https://env.okta.com/api/v1/users",
                        headers={
                            "Authorization": "SSWS env-token",
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                        },
                        timeout=30,
                    )


def test_profile_specific_environment_variables(temp_config_dir):
    """Test profile-specific environment variables."""
    runner = CliRunner()

    with patch.dict(
        os.environ,
        {"OKTA_DEV_DOMAIN": "dev-env.okta.com", "OKTA_DEV_TOKEN": "dev-env-token"},
    ):
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"profile": {"login": "dev-env-user@test.com"}}
            ]
            mock_get.return_value = mock_response

            result = runner.invoke(list_users, ["--profile", "dev"])

            # Should use profile-specific environment values
            mock_get.assert_called_with(
                "https://dev-env.okta.com/api/v1/users",
                headers={
                    "Authorization": "SSWS dev-env-token",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )


# Health Check Tests
@patch("requests.get")
def test_health_check_success(mock_get):
    """Test successful health check."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test-user",
        "profile": {"login": "test@example.com"},
    }
    mock_get.return_value = mock_response

    result = health_check("test.okta.com", "valid-token")

    assert result["status"] == "healthy"
    assert result["connectivity"] is True
    assert result["authentication"] is True
    assert "response_time" in result


@patch("requests.get")
def test_health_check_authentication_failure(mock_get):
    """Test health check with authentication failure."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    result = health_check("test.okta.com", "invalid-token")

    assert result["status"] == "unhealthy"
    assert result["connectivity"] is True
    assert result["authentication"] is False


@patch("requests.get")
def test_health_check_connectivity_failure(mock_get):
    """Test health check with connectivity failure."""
    mock_get.side_effect = Exception("Connection failed")

    result = health_check("test.okta.com", "valid-token")

    assert result["status"] == "unhealthy"
    assert result["connectivity"] is False
    assert result["authentication"] is False


# Configuration Migration Tests
def test_migrate_legacy_config(temp_config_dir):
    """Test migrating legacy configuration format."""
    manager = ProfileManager(temp_config_dir)

    # Create legacy config format
    legacy_config = {"domain": "legacy.okta.com", "token": "legacy-token"}

    with open(os.path.join(temp_config_dir, "legacy_config"), "w") as f:
        json.dump(legacy_config, f)

    result = manager.migrate_legacy_config(
        os.path.join(temp_config_dir, "legacy_config")
    )
    assert result is True

    # Should create default profile
    profile = manager.get_profile("default")
    assert profile["domain"] == "legacy.okta.com"
    assert profile["token"] == "legacy-token"


# Configuration Backup and Restore Tests
def test_config_backup_and_restore(temp_config_dir):
    """Test configuration backup and restore."""
    manager = ProfileManager(temp_config_dir)

    # Create test profiles
    manager.create_profile("dev", "dev.okta.com", "dev-token")
    manager.create_profile("prod", "prod.okta.com", "prod-token")

    # Create backup
    backup_path = manager.create_backup()
    assert os.path.exists(backup_path)

    # Clear current config
    manager.clear_all_profiles()
    assert len(manager.list_profiles()) == 0

    # Restore from backup
    result = manager.restore_from_backup(backup_path)
    assert result is True

    # Verify restoration
    profiles = manager.list_profiles()
    assert len(profiles) == 2
    assert "dev" in profiles
    assert "prod" in profiles


def test_config_export_import(temp_config_dir):
    """Test configuration export and import."""
    manager = ProfileManager(temp_config_dir)

    # Create test profiles
    manager.create_profile("test", "test.okta.com", "test-token")

    # Export configuration
    export_path = os.path.join(temp_config_dir, "export.json")
    result = manager.export_config(export_path)
    assert result is True
    assert os.path.exists(export_path)

    # Clear current config
    manager.clear_all_profiles()

    # Import configuration
    result = manager.import_config(export_path)
    assert result is True

    # Verify import
    profile = manager.get_profile("test")
    assert profile["domain"] == "test.okta.com"
    assert profile["token"] == "test-token"
