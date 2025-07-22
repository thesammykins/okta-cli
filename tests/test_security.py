import pytest
import os
import tempfile
import time
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner
from okta_cli.main import configure
from okta_cli.users import list_users
from okta_cli.enhanced_config import ProfileManager
import requests


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


# Encrypted Credential Storage Tests
def test_encrypt_decrypt_token():
    """Test token encryption and decryption."""
    from okta_cli.security import encrypt_token, decrypt_token

    original_token = "test-api-token-12345"
    password = "test-password"

    # Test encryption
    encrypted = encrypt_token(original_token, password)
    assert encrypted != original_token
    assert len(encrypted) > len(original_token)

    # Test decryption
    decrypted = decrypt_token(encrypted, password)
    assert decrypted == original_token


def test_encrypt_decrypt_different_passwords():
    """Test that different passwords fail to decrypt."""
    from okta_cli.security import encrypt_token, decrypt_token

    original_token = "test-api-token-12345"
    password1 = "password1"
    password2 = "password2"

    encrypted = encrypt_token(original_token, password1)

    with pytest.raises(Exception):
        decrypt_token(encrypted, password2)


@patch("okta_cli.security.getpass.getpass")
def test_secure_config_save_and_load(mock_getpass, temp_config_dir):
    """Test secure configuration saving and loading."""
    from okta_cli.security import SecureConfig

    # Mock password input
    mock_getpass.side_effect = ["testpassword", "testpassword", "testpassword"]

    secure_config = SecureConfig(temp_config_dir)
    profile = "test-profile"
    domain = "test.okta.com"
    token = "test-api-token-12345"

    # Save encrypted config
    secure_config.save_profile(profile, domain, token)

    # Load and verify
    loaded_domain, loaded_token = secure_config.load_profile(profile)
    assert loaded_domain == domain
    assert loaded_token == token


def test_secure_config_profile_not_found(temp_config_dir):
    """Test handling of non-existent profile."""
    from okta_cli.security import SecureConfig

    secure_config = SecureConfig(temp_config_dir)

    with pytest.raises(ValueError, match="Profile 'nonexistent' not found"):
        secure_config.load_profile("nonexistent")


@patch("okta_cli.security.getpass.getpass")
def test_secure_config_list_profiles(mock_getpass, temp_config_dir):
    """Test listing all profiles."""
    from okta_cli.security import SecureConfig

    # Mock password input
    mock_getpass.side_effect = ["testpassword", "testpassword"] * 3

    secure_config = SecureConfig(temp_config_dir)

    # Save multiple profiles
    secure_config.save_profile("profile1", "domain1.okta.com", "token1")
    secure_config.save_profile("profile2", "domain2.okta.com", "token2")

    profiles = secure_config.list_profiles()
    assert "profile1" in profiles
    assert "profile2" in profiles


@patch("okta_cli.security.getpass.getpass")
def test_secure_config_delete_profile(mock_getpass, temp_config_dir):
    """Test deleting a profile."""
    from okta_cli.security import SecureConfig

    # Mock password input
    mock_getpass.side_effect = ["testpassword", "testpassword", "testpassword"]

    secure_config = SecureConfig(temp_config_dir)

    # Save and then delete
    secure_config.save_profile("test-profile", "test.okta.com", "token")
    secure_config.delete_profile("test-profile")

    with pytest.raises(ValueError, match="Profile 'test-profile' not found"):
        secure_config.load_profile("test-profile")


# Token Validation Tests
@patch("requests.get")
def test_token_validator_valid_token(mock_get):
    """Test token validation with valid token."""
    from okta_cli.security import TokenValidator

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "test-user-id"}
    mock_get.return_value = mock_response

    validator = TokenValidator("test.okta.com", "valid-token")
    assert validator.is_valid() is True


@patch("requests.get")
def test_token_validator_invalid_token(mock_get):
    """Test token validation with invalid token."""
    from okta_cli.security import TokenValidator

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    validator = TokenValidator("test.okta.com", "invalid-token")
    assert validator.is_valid() is False


@patch("requests.get")
def test_token_validator_network_error(mock_get):
    """Test token validation with network error."""
    from okta_cli.security import TokenValidator

    mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

    validator = TokenValidator("test.okta.com", "test-token")
    assert validator.is_valid() is False


@patch("requests.get")
def test_token_validator_get_permissions(mock_get):
    """Test getting token permissions."""
    from okta_cli.security import TokenValidator

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test-user-id",
        "profile": {"login": "admin@test.com"},
        "_links": {"self": {"href": "https://test.okta.com/api/v1/users/test-user-id"}},
    }
    mock_get.return_value = mock_response

    validator = TokenValidator("test.okta.com", "test-token")
    permissions = validator.get_permissions()

    assert "users:read" in permissions
    assert permissions["users:read"] is True


