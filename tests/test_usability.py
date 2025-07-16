"""
Tests for usability features including interactive prompts, formatting, and progress indicators.
"""

import pytest
import click
import json
import time
from unittest.mock import Mock, patch, MagicMock
from okta_cli.interactive import InteractivePrompts
from okta_cli.formatting import (
    OutputFormatter,
    UserFormatter,
    GroupFormatter,
    ConfigFormatter,
    format_and_output,
    create_table_from_dict,
    create_table_from_list,
)
from okta_cli.progress import (
    ProgressIndicator,
    progress_spinner,
    progress_bar,
    timed_progress_bar,
    api_call_with_progress,
    connectivity_test_progress,
    batch_operation_progress,
    StepProgress,
)
from okta_cli.completion import CompletionProvider, setup_completion


class TestInteractivePrompts:
    """Test interactive prompts functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.interactive = InteractivePrompts()
        # Clean up any existing profiles from previous tests
        self.interactive.profile_manager.clear_all_profiles()

    @patch("okta_cli.interactive.click.prompt")
    def test_prompt_for_domain_valid(self, mock_prompt):
        """Test prompting for valid domain."""
        mock_prompt.return_value = "test.okta.com"

        result = self.interactive.prompt_for_domain()

        assert result == "test.okta.com"
        mock_prompt.assert_called_once()

    @patch("okta_cli.interactive.click.prompt")
    @patch("okta_cli.interactive.click.echo")
    def test_prompt_for_domain_invalid_then_valid(self, mock_echo, mock_prompt):
        """Test prompting for domain with invalid then valid input."""
        mock_prompt.side_effect = ["invalid-domain", "test.okta.com"]

        result = self.interactive.prompt_for_domain()

        assert result == "test.okta.com"
        assert mock_prompt.call_count == 2
        mock_echo.assert_called()

    @patch("okta_cli.interactive.click.prompt")
    def test_prompt_for_token_valid(self, mock_prompt):
        """Test prompting for valid token."""
        mock_prompt.return_value = "a" * 25  # Valid token length

        result = self.interactive.prompt_for_token()

        assert result == "a" * 25
        mock_prompt.assert_called_once()

    @patch("okta_cli.interactive.click.prompt")
    @patch("okta_cli.interactive.click.echo")
    def test_prompt_for_token_invalid_then_valid(self, mock_echo, mock_prompt):
        """Test prompting for token with invalid then valid input."""
        mock_prompt.side_effect = ["short", "a" * 25]

        result = self.interactive.prompt_for_token()

        assert result == "a" * 25
        assert mock_prompt.call_count == 2
        mock_echo.assert_called()

    @patch("okta_cli.interactive.click.prompt")
    def test_prompt_for_profile_name_valid(self, mock_prompt):
        """Test prompting for valid profile name."""
        mock_prompt.return_value = "test-profile"

        result = self.interactive.prompt_for_profile_name()

        assert result == "test-profile"
        mock_prompt.assert_called_once()

    @patch("okta_cli.interactive.click.prompt")
    @patch("okta_cli.interactive.click.echo")
    def test_prompt_for_profile_name_invalid_then_valid(self, mock_echo, mock_prompt):
        """Test prompting for profile name with invalid then valid input."""
        mock_prompt.side_effect = ["invalid name!", "test-profile"]

        result = self.interactive.prompt_for_profile_name()

        assert result == "test-profile"
        assert mock_prompt.call_count == 2
        mock_echo.assert_called()

    @patch("okta_cli.interactive.click.prompt")
    @patch("okta_cli.interactive.click.echo")
    def test_prompt_for_profile_selection(self, mock_echo, mock_prompt):
        """Test profile selection prompt."""
        self.interactive.profile_manager.create_profile(
            "test1", "test1.okta.com", "token1"
        )
        self.interactive.profile_manager.create_profile(
            "test2", "test2.okta.com", "token2"
        )

        mock_prompt.return_value = 1

        result = self.interactive.prompt_for_profile_selection()

        assert result in ["test1", "test2"]
        mock_prompt.assert_called_once()

    @patch("okta_cli.interactive.click.progressbar")
    @patch("okta_cli.interactive.click.confirm")
    @patch("okta_cli.interactive.click.echo")
    def test_configuration_wizard_success(
        self, mock_echo, mock_confirm, mock_progressbar
    ):
        """Test successful configuration wizard."""
        mock_confirm.side_effect = [
            True,
            True,
            True,
        ]  # Test connectivity, continue, set active
        mock_progressbar.return_value.__enter__.return_value = Mock()

        with patch.object(
            self.interactive, "prompt_for_profile_name", return_value="test"
        ):
            with patch.object(
                self.interactive, "prompt_for_domain", return_value="test.okta.com"
            ):
                with patch.object(
                    self.interactive, "prompt_for_token", return_value="a" * 25
                ):
                    with patch.object(
                        self.interactive.validator,
                        "validate_connectivity",
                        return_value=True,
                    ):
                        result = self.interactive.configuration_wizard()

        assert result is True
        mock_confirm.assert_called()
        mock_echo.assert_called()

    @patch("okta_cli.interactive.click.progressbar")
    @patch("okta_cli.interactive.click.confirm")
    @patch("okta_cli.interactive.click.echo")
    def test_interactive_profile_creation_success(
        self, mock_echo, mock_confirm, mock_progressbar
    ):
        """Test successful interactive profile creation."""
        mock_confirm.side_effect = [True, True]  # Test connectivity, set active
        mock_progressbar.return_value.__enter__.return_value = Mock()

        with patch.object(
            self.interactive, "prompt_for_profile_name", return_value="test"
        ):
            with patch.object(
                self.interactive, "prompt_for_domain", return_value="test.okta.com"
            ):
                with patch.object(
                    self.interactive, "prompt_for_token", return_value="a" * 25
                ):
                    with patch.object(
                        self.interactive.validator,
                        "validate_connectivity",
                        return_value=True,
                    ):
                        result = self.interactive.interactive_profile_creation()

        assert result is True
        mock_confirm.assert_called()
        mock_echo.assert_called()

    @patch("okta_cli.interactive.click.echo")
    def test_show_configuration_status(self, mock_echo):
        """Test configuration status display."""
        self.interactive.profile_manager.create_profile(
            "test", "test.okta.com", "token123"
        )

        self.interactive.show_configuration_status()

        mock_echo.assert_called()
        # Check that status information was displayed
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Configuration Status" in call for call in calls)


class TestOutputFormatter:
    """Test output formatting functionality."""

    def test_json_format(self):
        """Test JSON output format."""
        formatter = OutputFormatter("json")
        data = {"key": "value", "number": 42}

        result = formatter.format_output(data)

        parsed = json.loads(result)
        assert parsed == data

    def test_table_format_dict(self):
        """Test table format with dictionary data."""
        formatter = OutputFormatter("table")
        data = {"key1": "value1", "key2": "value2"}

        result = formatter.format_output(data)

        assert "key1" in result
        assert "value1" in result
        assert "key2" in result
        assert "value2" in result

    def test_table_format_list(self):
        """Test table format with list data."""
        formatter = OutputFormatter("table")
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

        result = formatter.format_output(data)

        assert "John" in result
        assert "Jane" in result
        assert "30" in result
        assert "25" in result

    def test_csv_format(self):
        """Test CSV output format."""
        formatter = OutputFormatter("csv")
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

        result = formatter.format_output(data)

        lines = result.strip().split("\n")
        assert len(lines) == 3  # Header + 2 data rows
        assert "name,age" in lines[0]
        assert "John,30" in lines[1]
        assert "Jane,25" in lines[2]

    def test_yaml_format(self):
        """Test YAML output format."""
        formatter = OutputFormatter("yaml")
        data = {"key": "value", "number": 42}

        result = formatter.format_output(data)

        assert "key: value" in result
        assert "number: 42" in result

    def test_text_format(self):
        """Test text output format."""
        formatter = OutputFormatter("text")
        data = {"key1": "value1", "key2": "value2"}

        result = formatter.format_output(data)

        assert "key1: value1" in result
        assert "key2: value2" in result

    def test_invalid_format(self):
        """Test invalid format type."""
        with pytest.raises(ValueError):
            OutputFormatter("invalid")


class TestUserFormatter:
    """Test user-specific formatting."""

    def test_format_user_list(self):
        """Test formatting user list."""
        formatter = UserFormatter("table")
        users = [
            {
                "profile": {
                    "login": "john.doe@example.com",
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@example.com",
                },
                "status": "ACTIVE",
                "created": "2023-01-01T00:00:00.000Z",
            }
        ]

        result = formatter.format_user_list(users)

        assert "john.doe@example.com" in result
        assert "John" in result
        assert "Doe" in result
        assert "ACTIVE" in result

    def test_format_user_detail(self):
        """Test formatting user detail."""
        formatter = UserFormatter("table")
        user = {
            "id": "123",
            "profile": {
                "login": "john.doe@example.com",
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
            },
            "status": "ACTIVE",
            "created": "2023-01-01T00:00:00.000Z",
        }

        result = formatter.format_user_detail(user)

        assert "123" in result
        assert "john.doe@example.com" in result
        assert "John" in result
        assert "Doe" in result
        assert "ACTIVE" in result

    def test_format_empty_user_list(self):
        """Test formatting empty user list."""
        formatter = UserFormatter("table")
        users = []

        result = formatter.format_user_list(users)

        assert "No users found" in result


class TestConfigFormatter:
    """Test configuration-specific formatting."""

    def test_format_profile_list(self):
        """Test formatting profile list."""
        formatter = ConfigFormatter("table")
        profiles = {
            "test": {
                "domain": "test.okta.com",
                "token": "token123",
                "created_at": 1640995200.0,
                "last_used": 1640995200.0,
            }
        }

        result = formatter.format_profile_list(profiles, "test")

        assert "test" in result
        assert "test.okta.com" in result
        assert "Active" in result

    def test_format_health_check(self):
        """Test formatting health check results."""
        formatter = ConfigFormatter("table")
        health_data = {
            "status": "healthy",
            "connectivity": True,
            "authentication": True,
            "response_time": 0.5,
            "errors": [],
        }

        result = formatter.format_health_check(health_data)

        assert "healthy" in result
        assert "✅ Connected" in result
        assert "✅ Authenticated" in result
        assert "0.50s" in result


class TestProgressIndicator:
    """Test progress indicator functionality."""

    def test_progress_spinner_context_manager(self):
        """Test progress spinner context manager."""
        with patch("okta_cli.progress.click.echo") as mock_echo:
            with progress_spinner("Testing..."):
                time.sleep(0.1)

        # Should have called echo to display spinner
        mock_echo.assert_called()

    def test_progress_bar_creation(self):
        """Test progress bar creation."""
        items = [1, 2, 3, 4, 5]

        with patch("okta_cli.progress.click.progressbar") as mock_progressbar:
            mock_progressbar.return_value = items
            result = progress_bar(items, "Testing")

        mock_progressbar.assert_called_once()
        assert result == items

    def test_api_call_with_progress(self):
        """Test API call with progress indicator."""

        def mock_api_call(arg1, arg2):
            return {"result": arg1 + arg2}

        with patch("okta_cli.progress.progress_spinner"):
            result = api_call_with_progress(mock_api_call, 1, 2)

        assert result == {"result": 3}

    def test_connectivity_test_progress(self):
        """Test connectivity test with progress."""

        def mock_test():
            return True

        with patch("okta_cli.progress.click.progressbar") as mock_progressbar:
            mock_progressbar.return_value.__enter__.return_value = Mock()
            result = connectivity_test_progress(mock_test)

        assert result is True
        mock_progressbar.assert_called_once()

    def test_batch_operation_progress(self):
        """Test batch operation with progress."""
        items = [1, 2, 3]

        def double(x):
            return x * 2

        with patch("okta_cli.progress.click.progressbar") as mock_progressbar:
            mock_progressbar.return_value.__enter__.return_value = items
            result = batch_operation_progress(items, double)

        assert result == [2, 4, 6]
        mock_progressbar.assert_called_once()

    def test_step_progress(self):
        """Test step progress indicator."""
        progress = StepProgress(3, "Test Progress")
        progress.add_step("Step 1", "First step")
        progress.add_step("Step 2", "Second step")
        progress.add_step("Step 3", "Third step")

        with patch("okta_cli.progress.click.echo") as mock_echo:
            progress.start_step(0)
            progress.complete_step(0)
            progress.start_step(1)
            progress.fail_step(1, "Test error")
            progress.show_summary()

        mock_echo.assert_called()
        assert progress.steps[0]["completed"] is True
        assert progress.steps[1]["completed"] is False


class TestCompletionProvider:
    """Test command completion functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.provider = CompletionProvider()
        # Clean up any existing profiles from previous tests
        self.provider.profile_manager.clear_all_profiles()

    def test_get_profile_names(self):
        """Test getting profile names for completion."""
        # Create some test profiles
        self.provider.profile_manager.create_profile(
            "test1", "test1.okta.com", "token1"
        )
        self.provider.profile_manager.create_profile(
            "test2", "test2.okta.com", "token2"
        )

        result = self.provider.get_profile_names()

        assert "test1" in result
        assert "test2" in result
        assert len(result) == 2

    def test_get_config_commands(self):
        """Test getting config commands for completion."""
        result = self.provider.get_config_commands()

        assert "list" in result
        assert "create" in result
        assert "update" in result
        assert "delete" in result
        assert "wizard" in result

    def test_get_user_commands(self):
        """Test getting user commands for completion."""
        result = self.provider.get_user_commands()

        assert "list" in result
        assert "create" in result
        assert "show" in result
        assert "update" in result
        assert "suspend" in result

    def test_get_group_commands(self):
        """Test getting group commands for completion."""
        result = self.provider.get_group_commands()

        assert "list" in result
        assert "create" in result
        assert "show" in result
        assert "update" in result
        assert "delete" in result

    @patch("okta_cli.completion.click.echo")
    @patch("okta_cli.completion.os.environ.get")
    @patch("builtins.open", new_callable=lambda: MagicMock())
    def test_setup_completion_bash(self, mock_open, mock_env_get, mock_echo):
        """Test setting up bash completion."""
        mock_env_get.return_value = "/bin/bash"

        setup_completion()

        mock_echo.assert_called()
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Bash completion" in call for call in calls)

    @patch("okta_cli.completion.click.echo")
    @patch("okta_cli.completion.os.environ.get")
    @patch("okta_cli.completion.os.makedirs")
    @patch("builtins.open", new_callable=lambda: MagicMock())
    def test_setup_completion_zsh(
        self, mock_open, mock_makedirs, mock_env_get, mock_echo
    ):
        """Test setting up zsh completion."""
        mock_env_get.return_value = "/bin/zsh"

        setup_completion()

        mock_echo.assert_called()
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Zsh completion" in call for call in calls)


