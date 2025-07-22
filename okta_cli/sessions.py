"""
User session management commands for the Okta CLI tool.
"""

import click
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .errors import (
    handle_api_error,
    handle_network_error,
    handle_json_error,
    handle_config_error,
    handle_corrupted_config,
    with_error_handling,
)
from .enhanced_config import get_effective_config
from .formatting import create_output_option, format_and_output
from .progress import progress_spinner



@click.group()
def sessions():
    """Manage user sessions in Okta."""
    pass


@sessions.command("list")
@click.argument("user_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option("--limit", type=int, default=20, help="Number of sessions to retrieve.")
@create_output_option()
@with_error_handling
def list_sessions(user_id, profile, limit, output):
    """List active sessions for a user."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"limit": limit}

    with progress_spinner("Fetching user sessions from Okta API..."):
        try:
            # Note: /api/v1/users/{userId}/sessions is deprecated
            # For current user sessions, use /api/v1/sessions/me with session cookie
            # This endpoint requires an admin token to list sessions for any user
            response = requests.get(
                f"https://{domain}/api/v1/sessions",
                headers=headers,
                params=params,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            sessions_data = response.json()

            if output == "table":
                # Format for table display
                formatted_sessions = []
                for session in sessions_data:
                    formatted_sessions.append(
                        {
                            "ID": session.get("id", ""),
                            "User ID": session.get("userId", ""),
                            "Login": session.get("login", ""),
                            "Created": session.get("createdAt", ""),
                            "Expires": session.get("expiresAt", ""),
                            "Status": session.get("status", ""),
                            "Last Factor Verification": session.get(
                                "lastFactorVerification", ""
                            ),
                            "Last Password Verification": session.get(
                                "lastPasswordVerification", ""
                            ),
                        }
                    )

                headers = [
                    "ID",
                    "User ID",
                    "Login",
                    "Created",
                    "Expires",
                    "Status",
                    "Last Factor Verification",
                    "Last Password Verification",
                ]
                format_and_output(formatted_sessions, output, "generic", headers)
            else:
                format_and_output(sessions_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@sessions.command("show")
@click.argument("user_id")
@click.argument("session_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@create_output_option()
@with_error_handling
def show_session(user_id, session_id, profile, output):
    """Show details for a specific user session."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Fetching session details..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/users/{user_id}/sessions/{session_id}",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            session_data = response.json()

            if output == "table":
                # Format for table display
                formatted_session = {
                    "ID": session_data.get("id", ""),
                    "User ID": session_data.get("userId", ""),
                    "Login": session_data.get("login", ""),
                    "Created": session_data.get("createdAt", ""),
                    "Expires": session_data.get("expiresAt", ""),
                    "Status": session_data.get("status", ""),
                    "Last Factor Verification": session_data.get(
                        "lastFactorVerification", ""
                    ),
                    "Last Password Verification": session_data.get(
                        "lastPasswordVerification", ""
                    ),
                    "Authentication Method": session_data.get(
                        "authenticationMethod", ""
                    ),
                    "Identity Provider": session_data.get("idp", {}).get("type", ""),
                    "MFA Required": str(session_data.get("mfaActive", False)),
                }
                format_and_output(formatted_session, output, "generic")
            else:
                format_and_output(session_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@sessions.command("clear")
@click.argument("user_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option("--oauth-only", is_flag=True, help="Clear only OAuth sessions.")
@click.option("--force", is_flag=True, help="Force clearing without confirmation.")
@with_error_handling
def clear_sessions(user_id, profile, oauth_only, force):
    """Clear all sessions for a user."""
    if not force:
        session_type = "OAuth sessions" if oauth_only else "all sessions"
        if not click.confirm(
            f"Are you sure you want to clear {session_type} for user '{user_id}'?"
        ):
            click.echo("Session clearing cancelled.")
            return

    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {}
    if oauth_only:
        params["oauthTokens"] = "true"

    with progress_spinner("Clearing user sessions..."):
        try:
            response = requests.delete(
                f"https://{domain}/api/v1/users/{user_id}/sessions",
                headers=headers,
                params=params,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 204:
        session_type = "OAuth sessions" if oauth_only else "all sessions"
        click.echo(
            click.style(
                f"✅ {session_type.capitalize()} cleared successfully!", fg="green"
            )
        )
    else:
        handle_api_error(response)


@sessions.command("extend")
@click.argument("user_id")
@click.argument("session_id")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@create_output_option()
@with_error_handling
def extend_session(user_id, session_id, profile, output):
    """Extend a user session."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Extending user session..."):
        try:
            # Use the correct sessions refresh endpoint
            response = requests.post(
                f"https://{domain}/api/v1/sessions/{session_id}/lifecycle/refresh",
                headers=headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            session_data = response.json()

            click.echo(click.style("✅ Session extended successfully!", fg="green"))

            if output == "table":
                formatted_session = {
                    "ID": session_data.get("id", ""),
                    "User ID": session_data.get("userId", ""),
                    "Login": session_data.get("login", ""),
                    "Created": session_data.get("createdAt", ""),
                    "Expires": session_data.get("expiresAt", ""),
                    "Status": session_data.get("status", ""),
                }
                format_and_output(formatted_session, output, "generic")
            else:
                format_and_output(session_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@sessions.command("stats")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option(
    "--days",
    type=int,
    default=7,
    help="Number of days to look back for session statistics.",
)
@create_output_option()
@with_error_handling
def session_stats(profile, days, output):
    """Get session statistics across the organization."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    params = {
        "since": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "until": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "filter": 'eventType eq "user.session.start"',
    }

    with progress_spinner(f"Fetching session statistics for the last {days} days..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/logs",
                headers=headers,
                params=params,
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            logs_data = response.json()

            # Process session statistics
            stats = {
                "total_sessions": len(logs_data),
                "unique_users": len(
                    set(log.get("actor", {}).get("id", "") for log in logs_data)
                ),
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "average_sessions_per_day": (
                    round(len(logs_data) / days, 2) if days > 0 else 0
                ),
            }

            # Group by authentication method
            auth_methods = {}
            for log in logs_data:
                auth_context = log.get("authenticationContext", {})
                auth_method = auth_context.get("authenticationProvider", "Unknown")
                auth_methods[auth_method] = auth_methods.get(auth_method, 0) + 1

            stats["authentication_methods"] = auth_methods

            if output == "table":
                formatted_stats = {
                    "Total Sessions": stats["total_sessions"],
                    "Unique Users": stats["unique_users"],
                    "Date Range": stats["date_range"],
                    "Average Sessions Per Day": stats["average_sessions_per_day"],
                    "Authentication Methods": ", ".join(
                        [f"{k}: {v}" for k, v in auth_methods.items()]
                    ),
                }
                format_and_output(formatted_stats, output, "generic")
            else:
                format_and_output(stats, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@sessions.command("active")
@click.option("--profile", default=None, help="The profile to use (defaults to active profile).")
@click.option("--limit", type=int, default=100, help="Number of sessions to check.")
@create_output_option()
@with_error_handling
def active_sessions(profile, limit, output):
    """List currently active sessions across the organization."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Get active users first
    params = {"limit": limit, "filter": 'status eq "ACTIVE"'}

    with progress_spinner("Fetching active sessions..."):
        try:
            # Get active users
            users_response = requests.get(
                f"https://{domain}/api/v1/users",
                headers=headers,
                params=params,
                timeout=30,
            )

            if users_response.status_code != 200:
                handle_api_error(users_response)
                return

            users_data = users_response.json()
            active_sessions_data = []

            # Check sessions for each user (limited to first 20 users to avoid too many API calls)
            for user in users_data[:20]:
                user_id = user.get("id")
                if user_id:
                    try:
                        sessions_response = requests.get(
                            f"https://{domain}/api/v1/users/{user_id}/sessions",
                            headers=headers,
                            timeout=10,
                        )
                        if sessions_response.status_code == 200:
                            sessions = sessions_response.json()
                            for session in sessions:
                                session["user_profile"] = user.get("profile", {})
                                active_sessions_data.append(session)
                    except requests.exceptions.RequestException:
                        # Skip users with session fetch errors
                        continue

        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if output == "table":
        # Format for table display
        formatted_sessions = []
        for session in active_sessions_data:
            formatted_sessions.append(
                {
                    "User Login": session.get("user_profile", {}).get("login", ""),
                    "Session ID": session.get("id", ""),
                    "Created": session.get("createdAt", ""),
                    "Expires": session.get("expiresAt", ""),
                    "Status": session.get("status", ""),
                    "Last Activity": session.get("lastPasswordVerification", ""),
                }
            )

        headers = [
            "User Login",
            "Session ID",
            "Created",
            "Expires",
            "Status",
            "Last Activity",
        ]
        format_and_output(formatted_sessions, output, "generic", headers)
    else:
        format_and_output(active_sessions_data, output, "generic")


if __name__ == "__main__":
    sessions()