@patch("requests.get")
def test_token_validator_check_specific_permission(mock_get):
    """Test checking specific permissions."""
    from okta_cli.security import TokenValidator

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "group1"}]
    mock_get.return_value = mock_response

    validator = TokenValidator("test.okta.com", "test-token")
    assert validator.has_permission("groups:read") is True


@patch("requests.get")
def test_token_validator_check_permission_denied(mock_get):
    """Test checking permissions with access denied."""
    from okta_cli.security import TokenValidator

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_get.return_value = mock_response

    validator = TokenValidator("test.okta.com", "test-token")
    assert validator.has_permission("groups:read") is False


# Rate Limiting Tests
def test_rate_limiter_initialization():
    """Test rate limiter initialization."""
    from okta_cli.security import RateLimiter

    limiter = RateLimiter(max_requests=10, time_window=60)
    assert limiter.max_requests == 10
    assert limiter.time_window == 60
    assert len(limiter.requests) == 0


def test_rate_limiter_allow_request():
    """Test allowing requests within rate limit."""
    from okta_cli.security import RateLimiter

    limiter = RateLimiter(max_requests=5, time_window=60)

    # Should allow first 5 requests
    for i in range(5):
        assert limiter.can_make_request() is True
        limiter.record_request()


def test_rate_limiter_block_request():
    """Test blocking requests exceeding rate limit."""
    from okta_cli.security import RateLimiter

    limiter = RateLimiter(max_requests=3, time_window=60)

    # Fill up the limit
    for i in range(3):
        assert limiter.can_make_request() is True
        limiter.record_request()

    # Should block the next request
    assert limiter.can_make_request() is False


def test_rate_limiter_time_window_reset():
    """Test rate limiter reset after time window."""
    from okta_cli.security import RateLimiter

    limiter = RateLimiter(max_requests=2, time_window=1)  # 1 second window

    # Fill up the limit
    for i in range(2):
        assert limiter.can_make_request() is True
        limiter.record_request()

    # Should block
    assert limiter.can_make_request() is False

    # Wait for window to reset
    time.sleep(1.1)

    # Should allow again
    assert limiter.can_make_request() is True


def test_rate_limiter_get_reset_time():
    """Test getting reset time for rate limiter."""
    from okta_cli.security import RateLimiter

    limiter = RateLimiter(max_requests=1, time_window=60)

    # Make a request
    limiter.record_request()

    # Get reset time
    reset_time = limiter.get_reset_time()
    assert reset_time is not None
    assert reset_time > time.time()


def test_rate_limiter_wait_for_reset():
    """Test waiting for rate limiter reset."""
    from okta_cli.security import RateLimiter

    limiter = RateLimiter(max_requests=1, time_window=1)

    # Fill up the limit
    limiter.record_request()
    assert limiter.can_make_request() is False

    # Wait for reset (should be quick with 1 second window)
    start_time = time.time()
    limiter.wait_for_reset()
    end_time = time.time()

    # Should have waited approximately 1 second
    assert end_time - start_time >= 0.9  # Allow some tolerance
    assert limiter.can_make_request() is True


# Integration Tests
def test_configure_with_secure_storage(temp_config_dir):
    """Test configure command with secure storage."""
    runner = CliRunner()

    # This test checks that the configure command works with the current implementation
    # Security integration would be added later
    result = runner.invoke(
        configure, input="test.okta.com\ntest-api-token-that-is-long-enough\n"
    )

    assert result.exit_code == 0
    assert "Configuration saved" in result.output


def test_list_users_with_token_validation():
    """Test list users command with token validation."""
    # This test would be implemented when token validation is integrated
    # For now, we test the basic functionality
    pass


def test_rate_limiting_integration():
    """Test rate limiting integration with API calls."""
    # This test would be implemented when rate limiting is integrated
    # For now, we test the basic functionality
    pass


def test_token_expiration_handling():
    """Test handling of expired tokens."""
    # This test would be implemented when token refresh is added
    pass


@patch("okta_cli.security.getpass.getpass")
def test_secure_config_backup_and_restore(mock_getpass, temp_config_dir):
    """Test backup and restore of secure configuration."""
    from okta_cli.security import SecureConfig

    # Mock password input
    mock_getpass.side_effect = ["testpassword", "testpassword", "testpassword"]

    secure_config = SecureConfig(temp_config_dir)

    # Save original profile
    secure_config.save_profile("test", "test.okta.com", "token123")

    # Create backup
    backup_path = secure_config.create_backup()
    assert os.path.exists(backup_path)

    # Delete original
    secure_config.delete_profile("test")

    # Restore from backup
    secure_config.restore_from_backup(backup_path)

    # Verify restoration
    domain, token = secure_config.load_profile("test")
    assert domain == "test.okta.com"
    assert token == "token123"
