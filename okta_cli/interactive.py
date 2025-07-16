"""
Interactive prompts and usability enhancements for the Okta CLI tool.
"""

import click
import os
import sys
import time
from typing import Dict, Any, Optional, List, Tuple
from .enhanced_config import (
    ProfileManager,
    ConfigValidator,
    EnvironmentConfig,
    get_effective_config,
)
from .errors import ConfigurationError, ValidationError


class InteractivePrompts:
    """
    Interactive prompts for user-friendly configuration and operations.
    """

    def __init__(self):
        """Initialize interactive prompts."""
        self.validator = ConfigValidator()
        self.profile_manager = ProfileManager()
        self.env_config = EnvironmentConfig()

    def prompt_for_domain(self, current_domain: str = None) -> str:
        """
        Prompt user for Okta domain with validation.

        Args:
            current_domain: Current domain value (for updates)

        Returns:
            Validated domain
        """
        while True:
            prompt_text = "Okta domain"
            if current_domain:
                prompt_text += f" (current: {current_domain})"

            domain = click.prompt(
                prompt_text,
                default=current_domain or "",
                show_default=bool(current_domain),
            )

            if not domain and current_domain:
                return current_domain

            if self.validator.validate_domain(domain):
                return domain

            click.echo(
                click.style(
                    "❌ Invalid domain format. Please use format: yourorg.okta.com",
                    fg="red",
                )
            )

    def prompt_for_token(self, current_token: str = None) -> str:
        """
        Prompt user for API token with validation.

        Args:
            current_token: Current token value (for updates)

        Returns:
            Validated token
        """
        while True:
            prompt_text = "API token"
            if current_token:
                prompt_text += f" (current: {'*' * 20}...{current_token[-4:]})"

            token = click.prompt(
                prompt_text,
                hide_input=True,
                default=current_token or "",
                show_default=False,
            )

            if not token and current_token:
                return current_token

            if self.validator.validate_token(token):
                return token

            click.echo(
                click.style(
                    "❌ Invalid token format. Token must be at least 20 characters long.",
                    fg="red",
                )
            )

    def prompt_for_profile_name(self, default_name: str = None) -> str:
        """
        Prompt user for profile name with validation.

        Args:
            default_name: Default profile name

        Returns:
            Validated profile name
        """
        while True:
            profile_name = click.prompt(
                "Profile name", default=default_name or "default", show_default=True
            )

            if self.validator.validate_profile(profile_name):
                return profile_name

            click.echo(
                click.style(
                    "❌ Invalid profile name. Use only letters, numbers, underscores, and hyphens.",
                    fg="red",
                )
            )

    def prompt_for_profile_selection(self, include_new: bool = False) -> str:
        """
        Prompt user to select from existing profiles.

        Args:
            include_new: Whether to include "Create new profile" option

        Returns:
            Selected profile name or "new" for new profile
        """
        profiles = self.profile_manager.list_profiles()

        if not profiles and not include_new:
            raise ConfigurationError("No profiles available")

        options = []
        if include_new:
            options.append("Create new profile")

        for profile_name in profiles.keys():
            options.append(f"Profile: {profile_name}")

        if not options:
            return "new"

        click.echo("\nAvailable options:")
        for i, option in enumerate(options, 1):
            click.echo(f"  {i}. {option}")

        while True:
            try:
                choice = click.prompt(
                    "Select option", type=int, default=1, show_default=True
                )

                if 1 <= choice <= len(options):
                    selected = options[choice - 1]
                    if selected == "Create new profile":
                        return "new"
                    else:
                        return selected.replace("Profile: ", "")
                else:
                    click.echo(
                        click.style(
                            f"❌ Please enter a number between 1 and {len(options)}",
                            fg="red",
                        )
                    )
            except click.Abort:
                raise
            except (ValueError, click.BadParameter):
                click.echo(click.style("❌ Please enter a valid number", fg="red"))

    def configuration_wizard(self) -> bool:
        """
        Interactive configuration wizard for first-time setup.

        Returns:
            True if configuration was successful
        """
        click.echo(
            click.style(
                "\n🚀 Welcome to Okta CLI Configuration Wizard!\n", fg="cyan", bold=True
            )
        )

        # Check if any profiles exist
        profiles = self.profile_manager.list_profiles()
        if profiles:
            click.echo("Existing profiles found:")
            for profile_name in profiles.keys():
                click.echo(f"  • {profile_name}")

            if not click.confirm("\nWould you like to create a new profile?"):
                return False

        # Get profile information
        click.echo("\nLet's create your first profile:")

        profile_name = self.prompt_for_profile_name()

        # Check if profile already exists
        if profile_name in profiles:
            if not click.confirm(
                f"Profile '{profile_name}' already exists. Overwrite?"
            ):
                return False

        click.echo(f"\nConfiguring profile: {profile_name}")

        # Get domain and token
        domain = self.prompt_for_domain()
        token = self.prompt_for_token()

        # Test connectivity
        if click.confirm("\nTest connectivity to Okta API?", default=True):
            click.echo("Testing connectivity...")

            with click.progressbar(
                length=100, label="Connecting to Okta API", show_percent=True
            ) as bar:
                for i in range(50):
                    time.sleep(0.02)
                    bar.update(1)

                connectivity_result = self.validator.validate_connectivity(
                    domain, token
                )

                for i in range(50):
                    time.sleep(0.02)
                    bar.update(1)

            if connectivity_result:
                click.echo(click.style("✅ Connectivity test passed!", fg="green"))
            else:
                click.echo(click.style("❌ Connectivity test failed!", fg="red"))
                if not click.confirm("Continue anyway?"):
                    return False

        # Create profile
        try:
            if profile_name in profiles:
                self.profile_manager.update_profile(profile_name, domain, token)
                click.echo(
                    click.style(
                        f"✅ Profile '{profile_name}' updated successfully!", fg="green"
                    )
                )
            else:
                self.profile_manager.create_profile(profile_name, domain, token)
                click.echo(
                    click.style(
                        f"✅ Profile '{profile_name}' created successfully!", fg="green"
                    )
                )
        except Exception as e:
            click.echo(click.style(f"❌ Failed to create profile: {e}", fg="red"))
            return False

        # Set as active profile
        if click.confirm(f"Set '{profile_name}' as active profile?", default=True):
            self.profile_manager.set_active_profile(profile_name)
            click.echo(
                click.style(f"✅ Profile '{profile_name}' set as active!", fg="green")
            )

        # Show next steps
        click.echo(click.style("\n🎉 Configuration complete!", fg="green", bold=True))
        click.echo("\nNext steps:")
        click.echo("  • Test your configuration: okta-cli config health")
        click.echo("  • List users: okta-cli users list")
        click.echo("  • Get help: okta-cli --help")

        return True

    def interactive_profile_creation(self) -> bool:
        """
        Interactive profile creation with guided prompts.

        Returns:
            True if profile was created successfully
        """
        click.echo(click.style("\n➕ Create New Profile\n", fg="cyan", bold=True))

        # Get profile name
        profile_name = self.prompt_for_profile_name()

        # Check if profile exists
        profiles = self.profile_manager.list_profiles()
        if profile_name in profiles:
            click.echo(
                click.style(f"⚠️  Profile '{profile_name}' already exists.", fg="yellow")
            )
            if not click.confirm("Overwrite existing profile?"):
                return False

        # Get configuration
        domain = self.prompt_for_domain()
        token = self.prompt_for_token()

        # Test connectivity
        if click.confirm("Test connectivity?", default=True):
            with click.progressbar(
                length=100, label="Testing connectivity", show_percent=True
            ) as bar:
                for i in range(50):
                    time.sleep(0.01)
                    bar.update(1)

                connectivity_result = self.validator.validate_connectivity(
                    domain, token
                )

                for i in range(50):
                    time.sleep(0.01)
                    bar.update(1)

            if not connectivity_result:
                click.echo(click.style("❌ Connectivity test failed!", fg="red"))
                if not click.confirm("Continue anyway?"):
                    return False

        # Create profile
        try:
            if profile_name in profiles:
                self.profile_manager.update_profile(profile_name, domain, token)
                action = "updated"
            else:
                self.profile_manager.create_profile(profile_name, domain, token)
                action = "created"

            click.echo(
                click.style(
                    f"✅ Profile '{profile_name}' {action} successfully!", fg="green"
                )
            )

            # Ask to set as active
            if click.confirm(f"Set '{profile_name}' as active profile?", default=True):
                self.profile_manager.set_active_profile(profile_name)
                click.echo(
                    click.style(
                        f"✅ Profile '{profile_name}' set as active!", fg="green"
                    )
                )

            return True

        except Exception as e:
            click.echo(click.style(f"❌ Failed to create profile: {e}", fg="red"))
            return False

    def interactive_profile_update(self) -> bool:
        """
        Interactive profile update with guided prompts.

        Returns:
            True if profile was updated successfully
        """
        click.echo(click.style("\n✏️  Update Profile\n", fg="cyan", bold=True))

        # Select profile to update
        try:
            profile_name = self.prompt_for_profile_selection()
        except ConfigurationError:
            click.echo(click.style("❌ No profiles available to update.", fg="red"))
            return False

        # Get current profile data
        try:
            current_profile = self.profile_manager.get_profile(profile_name)
        except ValueError as e:
            click.echo(click.style(f"❌ {e}", fg="red"))
            return False

        click.echo(f"\nUpdating profile: {profile_name}")
        click.echo(f"Current domain: {current_profile['domain']}")
        click.echo(f"Current token: {'*' * 20}...{current_profile['token'][-4:]}")

        # Get updates
        click.echo("\nEnter new values (press Enter to keep current):")

        domain = self.prompt_for_domain(current_profile["domain"])
        token = self.prompt_for_token(current_profile["token"])

        # Check if anything changed
        if domain == current_profile["domain"] and token == current_profile["token"]:
            click.echo(click.style("ℹ️  No changes made.", fg="yellow"))
            return True

        # Test connectivity if changed
        if domain != current_profile["domain"] or token != current_profile["token"]:
            if click.confirm("Test connectivity with new settings?", default=True):
                with click.progressbar(
                    length=100, label="Testing connectivity", show_percent=True
                ) as bar:
                    for i in range(50):
                        time.sleep(0.01)
                        bar.update(1)

                    connectivity_result = self.validator.validate_connectivity(
                        domain, token
                    )

                    for i in range(50):
                        time.sleep(0.01)
                        bar.update(1)

                if not connectivity_result:
                    click.echo(click.style("❌ Connectivity test failed!", fg="red"))
                    if not click.confirm("Continue anyway?"):
                        return False

        # Update profile
        try:
            self.profile_manager.update_profile(profile_name, domain, token)
            click.echo(
                click.style(
                    f"✅ Profile '{profile_name}' updated successfully!", fg="green"
                )
            )
            return True

        except Exception as e:
            click.echo(click.style(f"❌ Failed to update profile: {e}", fg="red"))
            return False

    def show_configuration_status(self) -> None:
        """Show current configuration status with helpful information."""
        click.echo(click.style("\n📊 Configuration Status\n", fg="cyan", bold=True))

        # Check environment variables
        env_domain = self.env_config.get_domain()
        env_token = self.env_config.get_token()
        env_profile = self.env_config.get_profile()

        if env_domain or env_token:
            click.echo(click.style("🌍 Environment Variables:", fg="blue", bold=True))
            click.echo(f"  OKTA_DOMAIN: {env_domain or 'Not set'}")
            click.echo(f"  OKTA_TOKEN: {'Set' if env_token else 'Not set'}")
            click.echo(f"  OKTA_PROFILE: {env_profile or 'Not set'}")

            if self.env_config.has_complete_config():
                click.echo(
                    click.style(
                        "  ✅ Complete configuration via environment", fg="green"
                    )
                )
            else:
                click.echo(
                    click.style(
                        "  ⚠️  Incomplete environment configuration", fg="yellow"
                    )
                )
            click.echo()

        # Check profiles
        profiles = self.profile_manager.list_profiles()
        active_profile = self.profile_manager.get_active_profile()

        if profiles:
            click.echo(click.style("👤 Profiles:", fg="blue", bold=True))
            for name, profile_data in profiles.items():
                marker = "🔹" if name == active_profile else "  "
                status = " (active)" if name == active_profile else ""
                click.echo(f"{marker} {name}{status}")
                click.echo(f"    Domain: {profile_data['domain']}")
                click.echo(
                    f"    Created: {time.ctime(profile_data.get('created_at', 0))}"
                )
            click.echo()
        else:
            click.echo(click.style("👤 No profiles configured", fg="yellow"))
            click.echo()

        # Show effective configuration
        try:
            domain, token = get_effective_config()
            click.echo(click.style("⚙️  Effective Configuration:", fg="blue", bold=True))
            click.echo(f"  Domain: {domain}")
            click.echo(f"  Token: {'*' * 20}...{token[-4:]}")

            if self.env_config.has_complete_config():
                click.echo(f"  Source: Environment variables")
            else:
                click.echo(f"  Source: Profile '{active_profile}'")

            click.echo(click.style("  ✅ Ready to use!", fg="green"))

        except ConfigurationError as e:
            click.echo(click.style("⚙️  Effective Configuration:", fg="blue", bold=True))
            click.echo(click.style(f"  ❌ {e}", fg="red"))
            click.echo(
                click.style("  💡 Run 'okta-cli config wizard' to set up", fg="yellow")
            )


def prompt_for_confirmation(message: str, default: bool = False) -> bool:
    """
    Enhanced confirmation prompt with better formatting.

    Args:
        message: Confirmation message
        default: Default value

    Returns:
        User's confirmation
    """
    return click.confirm(click.style(f"❓ {message}", fg="yellow"), default=default)


def show_progress(operation: str, duration: float = 2.0) -> None:
    """
    Show progress bar for operations.

    Args:
        operation: Operation description
        duration: Duration in seconds
    """
    with click.progressbar(
        length=100, label=operation, show_percent=True, show_eta=True
    ) as bar:
        step = duration / 100
        for i in range(100):
            time.sleep(step)
            bar.update(1)


def format_success(message: str) -> str:
    """Format success message with styling."""
    return click.style(f"✅ {message}", fg="green")


def format_error(message: str) -> str:
    """Format error message with styling."""
    return click.style(f"❌ {message}", fg="red")


def format_warning(message: str) -> str:
    """Format warning message with styling."""
    return click.style(f"⚠️  {message}", fg="yellow")


def format_info(message: str) -> str:
    """Format info message with styling."""
    return click.style(f"ℹ️  {message}", fg="blue")
