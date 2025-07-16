"""
CLI commands for enhanced configuration management.
"""

import click
import json
import os
from .enhanced_config import (
    ProfileManager, ConfigValidator, EnvironmentConfig,
    get_effective_config, health_check, validate_profile
)
from .errors import with_error_handling
from .interactive import InteractivePrompts
from .formatting import ConfigFormatter, create_output_option, format_and_output
from .progress import progress_spinner, connectivity_test_progress


@click.group()
def config():
    """Manage configuration profiles and settings."""
    pass


@config.command('list')
@create_output_option()
@with_error_handling
def list_profiles(output):
    """List all configuration profiles."""
    manager = ProfileManager()
    profiles = manager.list_profiles()
    active_profile = manager.get_active_profile()
    
    if not profiles:
        click.echo("No profiles configured.")
        return
    
    if output == 'table':
        formatter = ConfigFormatter('table')
        click.echo(formatter.format_profile_list(profiles, active_profile))
    else:
        format_and_output(profiles, output, 'config')


@config.command('create')
@click.argument('name')
@click.option('--domain', required=True, help='Okta domain')
@click.option('--token', required=True, help='API token')
@click.option('--set-active', is_flag=True, help='Set as active profile')
@with_error_handling
def create_profile(name, domain, token, set_active):
    """Create a new configuration profile."""
    manager = ProfileManager()
    validator = ConfigValidator()
    
    # Validate inputs
    if not validator.validate_domain(domain):
        click.echo(f"Error: Invalid domain format: {domain}")
        return
    
    if not validator.validate_token(token):
        click.echo(f"Error: Invalid token format")
        return
    
    if not validator.validate_profile(name):
        click.echo(f"Error: Invalid profile name: {name}")
        return
    
    try:
        manager.create_profile(name, domain, token)
        click.echo(f"Profile '{name}' created successfully.")
        
        if set_active:
            manager.set_active_profile(name)
            click.echo(f"Profile '{name}' set as active.")
            
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command('update')
@click.argument('name')
@click.option('--domain', help='New Okta domain')
@click.option('--token', help='New API token')
@with_error_handling
def update_profile(name, domain, token):
    """Update an existing configuration profile."""
    manager = ProfileManager()
    validator = ConfigValidator()
    
    # Validate inputs
    if domain and not validator.validate_domain(domain):
        click.echo(f"Error: Invalid domain format: {domain}")
        return
    
    if token and not validator.validate_token(token):
        click.echo(f"Error: Invalid token format")
        return
    
    try:
        manager.update_profile(name, domain=domain, token=token)
        click.echo(f"Profile '{name}' updated successfully.")
        
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command('delete')
@click.argument('name')
@click.option('--force', is_flag=True, help='Force deletion without confirmation')
@with_error_handling
def delete_profile(name, force):
    """Delete a configuration profile."""
    manager = ProfileManager()
    
    if not force:
        if not click.confirm(f"Are you sure you want to delete profile '{name}'?"):
            click.echo("Profile deletion cancelled.")
            return
    
    try:
        manager.delete_profile(name)
        click.echo(f"Profile '{name}' deleted successfully.")
        
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command('activate')
@click.argument('name')
@with_error_handling
def activate_profile(name):
    """Set a profile as the active profile."""
    manager = ProfileManager()
    
    try:
        # Check if profile exists
        manager.get_profile(name)
        manager.set_active_profile(name)
        click.echo(f"Profile '{name}' is now active.")
        
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command('show')
@click.argument('name', required=False)
@with_error_handling
def show_profile(name):
    """Show details of a configuration profile."""
    manager = ProfileManager()
    
    if name is None:
        name = manager.get_active_profile()
    
    try:
        profile_data = manager.get_profile(name)
        
        click.echo(f"Profile: {name}")
        click.echo(f"Domain: {profile_data['domain']}")
        click.echo(f"Token: {'*' * 20}...{profile_data['token'][-4:]}")
        click.echo(f"Created: {profile_data.get('created_at', 'Unknown')}")
        click.echo(f"Last Used: {profile_data.get('last_used', 'Never')}")
        
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command('validate')
@click.argument('name', required=False)
@with_error_handling
def validate_profile_command(name):
    """Validate a configuration profile."""
    manager = ProfileManager()
    
    if name is None:
        name = manager.get_active_profile()
    
    try:
        result = validate_profile(name)
        
        click.echo(f"Profile: {result['profile']}")
        click.echo(f"Valid: {'✓' if result['valid'] else '✗'}")
        
        if result['issues']:
            click.echo("Issues:")
            for issue in result['issues']:
                click.echo(f"  - {issue}")
        else:
            click.echo("No issues found.")
            
    except Exception as e:
        click.echo(f"Error: {e}")


