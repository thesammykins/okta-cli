import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from okta_cli.groups import list_groups, create_group, show_group, update_group, delete_group, add_user_to_group, remove_user_from_group, list_group_members
from okta_cli import config

@pytest.fixture
def mock_config(tmp_path):
    config_path = tmp_path / "config"
    with patch.object(config, 'CONFIG_FILE', str(config_path)):
        cfg = config.get_config()
        cfg.add_section("default")
        cfg.set("default", "domain", "test.okta.com")
        cfg.set("default", "token", "test-token")
        config.write_config(cfg)
        yield

@patch('requests.get')
def test_list_groups(mock_get, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {'id': '1', 'profile': {'name': 'Group1'}},
        {'id': '2', 'profile': {'name': 'Group2'}},
    ]
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_groups)

    assert result.exit_code == 0
    assert "Group1" in result.output
    assert "Group2" in result.output

@patch('requests.post')
def test_create_group(mock_post, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'id': 'new-group-id',
        'profile': {'name': 'NewGroup'}
    }
    mock_post.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(create_group, [
        '--name', 'NewGroup',
        '--description', 'A new test group'
    ])

    assert result.exit_code == 0
    assert "Group created successfully" in result.output
    assert "NewGroup" in result.output
    mock_post.assert_called_once()
    assert mock_post.call_args[1]['json']['profile']['name'] == 'NewGroup'
    assert mock_post.call_args[1]['json']['profile']['description'] == 'A new test group'

@patch('requests.get')
def test_show_group(mock_get, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'id': '1',
        'profile': {
            'name': 'TestGroup',
            'description': 'A test group'
        }
    }
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(show_group, ['1'])

    assert result.exit_code == 0
    assert "TestGroup" in result.output
    assert "A test group" in result.output

@patch('requests.put')
def test_update_group(mock_put, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'id': '1',
        'profile': {
            'name': 'UpdatedGroup',
            'description': 'An updated test group'
        }
    }
    mock_put.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(update_group, [
        '1',
        '--name', 'UpdatedGroup',
        '--description', 'An updated test group'
    ])

    assert result.exit_code == 0
    assert "Group updated successfully" in result.output
    assert "UpdatedGroup" in result.output
    mock_put.assert_called_once()
    assert mock_put.call_args[1]['json']['profile']['name'] == 'UpdatedGroup'
    assert mock_put.call_args[1]['json']['profile']['description'] == 'An updated test group'

@patch('requests.delete')
def test_delete_group(mock_delete, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 204 # No Content for successful deletion
    mock_delete.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(delete_group, ['1'])

    assert result.exit_code == 0
    assert "Group deleted successfully" in result.output
    mock_delete.assert_called_once_with(
        'https://test.okta.com/api/v1/groups/1',
        headers={
            'Authorization': 'SSWS test-token',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    )

@patch('requests.put')
def test_add_user_to_group(mock_put, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 204 # No Content for successful add
    mock_put.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(add_user_to_group, ['group123', 'user456'])

    assert result.exit_code == 0
    assert "User added to group successfully" in result.output
    mock_put.assert_called_once_with(
        'https://test.okta.com/api/v1/groups/group123/users/user456',
        headers={
            'Authorization': 'SSWS test-token',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    )

@patch('requests.delete')
def test_remove_user_from_group(mock_delete, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 204 # No Content for successful removal
    mock_delete.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(remove_user_from_group, ['group123', 'user456'])

    assert result.exit_code == 0
    assert "User removed from group successfully" in result.output
    mock_delete.assert_called_once_with(
        'https://test.okta.com/api/v1/groups/group123/users/user456',
        headers={
            'Authorization': 'SSWS test-token',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    )

@patch('requests.get')
def test_list_group_members(mock_get, mock_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {'id': 'user1', 'profile': {'login': 'user1@example.com'}},
        {'id': 'user2', 'profile': {'login': 'user2@example.com'}},
    ]
    mock_get.return_value = mock_response

    runner = CliRunner()
    result = runner.invoke(list_group_members, ['group123'])

    assert result.exit_code == 0
    assert "user1@example.com" in result.output
    assert "user2@example.com" in result.output
    mock_get.assert_called_once_with(
        'https://test.okta.com/api/v1/groups/group123/users',
        headers={
            'Authorization': 'SSWS test-token',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    )