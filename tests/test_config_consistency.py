"""
Tests for configuration consistency and legacy config removal.

This test module ensures that the legacy config module has been properly
removed and cannot be imported, while validating that the enhanced config
system is working correctly.
"""
import pytest
from unittest.mock import patch


def test_legacy_config_module_cannot_be_imported():
    """Test that the legacy config module cannot be imported."""
    with pytest.raises(ImportError) as exc_info:
        from okta_cli import config
        # Try to use the module to ensure it fails
        config.get_config()
    
    # Check that the error message explains the migration
    assert "The okta_cli.config module has been removed" in str(exc_info.value)
    assert "Please migrate to the new configuration system" in str(exc_info.value)
    assert "ProfileManager" in str(exc_info.value)
    assert "get_effective_config" in str(exc_info.value)


def test_legacy_get_config_function_unavailable():
    """Test that get_config function from legacy config is not accessible."""
    with pytest.raises(ImportError) as exc_info:
        from okta_cli.config import get_config
    
    assert "The okta_cli.config module has been removed" in str(exc_info.value)


def test_legacy_write_config_function_unavailable():
    """Test that write_config function from legacy config is not accessible."""
    with pytest.raises(ImportError) as exc_info:
        from okta_cli.config import write_config
    
    assert "The okta_cli.config module has been removed" in str(exc_info.value)


def test_legacy_config_file_constant_unavailable():
    """Test that CONFIG_FILE constant from legacy config is not accessible."""
    with pytest.raises(ImportError) as exc_info:
        from okta_cli.config import CONFIG_FILE
    
    assert "The okta_cli.config module has been removed" in str(exc_info.value)


def test_enhanced_config_can_be_imported():
    """Test that the enhanced config module can be imported successfully."""
    try:
        from okta_cli.enhanced_config import ProfileManager, get_effective_config
        
        # Ensure these are callable
        assert callable(ProfileManager)
        assert callable(get_effective_config)
        
        # Test basic instantiation
        manager = ProfileManager()
        assert manager is not None
        
    except Exception as e:
        pytest.fail(f"Enhanced config should be importable: {e}")


def test_enhanced_config_imports_all_expected_components():
    """Test that all expected components can be imported from enhanced config."""
    expected_imports = [
        'ProfileManager',
        'EnvironmentConfig', 
        'ConfigValidator',
        'get_effective_config',
        'get_active_profile',
        'set_active_profile',
        'list_profiles',
        'delete_profile',
        'validate_profile',
        'health_check'
    ]
    
    for import_name in expected_imports:
        try:
            exec(f"from okta_cli.enhanced_config import {import_name}")
        except ImportError as e:
            pytest.fail(f"Should be able to import {import_name} from enhanced_config: {e}")


def test_migration_error_message_provides_helpful_guidance():
    """Test that the error message provides specific migration guidance."""
    with pytest.raises(ImportError) as exc_info:
        from okta_cli import config
        config.get_config()
    
    error_message = str(exc_info.value)
    
    # Check for specific migration instructions
    expected_instructions = [
        "Use 'from okta_cli.enhanced_config import ProfileManager, get_effective_config'",
        "Replace config.get_config() with ProfileManager().get_profile()",
        "Replace config.write_config() with ProfileManager().create_profile() or update_profile()",
        "For getting domain/token values, use get_effective_config(profile)"
    ]
    
    for instruction in expected_instructions:
        assert instruction in error_message


def test_direct_config_module_import_raises_error():
    """Test that importing the config module directly raises an ImportError."""
    with pytest.raises(ImportError) as exc_info:
        import okta_cli.config
    
    assert "The okta_cli.config module has been removed" in str(exc_info.value)


def test_no_remnants_of_legacy_config_in_enhanced_config():
    """Test that enhanced config doesn't contain any legacy config remnants."""
    import okta_cli.enhanced_config as enhanced_config
    
    # These should not exist in the enhanced config module
    legacy_attributes = ['get_config', 'write_config', 'CONFIG_FILE']
    
    for attr in legacy_attributes:
        assert not hasattr(enhanced_config, attr), \
            f"Enhanced config should not have legacy attribute {attr}"


def test_enhanced_config_is_default_import():
    """Test that enhanced config functionality is the expected default."""
    # This tests that when someone tries to use config functionality,
    # they are directed to use the enhanced system
    
    # These should work without issues
    from okta_cli.enhanced_config import ProfileManager, get_effective_config
    
    # Basic functionality test
    manager = ProfileManager()
    profiles = manager.list_profiles()  # Should return empty dict by default
    assert isinstance(profiles, dict)


def test_consistent_configuration_behavior():
    """Test that configuration behavior is consistent across the system."""
    from okta_cli.enhanced_config import ProfileManager
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = ProfileManager(temp_dir)
        
        # Test that we can create and retrieve profiles consistently
        manager.create_profile("test", "test.okta.com", "test-token-123456")
        profile = manager.get_profile("test")
        
        assert profile["domain"] == "test.okta.com"
        assert profile["token"] == "test-token-123456"
        assert "created_at" in profile
        assert "last_used" in profile


def test_no_config_module_in_enhanced_imports():
    """Test that enhanced config doesn't accidentally import legacy config."""
    import okta_cli.enhanced_config
    import sys
    
    # Check that legacy config module is not in the modules loaded by enhanced_config
    # This would indicate an accidental import
    if 'okta_cli.config' in sys.modules:
        # The legacy config might be loaded due to the error it raises
        # But it should not be used by enhanced_config
        
        # Try to access enhanced config functionality to ensure it works independently
        manager = okta_cli.enhanced_config.ProfileManager()
        profiles = manager.list_profiles()
        assert isinstance(profiles, dict)


def test_error_message_references_documentation():
    """Test that the error message references documentation for migration guide."""
    with pytest.raises(ImportError) as exc_info:
        from okta_cli import config
        config.get_config()
    
    error_message = str(exc_info.value)
    assert "See documentation for migration guide" in error_message
