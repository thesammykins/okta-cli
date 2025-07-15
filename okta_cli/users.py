import click
import requests
from . import config
import json

@click.group()
def users():
    """Manage Okta users."""
    pass

@users.command('list')
@click.option('--profile', default='default', help='The profile to use.')
def list_users(profile):
    """List users in Okta."""
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

    response = requests.get(f"https://{domain}/api/v1/users", headers=headers)

    if response.status_code == 200:
        for user in response.json():
            click.echo(user['profile']['login'])
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('create')
@click.option('--first-name', required=True)
@click.option('--last-name', required=True)
@click.option('--email', required=True)
@click.option('--login', required=True)
@click.option('--profile', default='default', help='The profile to use.')
def create_user(first_name, last_name, email, login, profile):
    """Create a new user in Okta."""
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

    data = {
        "profile": {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "login": login,
        }
    }

    response = requests.post(f"https://{domain}/api/v1/users?activate=false", headers=headers, json=data)

    if response.status_code == 200:
        user = response.json()
        click.echo("User created successfully:")
        click.echo(user['profile']['login'])
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('show')
@click.argument('user_id')
@click.option('--profile', default='default', help='The profile to use.')
def show_user(user_id, profile):
    """Show details for a specific user."""
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

    response = requests.get(f"https://{domain}/api/v1/users/{user_id}", headers=headers)

    if response.status_code == 200:
        click.echo(json.dumps(response.json(), indent=4))
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('suspend')
@click.argument('user_id')
@click.option('--profile', default='default', help='The profile to use.')
def suspend_user(user_id, profile):
    """Suspend a user in Okta."""
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

    response = requests.post(f"https://{domain}/api/v1/users/{user_id}/lifecycle/suspend", headers=headers)

    if response.status_code == 200:
        click.echo("User suspended successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('unsuspend')
@click.argument('user_id')
@click.option('--profile', default='default', help='The profile to use.')
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

    response = requests.post(f"https://{domain}/api/v1/users/{user_id}/lifecycle/unsuspend", headers=headers)

    if response.status_code == 200:
        click.echo("User unsuspended successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('update')
@click.argument('user_id')
@click.option('--first-name', help='User\'s first name.')
@click.option('--last-name', help='User\'s last name.')
@click.option('--email', help='User\'s email address.')
@click.option('--login', help='User\'s login name.')
@click.option('--profile', default='default', help='The profile to use.')
def update_user(user_id, first_name, last_name, email, login, profile):
    """Update a user's profile in Okta."""
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

    profile_data = {}
    if first_name: profile_data["firstName"] = first_name
    if last_name: profile_data["lastName"] = last_name
    if email: profile_data["email"] = email
    if login: profile_data["login"] = login

    if not profile_data:
        click.echo("No update parameters provided. Please provide at least one of --first-name, --last-name, --email, or --login.")
        return

    data = {"profile": profile_data}

    response = requests.post(f"https://{domain}/api/v1/users/{user_id}", headers=headers, json=data)

    if response.status_code == 200:
        user = response.json()
        click.echo("User updated successfully:")
        click.echo(json.dumps(user['profile'], indent=4))
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('assign-app')
@click.argument('user_id')
@click.argument('app_id')
@click.option('--profile-attributes', help='''JSON string of profile attributes (e.g., '{"role": "admin"}').''')
@click.option('--profile', default='default', help='The profile to use.')
def assign_app(user_id, app_id, profile_attributes, profile):
    """Assigns a user to an application with optional profile attributes."""
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

    data = {"id": user_id}
    if profile_attributes:
        try:
            data["profile"] = json.loads(profile_attributes)
        except json.JSONDecodeError:
            click.echo("Error: --profile-attributes must be a valid JSON string.")
            return

    response = requests.post(f"https://{domain}/api/v1/apps/{app_id}/assignments", headers=headers, json=data)

    if response.status_code == 200:
        click.echo("User assigned to application successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('unassign-app')
@click.argument('user_id')
@click.argument('app_id')
@click.option('--profile', default='default', help='The profile to use.')
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

    response = requests.delete(f"https://{domain}/api/v1/apps/{app_id}/assignments/{user_id}", headers=headers)

    if response.status_code == 204:
        click.echo("User unassigned from application successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('list-app-assignments')
@click.argument('app_id')
@click.option('--profile', default='default', help='The profile to use.')
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

    response = requests.get(f"https://{domain}/api/v1/apps/{app_id}/assignments", headers=headers)

    if response.status_code == 200:
        for assignment in response.json():
            click.echo(assignment['externalId'])
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('deactivate')
@click.argument('user_id')
@click.option('--profile', default='default', help='The profile to use.')
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

    response = requests.post(f"https://{domain}/api/v1/users/{user_id}/lifecycle/deactivate", headers=headers)

    if response.status_code == 200:
        click.echo("User deactivated successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('activate')
@click.argument('user_id')
@click.option('--profile', default='default', help='The profile to use.')
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

    response = requests.post(f"https://{domain}/api/v1/users/{user_id}/lifecycle/activate", headers=headers)

    if response.status_code == 200:
        click.echo("User activated successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")

@users.command('reset-password')
@click.argument('user_id')
@click.option('--profile', default='default', help='The profile to use.')
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

    response = requests.post(f"https://{domain}/api/v1/users/{user_id}/lifecycle/expire_password", headers=headers, json={"tempPassword": True})

    if response.status_code == 200:
        temp_password = response.json().get('tempPassword')
        if temp_password:
            click.echo(f"Temporary password for user {user_id}: {temp_password}")
        else:
            click.echo(f"Password reset initiated for user {user_id}. No temporary password returned.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")