"""
Group rules and policies management for the Okta CLI tool.
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
def policies():
    """Manage Okta policies and group rules."""
    pass


@policies.command("list")
@click.option(
    "--type",
    "policy_type",
    type=click.Choice(
        [
            "OKTA_SIGN_ON",
            "PASSWORD",
            "MFA_ENROLL",
            "ACCESS_POLICY",
            "PROFILE_ENROLLMENT",
            "OAUTH_AUTHORIZATION_POLICY",
        ]
    ),
    required=True,
    help="Filter policies by type (required).",
)
@click.option("--profile", default=None, help="The profile to use.")
@click.option("--limit", type=int, default=20, help="Number of policies to retrieve.")
@create_output_option()
@with_error_handling
def list_policies(policy_type, profile, limit, output):
    """List policies in Okta."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"limit": limit, "type": policy_type}

    with progress_spinner("Fetching policies from Okta API..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/policies",
                headers=headers,
                params=params,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            policies_data = response.json()

            if output == "table":
                # Format for table display
                formatted_policies = []
                for policy in policies_data:
                    formatted_policies.append(
                        {
                            "ID": policy.get("id", ""),
                            "Name": policy.get("name", ""),
                            "Type": policy.get("type", ""),
                            "Status": policy.get("status", ""),
                            "Priority": policy.get("priority", ""),
                            "Created": policy.get("created", ""),
                            "Last Updated": policy.get("lastUpdated", ""),
                        }
                    )

                headers = [
                    "ID",
                    "Name",
                    "Type",
                    "Status",
                    "Priority",
                    "Created",
                    "Last Updated",
                ]
                format_and_output(formatted_policies, output, "generic", headers)
            else:
                format_and_output(policies_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@policies.command("show")
@click.argument("policy_id")
@click.option("--profile", default=None, help="The profile to use.")
@create_output_option()
@with_error_handling
def show_policy(policy_id, profile, output):
    """Show details for a specific policy."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Fetching policy details..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/policies/{policy_id}",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            policy_data = response.json()

            if output == "table":
                # Format for table display
                formatted_policy = {
                    "ID": policy_data.get("id", ""),
                    "Name": policy_data.get("name", ""),
                    "Type": policy_data.get("type", ""),
                    "Status": policy_data.get("status", ""),
                    "Priority": policy_data.get("priority", ""),
                    "Description": policy_data.get("description", ""),
                    "Created": policy_data.get("created", ""),
                    "Last Updated": policy_data.get("lastUpdated", ""),
                    "Conditions": str(policy_data.get("conditions", {})),
                    "Settings": str(policy_data.get("settings", {})),
                }
                format_and_output(formatted_policy, output, "generic")
            else:
                format_and_output(policy_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@policies.command("activate")
@click.argument("policy_id")
@click.option("--profile", default=None, help="The profile to use.")
@with_error_handling
def activate_policy(policy_id, profile):
    """Activate a policy."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Activating policy..."):
        try:
            response = requests.post(
                f"https://{domain}/api/v1/policies/{policy_id}/lifecycle/activate",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        click.echo(click.style("✅ Policy activated successfully!", fg="green"))
    else:
        handle_api_error(response)


@policies.command("deactivate")
@click.argument("policy_id")
@click.option("--profile", default=None, help="The profile to use.")
@with_error_handling
def deactivate_policy(policy_id, profile):
    """Deactivate a policy."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Deactivating policy..."):
        try:
            response = requests.post(
                f"https://{domain}/api/v1/policies/{policy_id}/lifecycle/deactivate",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        click.echo(click.style("✅ Policy deactivated successfully!", fg="green"))
    else:
        handle_api_error(response)


@policies.group("rules")
def group_rules():
    """Manage group rules."""
    pass


@group_rules.command("list")
@click.option("--profile", default=None, help="The profile to use.")
@click.option(
    "--limit", type=int, default=20, help="Number of group rules to retrieve."
)
@create_output_option()
@with_error_handling
def list_group_rules(profile, limit, output):
    """List group rules in Okta."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"limit": limit}

    with progress_spinner("Fetching group rules from Okta API..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/groups/rules",
                headers=headers,
                params=params,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            rules_data = response.json()

            if output == "table":
                # Format for table display
                formatted_rules = []
                for rule in rules_data:
                    formatted_rules.append(
                        {
                            "ID": rule.get("id", ""),
                            "Name": rule.get("name", ""),
                            "Type": rule.get("type", ""),
                            "Status": rule.get("status", ""),
                            "Created": rule.get("created", ""),
                            "Last Updated": rule.get("lastUpdated", ""),
                            "Conditions": str(rule.get("conditions", {})),
                        }
                    )

                headers = [
                    "ID",
                    "Name",
                    "Type",
                    "Status",
                    "Created",
                    "Last Updated",
                    "Conditions",
                ]
                format_and_output(formatted_rules, output, "generic", headers)
            else:
                format_and_output(rules_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@group_rules.command("show")
@click.argument("rule_id")
@click.option("--profile", default=None, help="The profile to use.")
@create_output_option()
@with_error_handling
def show_group_rule(rule_id, profile, output):
    """Show details for a specific group rule."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Fetching group rule details..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/groups/rules/{rule_id}",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            rule_data = response.json()

            if output == "table":
                # Format for table display
                formatted_rule = {
                    "ID": rule_data.get("id", ""),
                    "Name": rule_data.get("name", ""),
                    "Type": rule_data.get("type", ""),
                    "Status": rule_data.get("status", ""),
                    "Created": rule_data.get("created", ""),
                    "Last Updated": rule_data.get("lastUpdated", ""),
                    "Conditions": str(rule_data.get("conditions", {})),
                    "Actions": str(rule_data.get("actions", {})),
                }
                format_and_output(formatted_rule, output, "generic")
            else:
                format_and_output(rule_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@group_rules.command("create")
@click.option("--name", required=True, help="Group rule name.")
@click.option(
    "--type",
    "rule_type",
    type=click.Choice(["group_rule"]),
    default="group_rule",
    help="Rule type.",
)
@click.option(
    "--expression",
    required=True,
    help='Expression to match users (e.g., "user.department=="Engineering"").',
)
@click.option("--group-id", required=True, help="ID of the group to assign users to.")
@click.option("--profile", default=None, help="The profile to use.")
@create_output_option()
@with_error_handling
def create_group_rule(name, rule_type, expression, group_id, profile, output):
    """Create a new group rule."""
    validate_name(name, "Rule name")

    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    data = {
        "type": rule_type,
        "name": name,
        "conditions": {
            "expression": {"value": expression, "type": "urn:okta:expression:1.0"}
        },
        "actions": {"assignUserToGroups": {"groupIds": [group_id]}},
    }

    with progress_spinner("Creating group rule..."):
        try:
            response = requests.post(
                f"https://{domain}/api/v1/groups/rules",
                headers=headers,
                json=data,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            rule_data = response.json()

            click.echo(click.style("✅ Group rule created successfully!", fg="green"))

            if output == "table":
                formatted_rule = {
                    "ID": rule_data.get("id", ""),
                    "Name": rule_data.get("name", ""),
                    "Type": rule_data.get("type", ""),
                    "Status": rule_data.get("status", ""),
                    "Created": rule_data.get("created", ""),
                    "Expression": expression,
                    "Group ID": group_id,
                }
                format_and_output(formatted_rule, output, "generic")
            else:
                format_and_output(rule_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@group_rules.command("update")
@click.argument("rule_id")
@click.option("--name", help="New rule name.")
@click.option("--expression", help="New expression to match users.")
@click.option("--group-id", help="New group ID to assign users to.")
@click.option("--profile", default=None, help="The profile to use.")
@create_output_option()
@with_error_handling
def update_group_rule(rule_id, name, expression, group_id, profile, output):
    """Update an existing group rule."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Get current rule data first
    with progress_spinner("Fetching current rule data..."):
        try:
            current_response = requests.get(
                f"https://{domain}/api/v1/groups/rules/{rule_id}",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if current_response.status_code != 200:
        handle_api_error(current_response)
        return

    try:
        current_data = current_response.json()
    except (ValueError, KeyError) as e:
        handle_json_error(e, current_response.text)
        return

    # Update data with new values
    data = current_data.copy()

    if name:
        validate_name(name, "Rule name")
        data["name"] = name

    if expression:
        data["conditions"]["expression"]["value"] = expression

    if group_id:
        data["actions"]["assignUserToGroups"]["groupIds"] = [group_id]

    with progress_spinner("Updating group rule..."):
        try:
            response = requests.put(
                f"https://{domain}/api/v1/groups/rules/{rule_id}",
                headers=headers,
                json=data,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            rule_data = response.json()

            click.echo(click.style("✅ Group rule updated successfully!", fg="green"))

            if output == "table":
                formatted_rule = {
                    "ID": rule_data.get("id", ""),
                    "Name": rule_data.get("name", ""),
                    "Type": rule_data.get("type", ""),
                    "Status": rule_data.get("status", ""),
                    "Last Updated": rule_data.get("lastUpdated", ""),
                    "Expression": rule_data.get("conditions", {})
                    .get("expression", {})
                    .get("value", ""),
                    "Group IDs": ", ".join(
                        rule_data.get("actions", {})
                        .get("assignUserToGroups", {})
                        .get("groupIds", [])
                    ),
                }
                format_and_output(formatted_rule, output, "generic")
            else:
                format_and_output(rule_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@group_rules.command("delete")
@click.argument("rule_id")
@click.option("--profile", default=None, help="The profile to use.")
@click.option("--force", is_flag=True, help="Force deletion without confirmation.")
@with_error_handling
def delete_group_rule(rule_id, profile, force):
    """Delete a group rule."""
    if not force:
        if not click.confirm(
            f"Are you sure you want to delete group rule '{rule_id}'?"
        ):
            click.echo("Group rule deletion cancelled.")
            return

    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Deleting group rule..."):
        try:
            response = requests.delete(
                f"https://{domain}/api/v1/groups/rules/{rule_id}",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 202:
        click.echo(click.style("✅ Group rule deleted successfully!", fg="green"))
    else:
        handle_api_error(response)


@group_rules.command("activate")
@click.argument("rule_id")
@click.option("--profile", default=None, help="The profile to use.")
@with_error_handling
def activate_group_rule(rule_id, profile):
    """Activate a group rule."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Activating group rule..."):
        try:
            response = requests.post(
                f"https://{domain}/api/v1/groups/rules/{rule_id}/lifecycle/activate",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        click.echo(click.style("✅ Group rule activated successfully!", fg="green"))
    else:
        handle_api_error(response)


@group_rules.command("deactivate")
@click.argument("rule_id")
@click.option("--profile", default=None, help="The profile to use.")
@with_error_handling
def deactivate_group_rule(rule_id, profile):
    """Deactivate a group rule."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Deactivating group rule..."):
        try:
            response = requests.post(
                f"https://{domain}/api/v1/groups/rules/{rule_id}/lifecycle/deactivate",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        click.echo(click.style("✅ Group rule deactivated successfully!", fg="green"))
    else:
        handle_api_error(response)


if __name__ == "__main__":
    policies()
