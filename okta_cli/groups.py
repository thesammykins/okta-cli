import click
import requests
from .enhanced_config import get_effective_config
import json
from .utils import resolve_user_id, resolve_group_id, get_group_by_identifier
from .errors import ConfigurationError, handle_config_error, ResolutionError


@click.group()
def groups():
    """Manage Okta groups."""
    pass


@groups.command("list")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
def list_groups(profile):
    """List groups in Okta."""
    try:
        domain, token = get_effective_config(profile)
    except ConfigurationError:
        handle_config_error(profile or "default")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.get(f"https://{domain}/api/v1/groups", headers=headers)

    if response.status_code == 200:
        for group in response.json():
            click.echo(group["profile"]["name"])
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@groups.command("create")
@click.option("--name", required=True, help="The name of the group.")
@click.option("--description", help="The description of the group.")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
def create_group(name, description, profile):
    """Create a new group in Okta."""
    try:
        domain, token = get_effective_config(profile)
    except ConfigurationError:
        handle_config_error(profile or "default")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    data = {"profile": {"name": name, "description": description}}

    response = requests.post(
        f"https://{domain}/api/v1/groups", headers=headers, json=data
    )

    if response.status_code == 200:
        group = response.json()
        click.echo("Group created successfully:")
        click.echo(group["profile"]["name"])
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@groups.command("show")
@click.argument("group_identifier")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
def show_group(group_identifier, profile):
    """Show details for a specific group (accepts ID or name)."""
    try:
        domain, token = get_effective_config(profile)
    except ConfigurationError:
        handle_config_error(profile or "default")
        return

    # Try to get group by identifier (ID or name)
    group = get_group_by_identifier(group_identifier, domain, token)

    if group:
        click.echo(json.dumps(group, indent=4))
    else:
        click.echo(f"Error: Group not found with identifier '{group_identifier}'")


@groups.command("update")
@click.argument("group_id")
@click.option("--name", help="The new name of the group.")
@click.option("--description", help="The new description of the group.")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
def update_group(group_id, name, description, profile):
    """Update a group's profile in Okta."""
    try:
        domain, token = get_effective_config(profile)
    except ConfigurationError:
        handle_config_error(profile or "default")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    profile_data = {}
    if name:
        profile_data["name"] = name
    if description:
        profile_data["description"] = description

    if not profile_data:
        click.echo(
            "No update parameters provided. Please provide at least one of --name or --description."
        )
        return

    data = {"profile": profile_data}

    response = requests.put(
        f"https://{domain}/api/v1/groups/{group_id}", headers=headers, json=data
    )

    if response.status_code == 200:
        group = response.json()
        click.echo("Group updated successfully:")
        click.echo(json.dumps(group["profile"], indent=4))
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@groups.command("delete")
@click.argument("group_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
def delete_group(group_id, profile):
    """Delete a group in Okta."""
    try:
        domain, token = get_effective_config(profile)
    except ConfigurationError:
        handle_config_error(profile or "default")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.delete(
        f"https://{domain}/api/v1/groups/{group_id}", headers=headers
    )

    if response.status_code == 204:
        click.echo("Group deleted successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@groups.command("add-user")
@click.argument("group_identifier")
@click.argument("user_identifier")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option("--debug", is_flag=True, help="Enable debug output for troubleshooting.")
def add_user_to_group(group_identifier, user_identifier, profile, debug):
    """Adds a user to a group in Okta (accepts names or IDs)."""
    try:
        domain, token = get_effective_config(profile)
    except ConfigurationError:
        handle_config_error(profile or "default")
        return

    # Resolve identifiers to IDs with improved error handling
    try:
        group_id = resolve_group_id(group_identifier, domain, token, debug=debug, raise_on_failure=True)
    except ResolutionError as e:
        click.echo(f"Error: {e}")
        return

    user_id = resolve_user_id(user_identifier, domain, token, debug=debug)
    if not user_id:
        click.echo(f"Error: User not found with identifier '{user_identifier}'")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.put(
        f"https://{domain}/api/v1/groups/{group_id}/users/{user_id}", headers=headers
    )

    if response.status_code == 204:
        click.echo("User added to group successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@groups.command("remove-user")
@click.argument("group_identifier")
@click.argument("user_identifier")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option("--debug", is_flag=True, help="Enable debug output for troubleshooting.")
def remove_user_from_group(group_identifier, user_identifier, profile, debug):
    """Removes a user from a group in Okta (accepts names or IDs)."""
    try:
        domain, token = get_effective_config(profile)
    except ConfigurationError:
        handle_config_error(profile or "default")
        return

    # Resolve identifiers to IDs with improved error handling
    try:
        group_id = resolve_group_id(group_identifier, domain, token, debug=debug, raise_on_failure=True)
    except ResolutionError as e:
        click.echo(f"Error: {e}")
        return

    user_id = resolve_user_id(user_identifier, domain, token, debug=debug)
    if not user_id:
        click.echo(f"Error: User not found with identifier '{user_identifier}'")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if debug:
        click.echo(f"[DEBUG] Removing user {user_id} from group {group_id}")

    response = requests.delete(
        f"https://{domain}/api/v1/groups/{group_id}/users/{user_id}", headers=headers
    )

    if response.status_code == 204:
        click.echo("User removed from group successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@groups.command("list-members")
@click.argument("group_identifier")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option("--debug", is_flag=True, help="Enable debug output for troubleshooting.")
def list_group_members(group_identifier, profile, debug):
    """Lists members of a group in Okta (accepts group name or ID)."""
    try:
        domain, token = get_effective_config(profile)
    except ConfigurationError:
        handle_config_error(profile or "default")
        return

    # Resolve group identifier to ID with improved error handling
    try:
        group_id = resolve_group_id(group_identifier, domain, token, debug=debug, raise_on_failure=True)
    except ResolutionError as e:
        click.echo(f"Error: {e}")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if debug:
        click.echo(f"[DEBUG] Fetching members for group ID: {group_id}")
    
    response = requests.get(
        f"https://{domain}/api/v1/groups/{group_id}/users", headers=headers
    )

    if response.status_code == 200:
        users = response.json()
        if debug:
            click.echo(f"[DEBUG] Found {len(users)} group members")
        for user in users:
            click.echo(user["profile"]["login"])
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")
