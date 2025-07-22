import os
import tempfile
from unittest.mock import patch
from click.testing import CliRunner
from okta_cli.main import configure
from okta_cli.enhanced_config import ProfileManager


def test_configure():
    """Test the configure command with the new ProfileManager system."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create temporary config directory
        temp_dir = os.getcwd()
        
        # Mock ProfileManager to use our temp directory
        with patch('okta_cli.main.ProfileManager') as mock_profile_manager_class:
            # Create actual instances that use our temp directory
            def create_real_manager(*args, **kwargs):
                return ProfileManager(temp_dir)
            mock_profile_manager_class.side_effect = create_real_manager
            
            result = runner.invoke(
                configure,
                input="test.okta.com\nmy-api-token-that-is-longer-than-20-chars\n",
            )
            if result.exit_code != 0:
                print(f"Exit code: {result.exit_code}")
                print(f"Output: {result.output}")
            assert result.exit_code == 0
            assert "Configuration saved for profile 'default'" in result.output

            # Verify the profile was created with ProfileManager
            manager = ProfileManager(temp_dir)
            profiles = manager.list_profiles()
            assert "default" in profiles
            
            profile = manager.get_profile("default")
            assert profile["domain"] == "test.okta.com"
            assert profile["token"] == "my-api-token-that-is-longer-than-20-chars"
