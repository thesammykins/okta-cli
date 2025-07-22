"""
Event log querying commands for the Okta CLI tool.
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



def safe_nested_get(obj, *keys, default=""):
    """Safely get nested dictionary values, returning default if any key is None or missing."""
    current = obj
    for key in keys:
        if current is None:
            return default

        if isinstance(key, int):
            # Handle list indices
            if not isinstance(current, list) or key >= len(current):
                return default
            current = current[key]
        else:
            # Handle dictionary keys
            if not isinstance(current, dict):
                return default
            current = current.get(key)

    return current if current is not None and current != {} else default


@click.group()
def logs():
    """Query and analyze Okta event logs."""
    pass


@logs.command("list")
@click.option("--profile", default=None, help="The profile to use.")
@click.option(
    "--limit", type=int, default=100, help="Number of log events to retrieve."
)
@click.option("--since", help="Start date for log events (ISO 8601 format).")
@click.option("--until", help="End date for log events (ISO 8601 format).")
@click.option("--filter", help="Filter expression for log events.")
@click.option("--q", help="Search query for log events.")
@create_output_option()
@with_error_handling
def list_logs(profile, limit, since, until, filter, q, output):
    """List event logs from Okta."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"limit": limit}
    if since:
        params["since"] = since
    if until:
        params["until"] = until
    if filter:
        params["filter"] = filter
    if q:
        params["q"] = q

    with progress_spinner("Fetching event logs from Okta API..."):
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

            if output == "table":
                # Format for table display
                formatted_logs = []
                for log in logs_data:
                    actor = log.get("actor", {})
                    target = log.get("target", [{}])[0] if log.get("target") else {}

                    formatted_logs.append(
                        {
                            "UUID": log.get("uuid", ""),
                            "Published": log.get("published", ""),
                            "Event Type": log.get("eventType", ""),
                            "Actor": actor.get(
                                "displayName", actor.get("alternateId", "")
                            ),
                            "Target": target.get(
                                "displayName", target.get("alternateId", "")
                            ),
                            "Client": safe_nested_get(
                                log, "client", "userAgent", "browser"
                            ),
                            "Outcome": safe_nested_get(log, "outcome", "result"),
                            "City": safe_nested_get(
                                log, "client", "geographicalContext", "city"
                            ),
                            "Country": safe_nested_get(
                                log, "client", "geographicalContext", "country"
                            ),
                        }
                    )

                headers = [
                    "UUID",
                    "Published",
                    "Event Type",
                    "Actor",
                    "Target",
                    "Client",
                    "Outcome",
                    "City",
                    "Country",
                ]
                format_and_output(formatted_logs, output, "generic", headers)
            else:
                format_and_output(logs_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@logs.command("show")
@click.argument("log_id")
@click.option("--profile", default=None, help="The profile to use.")
@create_output_option()
@with_error_handling
def show_log(log_id, profile, output):
    """Show details for a specific log event."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Fetching log event details..."):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/logs/{log_id}", headers=headers, timeout=30
            )
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            log_data = response.json()

            # Handle case where API returns unexpected format
            if not isinstance(log_data, dict):
                raise ValueError(
                    f"Expected log object but got {type(log_data).__name__}"
                )

            if output == "table":
                # Format for table display
                actor = log_data.get("actor", {})
                target = (
                    log_data.get("target", [{}])[0] if log_data.get("target") else {}
                )
                client = log_data.get("client", {})

                formatted_log = {
                    "UUID": log_data.get("uuid", ""),
                    "Published": log_data.get("published", ""),
                    "Event Type": log_data.get("eventType", ""),
                    "Display Message": log_data.get("displayMessage", ""),
                    "Actor ID": actor.get("id", ""),
                    "Actor Name": actor.get("displayName", ""),
                    "Actor Type": actor.get("type", ""),
                    "Target ID": target.get("id", ""),
                    "Target Name": target.get("displayName", ""),
                    "Target Type": target.get("type", ""),
                    "Client IP": client.get("ipAddress", ""),
                    "User Agent": safe_nested_get(client, "userAgent", "rawUserAgent"),
                    "Outcome": safe_nested_get(log_data, "outcome", "result"),
                    "Outcome Reason": safe_nested_get(log_data, "outcome", "reason"),
                    "Request ID": (
                        safe_nested_get(log_data, "request", "ipChain", 0, "ip")
                        if log_data.get("request", {}).get("ipChain")
                        else ""
                    ),
                    "Transaction ID": safe_nested_get(log_data, "transaction", "id"),
                    "Version": log_data.get("version", ""),
                    "Severity": log_data.get("severity", ""),
                    "Legacy Event Type": log_data.get("legacyEventType", ""),
                }
                format_and_output(formatted_log, output, "generic")
            else:
                format_and_output(log_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@logs.command("search")
@click.option("--profile", default=None, help="The profile to use.")
@click.option("--event-type", help='Filter by event type (e.g., "user.session.start").')
@click.option("--actor", help="Filter by actor ID or display name.")
@click.option("--target", help="Filter by target ID or display name.")
@click.option(
    "--outcome",
    type=click.Choice(
        ["SUCCESS", "FAILURE", "SKIPPED", "ALLOW", "DENY", "CHALLENGE", "UNKNOWN"]
    ),
    help="Filter by outcome.",
)
@click.option("--days", type=int, default=7, help="Number of days to look back.")
@click.option(
    "--limit", type=int, default=100, help="Number of log events to retrieve."
)
@create_output_option()
@with_error_handling
def search_logs(profile, event_type, actor, target, outcome, days, limit, output):
    """Search event logs with filters."""
    domain, token = get_effective_config(profile)

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Build filter expression
    filters = []
    if event_type:
        filters.append(f'eventType eq "{event_type}"')
    if actor:
        filters.append(
            f'actor.alternateId eq "{actor}" or actor.displayName eq "{actor}"'
        )
    if target:
        filters.append(
            f'target.alternateId eq "{target}" or target.displayName eq "{target}"'
        )
    if outcome:
        filters.append(f'outcome.result eq "{outcome}"')

    filter_expr = " and ".join(filters) if filters else None

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    params = {
        "limit": limit,
        "since": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "until": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    if filter_expr:
        params["filter"] = filter_expr

    with progress_spinner(f"Searching event logs for the last {days} days..."):
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

            if output == "table":
                # Format for table display
                formatted_logs = []
                for log in logs_data:
                    actor_info = log.get("actor", {})
                    target_info = (
                        log.get("target", [{}])[0] if log.get("target") else {}
                    )

                    formatted_logs.append(
                        {
                            "Published": log.get("published", ""),
                            "Event Type": log.get("eventType", ""),
                            "Actor": actor_info.get(
                                "displayName", actor_info.get("alternateId", "")
                            ),
                            "Target": target_info.get(
                                "displayName", target_info.get("alternateId", "")
                            ),
                            "Outcome": safe_nested_get(log, "outcome", "result"),
                            "Client IP": safe_nested_get(log, "client", "ipAddress"),
                            "City": safe_nested_get(
                                log, "client", "geographicalContext", "city"
                            ),
                            "Country": safe_nested_get(
                                log, "client", "geographicalContext", "country"
                            ),
                        }
                    )

                headers = [
                    "Published",
                    "Event Type",
                    "Actor",
                    "Target",
                    "Outcome",
                    "Client IP",
                    "City",
                    "Country",
                ]
                format_and_output(formatted_logs, output, "generic", headers)
            else:
                format_and_output(logs_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@logs.command("stats")
@click.option("--profile", default=None, help="The profile to use.")
@click.option("--days", type=int, default=7, help="Number of days to analyze.")
@click.option("--event-type", help="Filter by specific event type.")
@create_output_option()
@with_error_handling
def log_stats(profile, days, event_type, output):
    """Get statistics about event logs."""
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
        "limit": 1000,  # Get more data for better statistics
        "since": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "until": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    if event_type:
        params["filter"] = f'eventType eq "{event_type}"'

    with progress_spinner(f"Analyzing event logs for the last {days} days..."):
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

            # Calculate statistics
            total_events = len(logs_data)

            # Count by event type
            event_types = {}
            outcomes = {}
            actors = {}
            clients = {}
            countries = {}

            for log in logs_data:
                # Event types
                event_type = log.get("eventType", "Unknown")
                event_types[event_type] = event_types.get(event_type, 0) + 1

                # Outcomes
                outcome = safe_nested_get(log, "outcome", "result", default="Unknown")
                outcomes[outcome] = outcomes.get(outcome, 0) + 1

                # Actors
                actor = safe_nested_get(log, "actor", "displayName", default="Unknown")
                actors[actor] = actors.get(actor, 0) + 1

                # Clients
                client = safe_nested_get(
                    log, "client", "userAgent", "browser", default="Unknown"
                )
                clients[client] = clients.get(client, 0) + 1

                # Countries
                country = safe_nested_get(
                    log, "client", "geographicalContext", "country", default="Unknown"
                )
                countries[country] = countries.get(country, 0) + 1

            # Sort by frequency
            top_event_types = sorted(
                event_types.items(), key=lambda x: x[1], reverse=True
            )[:10]
            top_outcomes = sorted(outcomes.items(), key=lambda x: x[1], reverse=True)[
                :10
            ]
            top_actors = sorted(actors.items(), key=lambda x: x[1], reverse=True)[:10]
            top_clients = sorted(clients.items(), key=lambda x: x[1], reverse=True)[:10]
            top_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[
                :10
            ]

            stats = {
                "total_events": total_events,
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "average_events_per_day": (
                    round(total_events / days, 2) if days > 0 else 0
                ),
                "top_event_types": dict(top_event_types),
                "outcomes": dict(top_outcomes),
                "top_actors": dict(top_actors),
                "top_clients": dict(top_clients),
                "top_countries": dict(top_countries),
            }

            if output == "table":
                formatted_stats = {
                    "Total Events": stats["total_events"],
                    "Date Range": stats["date_range"],
                    "Average Events Per Day": stats["average_events_per_day"],
                    "Top Event Types": ", ".join(
                        [
                            f"{k}: {v}"
                            for k, v in list(stats["top_event_types"].items())[:5]
                        ]
                    ),
                    "Outcomes": ", ".join(
                        [f"{k}: {v}" for k, v in stats["outcomes"].items()]
                    ),
                    "Top Actors": ", ".join(
                        [f"{k}: {v}" for k, v in list(stats["top_actors"].items())[:5]]
                    ),
                    "Top Countries": ", ".join(
                        [
                            f"{k}: {v}"
                            for k, v in list(stats["top_countries"].items())[:5]
                        ]
                    ),
                }
                format_and_output(formatted_stats, output, "generic")
            else:
                format_and_output(stats, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@logs.command("failed-logins")
@click.option("--profile", default=None, help="The profile to use.")
@click.option("--days", type=int, default=7, help="Number of days to look back.")
@click.option(
    "--limit", type=int, default=50, help="Number of failed login attempts to retrieve."
)
@create_output_option()
@with_error_handling
def failed_logins(profile, days, limit, output):
    """Get failed login attempts."""
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
        "limit": limit,
        "since": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "until": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "filter": 'eventType eq "user.authentication.auth_via_mfa" and outcome.result eq "FAILURE" or eventType eq "user.session.start" and outcome.result eq "FAILURE"',
    }

    with progress_spinner(
        f"Fetching failed login attempts for the last {days} days..."
    ):
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

            if output == "table":
                # Format for table display
                formatted_logs = []
                for log in logs_data:
                    actor = log.get("actor", {})
                    client = log.get("client", {})

                    formatted_logs.append(
                        {
                            "Published": log.get("published", ""),
                            "Event Type": log.get("eventType", ""),
                            "User": actor.get(
                                "displayName", actor.get("alternateId", "")
                            ),
                            "Client IP": client.get("ipAddress", ""),
                            "User Agent": safe_nested_get(
                                client, "userAgent", "rawUserAgent"
                            ),
                            "Outcome Reason": safe_nested_get(log, "outcome", "reason"),
                            "City": safe_nested_get(
                                client, "geographicalContext", "city"
                            ),
                            "Country": safe_nested_get(
                                client, "geographicalContext", "country"
                            ),
                        }
                    )

                headers = [
                    "Published",
                    "Event Type",
                    "User",
                    "Client IP",
                    "User Agent",
                    "Outcome Reason",
                    "City",
                    "Country",
                ]
                format_and_output(formatted_logs, output, "generic", headers)
            else:
                format_and_output(logs_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@logs.command("suspicious")
@click.option("--profile", default=None, help="The profile to use.")
@click.option("--days", type=int, default=7, help="Number of days to look back.")
@click.option(
    "--limit", type=int, default=50, help="Number of suspicious activities to retrieve."
)
@create_output_option()
@with_error_handling
def suspicious_activities(profile, days, limit, output):
    """Get suspicious security activities."""
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
        "limit": limit,
        "since": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "until": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "filter": 'eventType eq "security.threat.detected" or eventType eq "user.account.lock" or eventType eq "user.authentication.auth_via_mfa" and outcome.result eq "CHALLENGE" or eventType eq "policy.evaluate_sign_on" and outcome.result eq "CHALLENGE"',
    }

    with progress_spinner(
        f"Fetching suspicious activities for the last {days} days..."
    ):
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

            if output == "table":
                # Format for table display
                formatted_logs = []
                for log in logs_data:
                    actor = log.get("actor", {})
                    client = log.get("client", {})

                    formatted_logs.append(
                        {
                            "Published": log.get("published", ""),
                            "Event Type": log.get("eventType", ""),
                            "User": actor.get(
                                "displayName", actor.get("alternateId", "")
                            ),
                            "Client IP": client.get("ipAddress", ""),
                            "Outcome": safe_nested_get(log, "outcome", "result"),
                            "Outcome Reason": safe_nested_get(log, "outcome", "reason"),
                            "City": safe_nested_get(
                                client, "geographicalContext", "city"
                            ),
                            "Country": safe_nested_get(
                                client, "geographicalContext", "country"
                            ),
                            "Display Message": log.get("displayMessage", ""),
                        }
                    )

                headers = [
                    "Published",
                    "Event Type",
                    "User",
                    "Client IP",
                    "Outcome",
                    "Outcome Reason",
                    "City",
                    "Country",
                    "Display Message",
                ]
                format_and_output(formatted_logs, output, "generic", headers)
            else:
                format_and_output(logs_data, output, "generic")

        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


if __name__ == "__main__":
    logs()
