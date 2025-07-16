import pytest
import requests
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from okta_cli.users import list_users, create_user, show_user
from okta_cli.groups import list_groups, create_group
from okta_cli.main import configure
from okta_cli import config


@pytest.fixture
def mock_config(tmp_path):
    config_path = tmp_path / "config"
    with patch.object(config, "CONFIG_FILE", str(config_path)):
        cfg = config.get_config()
        cfg.add_section("default")
        cfg.set("default", "domain", "test.okta.com")
        cfg.set("default", "token", "test-token")
        config.write_config(cfg)
        yield


# API Error Response Tests
@patch("requests.get")
def test_list_users_unauthorized_error(mock_get, mock_config):
    """Test handling of 401 Unauthorized error"""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "errorCode": "E0000011",
        "errorSummary": "Invalid token provided",
        "errorId": "oaeUYzFLWz8vVpKKNEPJOyZqA",
    }
    mock_response.text = (
        '{"errorCode": "E0000011", "errorSummary": "Invalid token provided"}'
    )
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Authentication failed" in result.output
    assert "Invalid token provided" in result.output


@patch("requests.get")
def test_list_users_forbidden_error(mock_get, mock_config):
    """Test handling of 403 Forbidden error"""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.json.return_value = {
        "errorCode": "E0000006",
        "errorSummary": "You do not have permission to access this resource",
        "errorId": "oaeUYzFLWz8vVpKKNEPJOyZqB",
    }
    mock_response.text = '{"errorCode": "E0000006", "errorSummary": "You do not have permission to access this resource"}'
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Permission denied" in result.output
    assert "You do not have permission to access this resource" in result.output


@patch("requests.get")
def test_list_users_not_found_error(mock_get, mock_config):
    """Test handling of 404 Not Found error"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "errorCode": "E0000007",
        "errorSummary": "Not found: Resource not found",
        "errorId": "oaeUYzFLWz8vVpKKNEPJOyZqC",
    }
    mock_response.text = (
        '{"errorCode": "E0000007", "errorSummary": "Not found: Resource not found"}'
    )
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Resource not found" in result.output
    assert "Not found: Resource not found" in result.output


@patch("requests.get")
def test_list_users_rate_limit_error(mock_get, mock_config):
    """Test handling of 429 Rate Limit error"""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "errorCode": "E0000047",
        "errorSummary": "API call exceeded rate limit",
        "errorId": "oaeUYzFLWz8vVpKKNEPJOyZqD",
    }
    mock_response.text = (
        '{"errorCode": "E0000047", "errorSummary": "API call exceeded rate limit"}'
    )
    mock_response.headers = {"X-Rate-Limit-Reset": "1609459200"}
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Rate limit exceeded" in result.output
    assert "API call exceeded rate limit" in result.output


@patch("requests.get")
def test_list_users_server_error(mock_get, mock_config):
    """Test handling of 500 Server Error"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "errorCode": "E0000009",
        "errorSummary": "Internal Server Error",
        "errorId": "oaeUYzFLWz8vVpKKNEPJOyZqE",
    }
    mock_response.text = (
        '{"errorCode": "E0000009", "errorSummary": "Internal Server Error"}'
    )
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Server error" in result.output
    assert "Internal Server Error" in result.output


@patch("requests.get")
def test_list_users_invalid_json_response(mock_get, mock_config):
    """Test handling of invalid JSON response"""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.text = "Invalid JSON response"
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Invalid response format" in result.output
    assert "Invalid JSON response" in result.output


# Network Timeout Tests
@patch("requests.get")
def test_list_users_connection_timeout(mock_get, mock_config):
    """Test handling of connection timeout"""
    mock_get.side_effect = requests.exceptions.ConnectTimeout("Connection timed out")

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Connection timeout" in result.output
    assert "Unable to connect to Okta" in result.output


@patch("requests.get")
def test_list_users_read_timeout(mock_get, mock_config):
    """Test handling of read timeout"""
    mock_get.side_effect = requests.exceptions.ReadTimeout("Read operation timed out")

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Request timeout" in result.output
    assert "The request took too long to complete" in result.output


@patch("requests.get")
def test_list_users_connection_error(mock_get, mock_config):
    """Test handling of connection error"""
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Connection failed" in result.output
    assert "Unable to connect to Okta" in result.output


# Input Validation Tests
def test_create_user_invalid_email():
    """Test validation of invalid email format"""
    runner = CliRunner()
    result = runner.invoke(
        create_user,
        [
            "--first-name",
            "Test",
            "--last-name",
            "User",
            "--email",
            "invalid-email",
            "--login",
            "testuser",
        ],
    )

    assert result.exit_code == 1
    assert "Invalid email format" in result.output


def test_create_user_invalid_login():
    """Test validation of invalid login format"""
    runner = CliRunner()
    result = runner.invoke(
        create_user,
        [
            "--first-name",
            "Test",
            "--last-name",
            "User",
            "--email",
            "test@example.com",
            "--login",
            "",
        ],
    )

    assert result.exit_code == 1
    assert "Login cannot be empty" in result.output


def test_create_user_invalid_name():
    """Test validation of invalid name format"""
    runner = CliRunner()
    result = runner.invoke(
        create_user,
        [
            "--first-name",
            "",
            "--last-name",
            "User",
            "--email",
            "test@example.com",
            "--login",
            "testuser",
        ],
    )

    assert result.exit_code == 1
    assert "First name cannot be empty" in result.output


def test_configure_invalid_domain():
    """Test validation of invalid Okta domain"""
    runner = CliRunner()
    result = runner.invoke(configure, input="invalid-domain\nmy-api-token\n")

    assert result.exit_code == 1
    assert "Invalid Okta domain format" in result.output


def test_configure_empty_token():
    """Test validation of empty API token"""
    runner = CliRunner()
    result = runner.invoke(configure, input="test.okta.com\n\n")

    assert result.exit_code == 1
    assert "API token cannot be empty" in result.output


# Configuration Error Tests
def test_missing_profile_configuration():
    """Test handling of missing profile configuration"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Don't create any config file
        result = runner.invoke(list_users, ["--profile", "nonexistent"])

    assert result.exit_code == 1
    assert "Profile 'nonexistent' not found" in result.output
    assert "okta-cli configure --profile nonexistent" in result.output


def test_corrupted_config_file(tmp_path):
    """Test handling of corrupted configuration file"""
    config_path = tmp_path / "config"
    config_path.write_text("invalid config content")

    with patch.object(config, "CONFIG_FILE", str(config_path)):
        runner = CliRunner()
        result = runner.invoke(list_users)

    assert result.exit_code == 1
    assert "Configuration file is corrupted" in result.output