@config.command('health')
@click.argument('name', required=False)
@create_output_option()
@with_error_handling
def health_check_command(name, output):
    """Perform health check on a configuration profile."""
    try:
        domain, token = get_effective_config(name)
        
        def test_connectivity():
            return health_check(domain, token)
        
        result = connectivity_test_progress(test_connectivity, "Running health check")
        
        if output == 'table':
            formatter = ConfigFormatter('table')
            click.echo(formatter.format_health_check(result))
        else:
            format_and_output(result, output, 'config')
                
    except Exception as e:
        click.echo(f"Error: {e}")


@config.command('backup')
@click.option('--output', '-o', help='Output file path')
@with_error_handling
def backup_config(output):
    """Create a backup of the configuration."""
    manager = ProfileManager()
    
    if output:
        backup_path = output
        result = manager.export_config(backup_path)
        if result:
            click.echo(f"Configuration backed up to: {backup_path}")
        else:
            click.echo("Failed to create backup.")
    else:
        backup_path = manager.create_backup()
        click.echo(f"Configuration backed up to: {backup_path}")


@config.command('restore')
@click.argument('backup_path')
@click.option('--force', is_flag=True, help='Force restore without confirmation')
@with_error_handling
def restore_config(backup_path, force):
    """Restore configuration from a backup."""
    manager = ProfileManager()
    
    if not os.path.exists(backup_path):
        click.echo(f"Error: Backup file not found: {backup_path}")
        return
    
    if not force:
        if not click.confirm("This will overwrite your current configuration. Continue?"):
            click.echo("Restore cancelled.")
            return
    
    result = manager.restore_from_backup(backup_path)
    if result:
        click.echo("Configuration restored successfully.")
    else:
        click.echo("Failed to restore configuration.")


@config.command('export')
@click.argument('output_path')
@with_error_handling
def export_config(output_path):
    """Export configuration to a file."""
    manager = ProfileManager()
    
    result = manager.export_config(output_path)
    if result:
        click.echo(f"Configuration exported to: {output_path}")
    else:
        click.echo("Failed to export configuration.")


@config.command('import')
@click.argument('input_path')
@click.option('--force', is_flag=True, help='Force import without confirmation')
@with_error_handling
def import_config(input_path, force):
    """Import configuration from a file."""
    manager = ProfileManager()
    
    if not os.path.exists(input_path):
        click.echo(f"Error: Input file not found: {input_path}")
        return
    
    if not force:
        if not click.confirm("This will overwrite your current configuration. Continue?"):
            click.echo("Import cancelled.")
            return
    
    result = manager.import_config(input_path)
    if result:
        click.echo("Configuration imported successfully.")
    else:
        click.echo("Failed to import configuration.")


@config.command('env')
@with_error_handling
def show_env_config():
    """Show environment variable configuration."""
    env_config = EnvironmentConfig()
    
    click.echo("Environment Configuration:")
    click.echo(f"OKTA_DOMAIN: {env_config.get_domain() or 'Not set'}")
    click.echo(f"OKTA_TOKEN: {'Set' if env_config.get_token() else 'Not set'}")
    click.echo(f"OKTA_PROFILE: {env_config.get_profile() or 'Not set'}")
    
    if env_config.has_complete_config():
        click.echo("✓ Complete configuration available via environment variables")
    else:
        click.echo("✗ Incomplete environment configuration")


