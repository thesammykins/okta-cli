import click
import requests
from . import config
import json
from .utils import resolve_user_id, resolve_group_id, get_group_by_identifier


@click.group()
def groups():
    """Manage Okta groups."""
    pass


@groups.command("list")
@click.option("--profile", default="default", help="The profile to use.")
def list_groups(profile):
    """List groups in Okta."""
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

    response = requests.get(f"https://{domain}/api/v1/groups", headers=headers)

    if response.status_code == 200:
        for group in response.json():
            click.echo(group["profile"]["name"])
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@groups.command("create")
@click.option("--name", required=True, help="The name of the group.")
@click.option("--description", help="The description of the group.")
@click.option("--profile", default="default", help="The profile to use.")
def create_group(name, description, profile):
    """Create a new group in Okta."""
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
@click.option("--profile", default="default", help="The profile to use.")
def show_group(group_identifier, profile):
    """Show details for a specific group (accepts ID or name)."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

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
@click.option("--profile", default="default", help="The profile to use.")
def update_group(group_id, name, description, profile):
    """Update a group's profile in Okta."""
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
@click.option("--profile", default="default", help="The profile to use.")
def delete_group(group_id, profile):
    """Delete a group in Okta."""
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
        f"https://{domain}/api/v1/groups/{group_id}", headers=headers
    )

    if response.status_code == 204:
        click.echo("Group deleted successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@groups.command("add-user")
@click.argument("group_identifier")
@click.argument("user_identifier")
@click.option("--profile", default="default", help="The profile to use.")
def add_user_to_group(group_identifier, user_identifier, profile):
    """Adds a user to a group in Okta (accepts names or IDs)."""
    cfg = config.get_config()
    if not cfg.has_section(profile):
        click.echo(f"Profile '{profile}' not found. Please run `okta-cli configure`.")
        return

    domain = cfg.get(profile, "domain")
    token = cfg.get(profile, "token")

    # Resolve identifiers to IDs
    group_id = resolve_group_id(group_identifier, domain, token)
    if not group_id:
        click.echo(f"Error: Group not found with identifier '{group_identifier}'")
        return

    user_id = resolve_user_id(user_identifier, domain, token)
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
@click.argument("group_id")
@click.argument("user_id")
@click.option("--profile", default="default", help="The profile to use.")
def remove_user_from_group(group_id, user_id, profile):
    """Removes a user from a group in Okta."""
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
        f"https://{domain}/api/v1/groups/{group_id}/users/{user_id}", headers=headers
    )

    if response.status_code == 204:
        click.echo("User removed from group successfully.")
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")


@groups.command("list-members")
@click.argument("group_id")
@click.option("--profile", default="default", help="The profile to use.")
def list_group_members(group_id, profile):
    """Lists members of a group in Okta."""
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
        f"https://{domain}/api/v1/groups/{group_id}/users", headers=headers
    )

    if response.status_code == 200:
        for user in response.json():
            click.echo(user["profile"]["login"])
    else:
        click.echo(f"Error: {response.status_code} - {response.text}")
