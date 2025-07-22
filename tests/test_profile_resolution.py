"""
Tests for profile resolution and implicit active profile usage.

This test module validates that the enhanced config system correctly 
resolves profiles implicitly when no profile is specified.
"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from okta_cli.enhanced_config import ProfileManager, get_effective_config
from okta_cli.users import list_users
from okta_cli.groups import list_groups


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_implicit_active_profile_resolution(temp_config_dir):
    """Test that active profile is resolved implicitly when no profile is specified."""
    manager = ProfileManager(temp_config_dir)
    
    # Create multiple profiles
    manager.create_profile("default", "default.okta.com", "default-token-123456789")
    manager.create_profile("dev", "dev.okta.com", "dev-token-123456789")
    manager.create_profile("staging", "staging.okta.com", "staging-token-123456789")
    
    # Set dev as active profile
    manager.set_active_profile("dev")
    
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
            
            runner = CliRunner()
            result = runner.invoke(list_users)  # No --profile flag
            
            assert result.exit_code == 0
            # Should use the active profile (dev)
            mock_get.assert_called_with(
                "https://dev.okta.com/api/v1/users",
                headers={
                    "Authorization": "SSWS dev-token-123456789",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )


def test_active_profile_changes_affect_implicit_resolution(temp_config_dir):
    """Test that changing active profile affects implicit resolution."""
    manager = ProfileManager(temp_config_dir)
    
    # Create profiles
    manager.create_profile("dev", "dev.okta.com", "dev-token-123456789")
    manager.create_profile("prod", "prod.okta.com", "prod-token-123456789")
    
    # Initially set dev as active
    manager.set_active_profile("dev")
    
    with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
        def create_manager(*args, **kwargs):
            return manager
        mock_profile_class.side_effect = create_manager
        
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            runner = CliRunner()
            
            # First call should use dev
            result = runner.invoke(list_users)
            assert result.exit_code == 0
            mock_get.assert_called_with(
                "https://dev.okta.com/api/v1/users",
                headers={
                    "Authorization": "SSWS dev-token-123456789",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
            
            # Change active profile to prod
            manager.set_active_profile("prod")
            
            # Second call should use prod
            result = runner.invoke(list_users)
            assert result.exit_code == 0
            mock_get.assert_called_with(
                "https://prod.okta.com/api/v1/users",
                headers={
                    "Authorization": "SSWS prod-token-123456789",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )


def test_default_profile_fallback_when_no_active(temp_config_dir):
    """Test that 'default' profile is used when no active profile is set."""
    manager = ProfileManager(temp_config_dir)
    
    # Create only default profile
    manager.create_profile("default", "default.okta.com", "default-token-123456789")
    
    # Don't set any active profile (should fall back to "default")
    
    with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
        def create_manager(*args, **kwargs):
            return manager
        mock_profile_class.side_effect = create_manager
        
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            runner = CliRunner()
            result = runner.invoke(list_users)
            
            assert result.exit_code == 0
            # Should use default profile
            mock_get.assert_called_with(
                "https://default.okta.com/api/v1/users",
                headers={
                    "Authorization": "SSWS default-token-123456789",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )


def test_explicit_profile_overrides_active_profile(temp_config_dir):
    """Test that explicitly specifying a profile overrides the active profile."""
    manager = ProfileManager(temp_config_dir)
    
    # Create profiles
    manager.create_profile("dev", "dev.okta.com", "dev-token-123456789")
    manager.create_profile("staging", "staging.okta.com", "staging-token-123456789")
    
    # Set dev as active
    manager.set_active_profile("dev")
    
    with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
        def create_manager(*args, **kwargs):
            return manager
        mock_profile_class.side_effect = create_manager
        
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            runner = CliRunner()
            # Explicitly specify staging profile, should override active (dev)
            result = runner.invoke(list_users, ["--profile", "staging"])
            
            assert result.exit_code == 0
            # Should use staging, not dev
            mock_get.assert_called_with(
                "https://staging.okta.com/api/v1/users",
                headers={
                    "Authorization": "SSWS staging-token-123456789",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )


def test_get_effective_config_with_active_profile(temp_config_dir):
    """Test get_effective_config function with active profile."""
    manager = ProfileManager(temp_config_dir)
    
    # Create profiles
    manager.create_profile("test", "test.okta.com", "test-token-123456789")
    manager.set_active_profile("test")
    
    with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
        def create_manager(*args, **kwargs):
            return manager
        mock_profile_class.side_effect = create_manager
        
        # Call get_effective_config without specifying a profile
        domain, token = get_effective_config()
        
        assert domain == "test.okta.com"
        assert token == "test-token-123456789"


def test_get_effective_config_explicit_profile_override(temp_config_dir):
    """Test get_effective_config with explicit profile overriding active profile."""
    manager = ProfileManager(temp_config_dir)
    
    # Create profiles
    manager.create_profile("active", "active.okta.com", "active-token-123456789")
    manager.create_profile("explicit", "explicit.okta.com", "explicit-token-123456789")
    manager.set_active_profile("active")
    
    with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
        def create_manager(*args, **kwargs):
            return manager
        mock_profile_class.side_effect = create_manager
        
        # Call get_effective_config with explicit profile
        domain, token = get_effective_config("explicit")
        
        assert domain == "explicit.okta.com"
        assert token == "explicit-token-123456789"


def test_environment_variable_profile_override(temp_config_dir):
    """Test that OKTA_PROFILE environment variable sets the active profile."""
    manager = ProfileManager(temp_config_dir)
    
    # Create profiles
    manager.create_profile("file_active", "file.okta.com", "file-token-123456789")
    manager.create_profile("env_profile", "env.okta.com", "env-token-123456789")
    manager.set_active_profile("file_active")
    
    with patch.dict(os.environ, {"OKTA_PROFILE": "env_profile"}):
        with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
            def create_manager(*args, **kwargs):
                return manager
            mock_profile_class.side_effect = create_manager
            
            # Environment variable should override file-based active profile
            domain, token = get_effective_config()
            
            assert domain == "env.okta.com"
            assert token == "env-token-123456789"


def test_profile_resolution_with_multiple_commands(temp_config_dir):
    """Test that profile resolution works consistently across different commands."""
    manager = ProfileManager(temp_config_dir)
    
    # Create profile
    manager.create_profile("multi", "multi.okta.com", "multi-token-123456789")
    manager.set_active_profile("multi")
    
    with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
        def create_manager(*args, **kwargs):
            return manager
        mock_profile_class.side_effect = create_manager
        
        runner = CliRunner()
        
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            # Test with users command
            result = runner.invoke(list_users)
            assert result.exit_code == 0
            mock_get.assert_called_with(
                "https://multi.okta.com/api/v1/users",
                headers={
                    "Authorization": "SSWS multi-token-123456789",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
            
            # Test with groups command
            result = runner.invoke(list_groups)
            assert result.exit_code == 0
            mock_get.assert_called_with(
                "https://multi.okta.com/api/v1/groups",
                headers={
                    "Authorization": "SSWS multi-token-123456789",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )


def test_profile_not_found_error_handling(temp_config_dir):
    """Test error handling when active profile doesn't exist."""
    manager = ProfileManager(temp_config_dir)
    
    # Set active profile to something that doesn't exist
    manager.set_active_profile("nonexistent")
    
    with patch('okta_cli.enhanced_config.ProfileManager') as mock_profile_class:
        def create_manager(*args, **kwargs):
            return manager
        mock_profile_class.side_effect = create_manager
        
        runner = CliRunner()
        result = runner.invoke(list_users)
        
        assert result.exit_code == 1
        assert "Profile 'nonexistent' not found" in result.output