@config.command('migrate')
@click.argument('legacy_config_path')
@with_error_handling
def migrate_legacy_config(legacy_config_path):
    """Migrate legacy configuration format."""
    manager = ProfileManager()
    
    if not os.path.exists(legacy_config_path):
        click.echo(f"Error: Legacy config file not found: {legacy_config_path}")
        return
    
    result = manager.migrate_legacy_config(legacy_config_path)
    if result:
        click.echo("Legacy configuration migrated successfully.")
    else:
        click.echo("Failed to migrate legacy configuration.")


@config.command('current')
@create_output_option()
@with_error_handling
def show_current_config(output):
    """Show current effective configuration."""
    try:
        domain, token = get_effective_config()
        
        # Check source
        env_config = EnvironmentConfig()
        if env_config.has_complete_config():
            source = "Environment variables"
        else:
            manager = ProfileManager()
            active_profile = manager.get_active_profile()
            source = f"Profile '{active_profile}'"
        
        current_config = {
            "Domain": domain,
            "Token": f"{'*' * 20}...{token[-4:]}",
            "Source": source
        }
        
        if output == 'table':
            formatter = ConfigFormatter('table')
            click.echo(formatter.format_output(current_config))
        else:
            format_and_output(current_config, output, 'config')
            
    except Exception as e:
        click.echo(f"Error: {e}")


@config.command('wizard')
@with_error_handling
def configuration_wizard():
    """Interactive configuration wizard for first-time setup."""
    interactive = InteractivePrompts()
    interactive.configuration_wizard()


@config.command('interactive')
@with_error_handling
def interactive_mode():
    """Interactive configuration management."""
    interactive = InteractivePrompts()
    
    while True:
        click.echo("\n" + "="*50)
        click.echo("Interactive Configuration Management")
        click.echo("="*50)
        
        options = [
            "Show configuration status",
            "Create new profile",
            "Update existing profile",
            "Delete profile",
            "Set active profile",
            "Run health check",
            "Exit"
        ]
        
        click.echo("\nOptions:")
        for i, option in enumerate(options, 1):
            click.echo(f"  {i}. {option}")
        
        try:
            choice = click.prompt(
                "\nSelect option",
                type=int,
                default=1,
                show_default=True
            )
            
            if choice == 1:
                interactive.show_configuration_status()
            elif choice == 2:
                interactive.interactive_profile_creation()
            elif choice == 3:
                interactive.interactive_profile_update()
            elif choice == 4:
                # Delete profile
                try:
                    profile_name = interactive.prompt_for_profile_selection()
                    manager = ProfileManager()
                    if click.confirm(f"Are you sure you want to delete profile '{profile_name}'?"):
                        manager.delete_profile(profile_name)
                        click.echo(click.style(f"✅ Profile '{profile_name}' deleted successfully!", fg='green'))
                except Exception as e:
                    click.echo(click.style(f"❌ Error: {e}", fg='red'))
            elif choice == 5:
                # Set active profile
                try:
                    profile_name = interactive.prompt_for_profile_selection()
                    manager = ProfileManager()
                    manager.set_active_profile(profile_name)
                    click.echo(click.style(f"✅ Profile '{profile_name}' set as active!", fg='green'))
                except Exception as e:
                    click.echo(click.style(f"❌ Error: {e}", fg='red'))
            elif choice == 6:
                # Health check
                try:
                    profile_name = interactive.prompt_for_profile_selection()
                    domain, token = get_effective_config(profile_name)
                    
                    def test_connectivity():
                        return health_check(domain, token)
                    
                    result = connectivity_test_progress(test_connectivity, "Running health check")
                    
                    formatter = ConfigFormatter('table')
                    click.echo(formatter.format_health_check(result))
                except Exception as e:
                    click.echo(click.style(f"❌ Error: {e}", fg='red'))
            elif choice == 7:
                click.echo("Goodbye!")
                break
            else:
                click.echo(click.style("❌ Invalid option. Please try again.", fg='red'))
                
        except click.Abort:
            click.echo("\nGoodbye!")
            break
        except (ValueError, click.BadParameter):
            click.echo(click.style("❌ Please enter a valid number.", fg='red'))


@config.command('status')
@with_error_handling
def show_status():
    """Show detailed configuration status."""
    interactive = InteractivePrompts()
    interactive.show_configuration_status()


if __name__ == '__main__':
    config()