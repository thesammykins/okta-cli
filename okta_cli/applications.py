"""
Application management commands for the Okta CLI tool.
"""

import click
import requests
import json
from typing import Dict, Any, List, Optional
from .errors import (
    handle_api_error,
    handle_network_error,
    handle_json_error,
    handle_config_error,
    handle_corrupted_config,
    with_error_handling,
    validate_name,
)
from .enhanced_config import get_effective_config
from .formatting import create_output_option, format_and_output
from .progress import progress_spinner


@click.group()
def applications():
    """Manage Okta applications."""
    pass


@applications.command("list")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option(
    "--limit", type=int, default=20, help="Number of applications to retrieve."
)
@click.option("--filter", help='Filter applications (e.g., "status eq "ACTIVE"").')
@create_output_option()
@with_error_handling
def list_applications(profile, limit, filter, output):
    """List applications in Okta."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"limit": limit}
    if filter:
        params["filter"] = filter

    with progress_spinner("Fetching applications from Okta API..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/apps",
                headers=headers,
                params=params,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            apps_data = response.json()

            if output == "table":
                # Format for table display
                formatted_apps = []
                for app in apps_data:
                    formatted_apps.append(
                        {
                            "ID": app.get("id", ""),
                            "Name": app.get("name", ""),
                            "Label": app.get("label", ""),
                            "Status": app.get("status", ""),
                            "Created": app.get("created", ""),
                            "Last Updated": app.get("lastUpdated", ""),
                        }
                    )

                headers = ["ID", "Name", "Label", "Status", "Created", "Last Updated"]
                format_and_output(formatted_apps, output, "generic", headers)
            else:
                format_and_output(apps_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@applications.command("show")
@click.argument("app_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@create_output_option()
@with_error_handling
def show_application(app_id, profile, output):
    """Show details for a specific application."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Fetching application details..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/apps/{app_id}", headers=headers, timeout=30
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            app_data = response.json()

            if output == "table":
                # Format for table display
                formatted_app = {
                    "ID": app_data.get("id", ""),
                    "Name": app_data.get("name", ""),
                    "Label": app_data.get("label", ""),
                    "Status": app_data.get("status", ""),
                    "Sign On Mode": app_data.get("signOnMode", ""),
                    "Created": app_data.get("created", ""),
                    "Last Updated": app_data.get("lastUpdated", ""),
                    "Features": ", ".join(app_data.get("features", [])),
                    "Accessibility": str(app_data.get("accessibility", {})),
                }
                format_and_output(formatted_app, output, "generic")
            else:
                format_and_output(app_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@applications.command("create")
@click.option("--name", required=True, help="Application name.")
@click.option("--label", required=True, help="Application label.")
@click.option(
    "--sign-on-mode",
    type=click.Choice(
        [
            "BOOKMARK",
            "BASIC_AUTH",
            "BROWSER_PLUGIN",
            "SECURE_PASSWORD_STORE",
            "SAML_2_0",
            "WS_FEDERATION",
            "AUTO_LOGIN",
            "OPENID_CONNECT",
        ]
    ),
    default="BOOKMARK",
    help="Sign-on mode.",
)
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@create_output_option()
@with_error_handling
def create_application(name, label, sign_on_mode, profile, output):
    """Create a new application in Okta."""
    # Validate input
    validate_name(name, "Application name")
    validate_name(label, "Application label")

    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    data = {"name": name, "label": label, "signOnMode": sign_on_mode}

    with progress_spinner("Creating application in Okta..."):
        try:
            response = requests.post(
                f"https://{domain}/api/v1/apps", headers=headers, json=data, timeout=30
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            app_data = response.json()

            click.echo(click.style("✅ Application created successfully!", fg="green"))

            if output == "table":
                formatted_app = {
                    "ID": app_data.get("id", ""),
                    "Name": app_data.get("name", ""),
                    "Label": app_data.get("label", ""),
                    "Status": app_data.get("status", ""),
                    "Sign On Mode": app_data.get("signOnMode", ""),
                    "Created": app_data.get("created", ""),
                }
                format_and_output(formatted_app, output, "generic")
            else:
                format_and_output(app_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@applications.command("update")
@click.argument("app_id")
@click.option("--name", help="New application name.")
@click.option("--label", help="New application label.")
@click.option(
    "--status", type=click.Choice(["ACTIVE", "INACTIVE"]), help="Application status."
)
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@create_output_option()
@with_error_handling
def update_application(app_id, name, label, status, profile, output):
    """Update an existing application in Okta."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    data = {}
    if name:
        validate_name(name, "Application name")
        data["name"] = name
    if label:
        validate_name(label, "Application label")
        data["label"] = label
    if status:
        data["status"] = status

    if not data:
        click.echo(
            "No update parameters provided. Please provide at least one of --name, --label, or --status."
        )
        return

    with progress_spinner("Updating application in Okta..."):
        try:
            response = requests.put(
                f"https://{domain}/api/v1/apps/{app_id}",
                headers=headers,
                json=data,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            app_data = response.json()

            click.echo(click.style("✅ Application updated successfully!", fg="green"))

            if output == "table":
                formatted_app = {
                    "ID": app_data.get("id", ""),
                    "Name": app_data.get("name", ""),
                    "Label": app_data.get("label", ""),
                    "Status": app_data.get("status", ""),
                    "Sign On Mode": app_data.get("signOnMode", ""),
                    "Last Updated": app_data.get("lastUpdated", ""),
                }
                format_and_output(formatted_app, output, "generic")
            else:
                format_and_output(app_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@applications.command("delete")
@click.argument("app_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option("--force", is_flag=True, help="Force deletion without confirmation.")
@with_error_handling
def delete_application(app_id, profile, force):
    """Delete an application from Okta."""
    if not force:
        if not click.confirm(
            f"Are you sure you want to delete application '{app_id}'?"
        ):
            click.echo("Application deletion cancelled.")
            return

    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Deleting application from Okta..."):
        try:
            response = requests.delete(
                f"https://{domain}/api/v1/apps/{app_id}", headers=headers, timeout=30
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 204:
        click.echo(click.style("✅ Application deleted successfully!", fg="green"))
    else:
        handle_api_error(response)


@applications.command("activate")
@click.argument("app_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@with_error_handling
def activate_application(app_id, profile):
    """Activate an application in Okta."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Activating application in Okta..."):
        try:
            response = requests.post(
                f"https://{domain}/api/v1/apps/{app_id}/lifecycle/activate",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        click.echo(click.style("✅ Application activated successfully!", fg="green"))
    else:
        handle_api_error(response)


@applications.command("deactivate")
@click.argument("app_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@with_error_handling
def deactivate_application(app_id, profile):
    """Deactivate an application in Okta."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Deactivating application in Okta..."):
        try:
            response = requests.post(
                f"https://{domain}/api/v1/apps/{app_id}/lifecycle/deactivate",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        click.echo(click.style("✅ Application deactivated successfully!", fg="green"))
    else:
        handle_api_error(response)


@applications.command("list-users")
@click.argument("app_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option("--limit", type=int, default=20, help="Number of users to retrieve.")
@create_output_option()
@with_error_handling
def list_app_users(app_id, profile, limit, output):
    """List users assigned to an application."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"limit": limit}

    with progress_spinner("Fetching application users from Okta API..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/apps/{app_id}/users",
                headers=headers,
                params=params,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            users_data = response.json()

            if output == "table":
                # Format for table display
                formatted_users = []
                for user in users_data:
                    formatted_users.append(
                        {
                            "ID": user.get("id", ""),
                            "Username": user.get("credentials", {}).get("userName", ""),
                            "Status": user.get("status", ""),
                            "Created": user.get("created", ""),
                            "Last Updated": user.get("lastUpdated", ""),
                        }
                    )

                headers = ["ID", "Username", "Status", "Created", "Last Updated"]
                format_and_output(formatted_users, output, "generic", headers)
            else:
                format_and_output(users_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@applications.command("list-groups")
@click.argument("app_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option("--limit", type=int, default=20, help="Number of groups to retrieve.")
@create_output_option()
@with_error_handling
def list_app_groups(app_id, profile, limit, output):
    """List groups assigned to an application."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"limit": limit}

    with progress_spinner("Fetching application groups from Okta API..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/apps/{app_id}/groups",
                headers=headers,
                params=params,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            groups_data = response.json()

            if output == "table":
                # Format for table display
                formatted_groups = []
                for group in groups_data:
                    formatted_groups.append(
                        {
                            "ID": group.get("id", ""),
                            "Priority": group.get("priority", ""),
                            "Last Updated": group.get("lastUpdated", ""),
                        }
                    )

                headers = ["ID", "Priority", "Last Updated"]
                format_and_output(formatted_groups, output, "generic", headers)
            else:
                format_and_output(groups_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


if __name__ == "__main__":
    applications()
