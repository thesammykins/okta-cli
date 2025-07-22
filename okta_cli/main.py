import click
from . import users
from . import groups
from . import applications
from . import sessions
from . import policies
from . import authorization
from . import logs
from . import factors
from .config_commands import config as config_commands
from .errors import (
    validate_okta_domain,
    validate_api_token,
    with_error_handling,
    handle_corrupted_config,
)
from .interactive import InteractivePrompts
from .enhanced_config import ProfileManager


@click.group()
def cli():
    """A CLI tool to interact with Okta APIs."""
    # Check if this is first time use and suggest wizard
    try:
        manager = ProfileManager()
        profiles = manager.list_profiles()

        if not profiles:
            click.echo(
                click.style(
                    "💡 No profiles configured. Run 'okta-cli config wizard' to get started!",
                    fg="yellow",
                )
            )
    except Exception:
        # Silently ignore errors during initialization
        pass


@cli.command()
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@with_error_handling
def configure(profile):
    """Configures the Okta domain and API token."""
    okta_domain = click.prompt("Okta domain")
    api_token = click.prompt("API token", hide_input=True, default="")

    # Validate input
    validated_domain = validate_okta_domain(okta_domain)
    validated_token = validate_api_token(api_token)

    # Use ProfileManager instead of legacy config
    manager = ProfileManager()
    
    if profile is None:
        profile = "default"
    
    manager.create_profile(
        name=profile,
        domain=validated_domain,
        token=validated_token
    )
    
    # Set as active profile if it's the first one
    profiles = manager.list_profiles()
    if len(profiles) == 1:
        manager.set_active_profile(profile)
    
    click.echo(f"Configuration saved for profile '{profile}'.")


cli.add_command(users.users)
cli.add_command(groups.groups)
cli.add_command(applications.applications)
cli.add_command(sessions.sessions)
cli.add_command(policies.policies)
cli.add_command(authorization.authorization)
cli.add_command(logs.logs)
cli.add_command(factors.factors)
cli.add_command(config_commands)

if __name__ == "__main__":
    cli()
