import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from okta_cli.users import (
    list_users,
    create_user,
    show_user,
    suspend_user,
    unsuspend_user,
    update_user,
    assign_app,
    unassign_app,
    list_app_assignments,
    deactivate_user,
    activate_user,
    reset_password,
)
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


@patch("requests.get")
def test_list_users(mock_get, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "1", "profile": {"login": "user1@example.com"}},
        {"id": "2", "profile": {"login": "user2@example.com"}},
    ]
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_users)

    assert result.exit_code == 0
    assert "user1@example.com" in result.output
    assert "user2@example.com" in result.output


@patch("requests.post")
def test_create_user(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "new-user-id",
        "profile": {"login": "newuser@example.com"},
    }
    mock_post.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(
        create_user,
        [
            "--first-name",
            "New",
            "--last-name",
            "User",
            "--email",
            "newuser@example.com",
            "--login",
            "newuser@example.com",
        ],
    )

    assert result.exit_code == 0
    assert "User created successfully" in result.output
    assert "newuser@example.com" in result.output


@patch("requests.get")
def test_show_user(mock_get, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "1",
        "profile": {
            "login": "user1@example.com",
            "firstName": "Test",
            "lastName": "User",
            "email": "user1@example.com",
        },
    }
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(show_user, ["1"])

    assert result.exit_code == 0
    assert "user1@example.com" in result.output
    assert "Test" in result.output
    assert "User" in result.output


@patch("requests.post")
def test_suspend_user(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(suspend_user, ["1"])

    assert result.exit_code == 0
    assert "User suspended successfully" in result.output


@patch("requests.post")
def test_unsuspend_user(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(unsuspend_user, ["1"])

    assert result.exit_code == 0
    assert "User unsuspended successfully" in result.output


@patch("requests.post")
def test_update_user(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "1",
        "profile": {
            "login": "updateduser@example.com",
            "firstName": "Updated",
            "lastName": "User",
            "email": "updateduser@example.com",
        },
    }
    mock_post.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(
        update_user,
        ["1", "--first-name", "Updated", "--email", "updateduser@example.com"],
    )

    assert result.exit_code == 0
    assert "User updated successfully" in result.output
    assert "updateduser@example.com" in result.output
    mock_post.assert_called_once()
    assert mock_post.call_args[1]["json"]["profile"]["firstName"] == "Updated"
    assert (
        mock_post.call_args[1]["json"]["profile"]["email"] == "updateduser@example.com"
    )


@patch("requests.post")
def test_assign_app(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "app-user-id",
        "scope": "USER_ASSIGNMENT",
        "status": "ACTIVE",
    }
    mock_post.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(
        assign_app, ["user123", "app456", "--profile-attributes", '{"role": "admin"}']
    )

    assert result.exit_code == 0
    assert "User assigned to application successfully" in result.output
    mock_post.assert_called_once()
    assert (
        mock_post.call_args[0][0]
        == "https://test.okta.com/api/v1/apps/app456/assignments"
    )
    assert mock_post.call_args[1]["json"]["id"] == "user123"
    assert mock_post.call_args[1]["json"]["profile"] == {"role": "admin"}


@patch("requests.delete")
def test_unassign_app(mock_delete, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 204  # No Content for successful unassignment
    mock_delete.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(unassign_app, ["user123", "app456"])

    assert result.exit_code == 0
    assert "User unassigned from application successfully" in result.output
    mock_delete.assert_called_once_with(
        "https://test.okta.com/api/v1/apps/app456/assignments/user123",
        headers={
            "Authorization": "SSWS test-token",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )


@patch("requests.get")
def test_list_app_assignments(mock_get, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "user1", "externalId": "user1@example.com"},
        {"id": "user2", "externalId": "user2@example.com"},
    ]
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_app_assignments, ["app123"])

    assert result.exit_code == 0
    assert "user1@example.com" in result.output
    assert "user2@example.com" in result.output
    mock_get.assert_called_once_with(
        "https://test.okta.com/api/v1/apps/app123/users",
        headers={
            "Authorization": "SSWS test-token",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )


@patch("requests.post")
def test_deactivate_user(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(deactivate_user, ["user123"])

    assert result.exit_code == 0
    assert "User deactivated successfully" in result.output
    mock_post.assert_called_once_with(
        "https://test.okta.com/api/v1/users/user123/lifecycle/deactivate",
        headers={
            "Authorization": "SSWS test-token",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )


@patch("requests.post")
def test_activate_user(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(activate_user, ["user123"])

    assert result.exit_code == 0
    assert "User activated successfully" in result.output
    mock_post.assert_called_once_with(
        "https://test.okta.com/api/v1/users/user123/lifecycle/activate",
        headers={
            "Authorization": "SSWS test-token",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )


@patch("requests.post")
def test_reset_password(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tempPassword": "newTempPassword123"}
    mock_post.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(reset_password, ["user123"])

    assert result.exit_code == 0
    assert "Temporary password for user user123: newTempPassword123" in result.output
    mock_post.assert_called_once_with(
        "https://test.okta.com/api/v1/users/user123/lifecycle/expire_password",
        headers={
            "Authorization": "SSWS test-token",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={"tempPassword": True},
    )
