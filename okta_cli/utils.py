"""
Utility functions for the Okta CLI tool.
"""

import requests
import re
from typing import Optional, Dict, Any


def is_okta_id(identifier: str) -> bool:
    """
    Check if a string looks like an Okta ID.
    Okta IDs are typically 20 characters long and alphanumeric.
    """
    if not identifier:
        return False

    # Okta IDs are typically 20 characters long, alphanumeric
    okta_id_pattern = r"^[a-zA-Z0-9]{20}$"
    return bool(re.match(okta_id_pattern, identifier))


def resolve_user_id(user_identifier: str, domain: str, token: str) -> Optional[str]:
    """
    Resolve a user identifier (email, login, or ID) to an Okta user ID.

    Args:
        user_identifier: User ID, email, or login
        domain: Okta domain
        token: API token

    Returns:
        User ID if found, None otherwise
    """
    if is_okta_id(user_identifier):
        return user_identifier

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Try to find user by login/email
    try:
        response = requests.get(
            f"https://{domain}/api/v1/users/{user_identifier}",
            headers=headers,
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()["id"]
    except requests.exceptions.RequestException:
        pass

    # If direct lookup fails, search users
    try:
        response = requests.get(
            f"https://{domain}/api/v1/users",
            headers=headers,
            params={
                "search": f'profile.email eq "{user_identifier}" or profile.login eq "{user_identifier}"'
            },
            timeout=30,
        )
        if response.status_code == 200:
            users = response.json()
            if users:
                return users[0]["id"]
    except requests.exceptions.RequestException:
        pass

    return None


def resolve_group_id(group_identifier: str, domain: str, token: str) -> Optional[str]:
    """
    Resolve a group identifier (name or ID) to an Okta group ID.

    Args:
        group_identifier: Group ID or name
        domain: Okta domain
        token: API token

    Returns:
        Group ID if found, None otherwise
    """
    if is_okta_id(group_identifier):
        return group_identifier

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Search for group by name
    try:
        response = requests.get(
            f"https://{domain}/api/v1/groups",
            headers=headers,
            params={"search": f'profile.name eq "{group_identifier}"'},
            timeout=30,
        )
        if response.status_code == 200:
            groups = response.json()
            for group in groups:
                if group["profile"]["name"] == group_identifier:
                    return group["id"]
    except requests.exceptions.RequestException:
        pass

    return None


def resolve_app_id(app_identifier: str, domain: str, token: str) -> Optional[str]:
    """
    Resolve an application identifier (name or ID) to an Okta app ID.

    Args:
        app_identifier: Application ID or name
        domain: Okta domain
        token: API token

    Returns:
        Application ID if found, None otherwise
    """
    if is_okta_id(app_identifier):
        return app_identifier

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Search for app by name
    try:
        response = requests.get(
            f"https://{domain}/api/v1/apps", headers=headers, timeout=30
        )
        if response.status_code == 200:
            apps = response.json()
            for app in apps:
                if (
                    app.get("name") == app_identifier
                    or app.get("label") == app_identifier
                ):
                    return app["id"]
    except requests.exceptions.RequestException:
        pass

    return None


def get_user_by_identifier(
    user_identifier: str, domain: str, token: str
) -> Optional[Dict[str, Any]]:
    """
    Get user object by identifier (email, login, or ID).

    Args:
        user_identifier: User ID, email, or login
        domain: Okta domain
        token: API token

    Returns:
        User object if found, None otherwise
    """
    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # First try direct lookup
    try:
        response = requests.get(
            f"https://{domain}/api/v1/users/{user_identifier}",
            headers=headers,
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass

    # If that fails, search
    try:
        response = requests.get(
            f"https://{domain}/api/v1/users",
            headers=headers,
            params={
                "search": f'profile.email eq "{user_identifier}" or profile.login eq "{user_identifier}"'
            },
            timeout=30,
        )
        if response.status_code == 200:
            users = response.json()
            if users:
                return users[0]
    except requests.exceptions.RequestException:
        pass

    return None


def get_group_by_identifier(
    group_identifier: str, domain: str, token: str
) -> Optional[Dict[str, Any]]:
    """
    Get group object by identifier (name or ID).

    Args:
        group_identifier: Group ID or name
        domain: Okta domain
        token: API token

    Returns:
        Group object if found, None otherwise
    """
    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # First try direct lookup if it looks like an ID
    if is_okta_id(group_identifier):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/groups/{group_identifier}",
                headers=headers,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass

    # Search by name
    try:
        response = requests.get(
            f"https://{domain}/api/v1/groups",
            headers=headers,
            params={"search": f'profile.name eq "{group_identifier}"'},
            timeout=30,
        )
        if response.status_code == 200:
            groups = response.json()
            for group in groups:
                if group["profile"]["name"] == group_identifier:
                    return group
    except requests.exceptions.RequestException:
        pass

    return None


def get_app_by_identifier(
    app_identifier: str, domain: str, token: str
) -> Optional[Dict[str, Any]]:
    """
    Get application object by identifier (name or ID).

    Args:
        app_identifier: Application ID or name
        domain: Okta domain
        token: API token

    Returns:
        Application object if found, None otherwise
    """
    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # First try direct lookup if it looks like an ID
    if is_okta_id(app_identifier):
        try:
            response = requests.get(
                f"https://{domain}/api/v1/apps/{app_identifier}",
                headers=headers,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass

    # Search by name/label
    try:
        response = requests.get(
            f"https://{domain}/api/v1/apps", headers=headers, timeout=30
        )
        if response.status_code == 200:
            apps = response.json()
            for app in apps:
                if (
                    app.get("name") == app_identifier
                    or app.get("label") == app_identifier
                ):
                    return app
    except requests.exceptions.RequestException:
        pass

    return None
