import click
import requests
from . import config
from .errors import (
    handle_api_error,
    handle_network_error,
    handle_json_error,
    handle_config_error,
    handle_corrupted_config,
    with_error_handling,
    validate_email,
    validate_login,
    validate_name,
)
from .enhanced_config import get_effective_config
from .formatting import UserFormatter, create_output_option, format_and_output
from .utils import resolve_user_id, resolve_app_id, get_user_by_identifier
from .progress import progress_spinner
import json
import configparser


@click.group()
def users():
    """Manage Okta users."""
    pass


@users.command("list")
@click.option("--profile", default=None, help="The profile to use.")
@create_output_option()
@with_error_handling
def list_users(profile, output):
    """List users in Okta."""
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        # Fall back to legacy config if enhanced config fails
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()

        if profile is None:
            profile = "default"

        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Fetching users from Okta API..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/users", headers=headers, timeout=30
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            users_data = response.json()

            if output == "table":
                formatter = UserFormatter("table")
                click.echo(formatter.format_user_list(users_data))
            else:
                format_and_output(users_data, output, "user")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@users.command("create")
@click.option("--first-name", required=True)
@click.option("--last-name", required=True)
@click.option("--email", required=True)
@click.option("--login", required=True)
@click.option("--profile", default=None, help="The profile to use.")
@create_output_option()
@with_error_handling
def create_user(first_name, last_name, email, login, profile, output):
    """Create a new user in Okta."""
    # Validate input
    validate_name(first_name, "First name")
    validate_name(last_name, "Last name")
    validate_email(email)
    validate_login(login)

    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        # Fall back to legacy config if enhanced config fails
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()

        if profile is None:
            profile = "default"

        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    data = {
        "profile": {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "login": login,
        }
    }

    with progress_spinner("Creating user in Okta..."):
        try:
            response = requests.post(
                f"https://{domain}/api/v1/users?activate=false",
                headers=headers,
                json=data,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            user = response.json()

            if output == "table":
                formatter = UserFormatter("table")
                click.echo(click.style("✅ User created successfully!", fg="green"))
                click.echo(formatter.format_user_detail(user))
            else:
                click.echo(click.style("✅ User created successfully!", fg="green"))
                format_and_output(user, output, "user")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@users.command("show")
@click.argument("user_identifier")
@click.option("--profile", default="default", help="The profile to use.")
def show_user(user_identifier, profile):
    """Show details for a specific user (accepts ID, email, or login)."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    # Try to get user by identifier (ID, email, or login)
    user = get_user_by_identifier(user_identifier, domain, token)

    if user:
        click.echo(json.dumps(user, indent=4))
    else:
        click.echo(f"Error: User not found with identifier '{user_identifier}'")


@users.command("suspend")
@click.argument("user_identifier")
@click.option("--profile", default="default", help="The profile to use.")
def suspend_user(user_identifier, profile):
    """Suspend a user in Okta (accepts ID, email, or login)."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    # Resolve user identifier to ID
    user_id = resolve_user_id(user_identifier, domain, token)
    if not user_id:
        click.echo(f"Error: User not found with identifier '{user_identifier}'")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"https://{domain}/api/v1/users/{user_id}/lifecycle/suspend", headers=headers
    )

    if response.status_code == 200:
        click.echo("User suspended successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@users.command("unsuspend")
@click.argument("user_id")
@click.option("--profile", default="default", help="The profile to use.")
def unsuspend_user(user_id, profile):
    """Unsuspend a user in Okta."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"https://{domain}/api/v1/users/{user_id}/lifecycle/unsuspend", headers=headers
    )

    if response.status_code == 200:
        click.echo("User unsuspended successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@users.command("update")
@click.argument("user_identifier")
@click.option("--first-name", help="User's first name.")
@click.option("--last-name", help="User's last name.")
@click.option("--email", help="User's email address.")
@click.option("--login", help="User's login name.")
@click.option("--profile", default="default", help="The profile to use.")
def update_user(user_identifier, first_name, last_name, email, login, profile):
    """Update a user's profile in Okta (accepts ID, email, or login)."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    # Resolve user identifier to ID
    user_id = resolve_user_id(user_identifier, domain, token)
    if not user_id:
        click.echo(f"Error: User not found with identifier '{user_identifier}'")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    profile_data = {}
    if first_name:
        profile_data["firstName"] = first_name
    if last_name:
        profile_data["lastName"] = last_name
    if email:
        profile_data["email"] = email
    if login:
        profile_data["login"] = login

    if not profile_data:
        click.echo(
            "No update parameters provided. Please provide at least one of --first-name, --last-name, --email, or --login."
        )
        return

    data = {"profile": profile_data}

    response = requests.post(
        f"https://{domain}/api/v1/users/{user_id}", headers=headers, json=data
    )

    if response.status_code == 200:
        user = response.json()
        click.echo("User updated successfully:")
        click.echo(json.dumps(user["profile"], indent=4))
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@users.command("assign-app")
@click.argument("user_identifier")
@click.argument("app_identifier")
@click.option(
    "--profile-attributes",
    help="""JSON string of profile attributes (e.g., '{"role": "admin"}').""",
)
@click.option("--profile", default="default", help="The profile to use.")
def assign_app(user_identifier, app_identifier, profile_attributes, profile):
    """Assigns a user to an application with optional profile attributes (accepts names or IDs)."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    # Resolve identifiers to IDs
    user_id = resolve_user_id(user_identifier, domain, token)
    if not user_id:
        click.echo(f"Error: User not found with identifier '{user_identifier}'")
        return

    app_id = resolve_app_id(app_identifier, domain, token)
    if not app_id:
        click.echo(f"Error: Application not found with identifier '{app_identifier}'")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    data = {"id": user_id}
    if profile_attributes:
        try:
            data["profile"] = json.loads(profile_attributes)
        except json.JSONDecodeError:
            click.echo("Error: --profile-attributes must be a valid JSON string.")
            return

    response = requests.post(
        f"https://{domain}/api/v1/apps/{app_id}/users", headers=headers, json=data
    )

    if response.status_code == 200:
        click.echo("User assigned to application successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@users.command("unassign-app")
@click.argument("user_id")
@click.argument("app_id")
@click.option("--profile", default="default", help="The profile to use.")
def unassign_app(user_id, app_id, profile):
    """Unassigns a user from an application."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.delete(
        f"https://{domain}/api/v1/apps/{app_id}/users/{user_id}", headers=headers
    )

    if response.status_code == 204:
        click.echo("User unassigned from application successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@users.command("list-app-assignments")
@click.argument("app_id")
@click.option("--profile", default="default", help="The profile to use.")
def list_app_assignments(app_id, profile):
    """Lists users assigned to a specific application."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.get(
        f"https://{domain}/api/v1/apps/{app_id}/users", headers=headers
    )

    if response.status_code == 200:
        for assignment in response.json():
            click.echo(assignment["externalId"])
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@users.command("deactivate")
@click.argument("user_id")
@click.option("--profile", default="default", help="The profile to use.")
def deactivate_user(user_id, profile):
    """Deactivates a user in Okta."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"https://{domain}/api/v1/users/{user_id}/lifecycle/deactivate", headers=headers
    )

    if response.status_code == 200:
        click.echo("User deactivated successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@users.command("activate")
@click.argument("user_id")
@click.option("--profile", default="default", help="The profile to use.")
def activate_user(user_id, profile):
    """Activates a user in Okta."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"https://{domain}/api/v1/users/{user_id}/lifecycle/activate", headers=headers
    )

    if response.status_code == 200:
        click.echo("User activated successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@users.command("reset-password")
@click.argument("user_id")
@click.option("--profile", default="default", help="The profile to use.")
def reset_password(user_id, profile):
    """Resets a user's password in Okta and returns a temporary password."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"https://{domain}/api/v1/users/{user_id}/lifecycle/expire_password",
        headers=headers,
        json={"tempPassword": True},
    )

    if response.status_code == 200:
        temp_password = response.json().get("tempPassword")
        if temp_password:
            click.echo(f"Temporary password for user {user_id}: {temp_password}")
        else:
            click.echo(
                f"Password reset initiated for user {user_id}. No temporary password returned."
            )
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")
