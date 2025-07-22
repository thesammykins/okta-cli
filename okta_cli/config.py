"""Legacy config module stub - REMOVED

This module has been removed as part of the transition to the new enhanced
configuration system. The functionality is now provided by:

- okta_cli.enhanced_config.ProfileManager for configuration management
- okta_cli.enhanced_config.get_effective_config for retrieving config values

Please update your imports to use the new configuration system.
"""

raise ImportError(
    "The okta_cli.config module has been removed. "
    "Please migrate to the new configuration system:\n"
    "- Use 'from okta_cli.enhanced_config import ProfileManager, get_effective_config'\n"
    "- Replace config.get_config() with ProfileManager().get_profile()\n"
    "- Replace config.write_config() with ProfileManager().create_profile() or update_profile()\n"
    "- For getting domain/token values, use get_effective_config(profile)\n"
    "See documentation for migration guide."
)