class TestUtilityFunctions:
    """Test utility functions."""

    @patch("okta_cli.formatting.click.echo")
    def test_format_and_output(self, mock_echo):
        """Test format_and_output function."""
        data = {"key": "value"}

        format_and_output(data, "json", "generic")

        mock_echo.assert_called_once()
        output = mock_echo.call_args[0][0]
        assert "key" in output
        assert "value" in output

    def test_create_table_from_dict(self):
        """Test creating table from dictionary."""
        data = {"key1": "value1", "key2": "value2"}

        result = create_table_from_dict(data, "Test Title")

        assert "Test Title" in result
        assert "key1" in result
        assert "value1" in result
        assert "key2" in result
        assert "value2" in result

    def test_create_table_from_list(self):
        """Test creating table from list."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        headers = ["name", "age"]

        result = create_table_from_list(data, headers, "Test Title")

        assert "Test Title" in result
        assert "John" in result
        assert "Jane" in result
        assert "30" in result
        assert "25" in result

    def test_create_table_from_empty_list(self):
        """Test creating table from empty list."""
        data = []

        result = create_table_from_list(data)

        assert "No data to display" in result


class TestIntegration:
    """Integration tests for usability features."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clean up any existing profiles from previous tests
        provider = CompletionProvider()
        provider.profile_manager.clear_all_profiles()

    def test_interactive_with_formatting(self):
        """Test interactive prompts with formatting."""
        interactive = InteractivePrompts()

        # Create a test profile
        interactive.profile_manager.create_profile("test", "test.okta.com", "token123")

        # Test status display
        with patch("okta_cli.interactive.click.echo") as mock_echo:
            interactive.show_configuration_status()

        mock_echo.assert_called()

        # Verify that configuration info was displayed
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Configuration Status" in call for call in calls)

    def test_progress_with_formatting(self):
        """Test progress indicators with formatted output."""

        def mock_operation():
            return {"result": "success"}

        with patch("okta_cli.progress.progress_spinner"):
            result = api_call_with_progress(mock_operation, message="Testing...")

        assert result == {"result": "success"}

    def test_completion_with_profiles(self):
        """Test completion with actual profiles."""
        provider = CompletionProvider()

        # Create test profiles
        provider.profile_manager.create_profile("dev", "dev.okta.com", "token1")
        provider.profile_manager.create_profile("prod", "prod.okta.com", "token2")

        # Test completion
        profiles = provider.get_profile_names()

        assert "dev" in profiles
        assert "prod" in profiles
        assert len(profiles) == 2
