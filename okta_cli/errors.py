"""
Error handling utilities for the Okta CLI tool.
"""

import re
import sys
import click
import requests
from typing import Optional, Dict, Any


class OktaError(Exception):
    """Base exception class for Okta CLI errors."""

    pass


class ValidationError(OktaError):
    """Exception raised for input validation errors."""

    pass


class ConfigurationError(OktaError):
    """Exception raised for configuration-related errors."""

    pass


class APIError(OktaError):
    """Exception raised for API-related errors."""

    pass


def validate_email(email: str) -> str:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        The validated email address

    Raises:
        ValidationError: If email format is invalid
    """
    if not email:
        raise ValidationError("Email cannot be empty")

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValidationError(f"Invalid email format: {email}")

    return email


def validate_login(login: str) -> str:
    """
    Validate login format.

    Args:
        login: Login name to validate

    Returns:
        The validated login name

    Raises:
        ValidationError: If login format is invalid
    """
    if not login or not login.strip():
        raise ValidationError("Login cannot be empty")

    return login.strip()


def validate_name(name: str, field_name: str) -> str:
    """
    Validate name format.

    Args:
        name: Name to validate
        field_name: Name of the field (for error messages)

    Returns:
        The validated name

    Raises:
        ValidationError: If name format is invalid
    """
    if not name or not name.strip():
        raise ValidationError(f"{field_name} cannot be empty")

    if len(name.strip()) > 100:
        raise ValidationError(f"{field_name} cannot be longer than 100 characters")

    return name.strip()


def validate_okta_domain(domain: str) -> str:
    """
    Validate Okta domain format.

    Args:
        domain: Okta domain to validate

    Returns:
        The validated domain

    Raises:
        ValidationError: If domain format is invalid
    """
    if not domain or not domain.strip():
        raise ValidationError("Okta domain cannot be empty")

    domain = domain.strip()

    # Remove protocol if present
    if domain.startswith("https://"):
        domain = domain[8:]
    elif domain.startswith("http://"):
        domain = domain[7:]

    # Remove trailing slash if present
    if domain.endswith("/"):
        domain = domain[:-1]

    # Check for valid Okta domain format
    okta_pattern = r"^[a-zA-Z0-9-]+\.(okta|oktapreview)\.com$"
    if not re.match(okta_pattern, domain):
        raise ValidationError(
            f"Invalid Okta domain format: {domain}. Expected format: your-domain.okta.com"
        )

    return domain


def validate_api_token(token: str) -> str:
    """
    Validate API token format.

    Args:
        token: API token to validate

    Returns:
        The validated token

    Raises:
        ValidationError: If token format is invalid
    """
    if token is None or not str(token).strip():
        raise ValidationError("API token cannot be empty")

    token = str(token).strip()

    # Basic token format validation (Okta tokens are typically 40+ characters)
    if len(token) < 20:
        raise ValidationError("API token appears to be too short")

    return token


def handle_api_error(response: requests.Response) -> None:
    """
    Handle API error responses and convert them to appropriate exceptions.

    Args:
        response: The HTTP response object

    Raises:
        APIError: With appropriate error message based on status code
    """
    status_code = response.status_code

    # Try to parse JSON error response
    try:
        error_data = response.json()
        error_summary = error_data.get("errorSummary", "Unknown error")
        error_code = error_data.get("errorCode", "Unknown")
    except (ValueError, KeyError):
        # Handle invalid JSON response
        if status_code >= 400:
            raise APIError(f"Invalid response format: {response.text}")
        error_summary = response.text or "Unknown error"
        error_code = "Unknown"

    # Map status codes to user-friendly messages with context
    error_messages = {
        400: f"Bad request: {error_summary}",
        401: f"Authentication failed: {error_summary}. Please check your API token.",
        403: f"Permission denied: {error_summary}. Your API token may not have the required permissions.",
        404: f"Resource not found: {error_summary}. The requested resource does not exist.",
        405: f"Method not allowed: {error_summary}. This operation is not supported for this resource.",
        409: f"Conflict: {error_summary}. The resource already exists or is in an invalid state.",
        429: f"Rate limit exceeded: {error_summary}. Please wait before making more requests.",
        500: f"Server error: {error_summary}. Please try again later.",
        502: f"Bad gateway: {error_summary}. Service temporarily unavailable.",
        503: f"Service unavailable: {error_summary}. Please try again later.",
        504: f"Gateway timeout: {error_summary}. Request took too long to complete.",
    }

    error_message = error_messages.get(
        status_code, f"HTTP {status_code}: {error_summary}"
    )

    # Add rate limit reset time if available
    if status_code == 429:
        reset_time = response.headers.get("X-Rate-Limit-Reset")
        if reset_time:
            error_message += f" (Reset at: {reset_time})"

    raise APIError(error_message)


def handle_network_error(error: requests.exceptions.RequestException) -> None:
    """
    Handle network-related errors.

    Args:
        error: The network error exception

    Raises:
        APIError: With appropriate error message
    """
    if isinstance(error, requests.exceptions.ConnectTimeout):
        raise APIError(
            "Connection timeout: Unable to connect to Okta. Please check your internet connection."
        )
    elif isinstance(error, requests.exceptions.ReadTimeout):
        raise APIError(
            "Request timeout: The request took too long to complete. Please try again."
        )
    elif isinstance(error, requests.exceptions.ConnectionError):
        raise APIError(
            "Connection failed: Unable to connect to Okta. Please check your internet connection and domain configuration."
        )
    elif isinstance(error, requests.exceptions.HTTPError):
        raise APIError(f"HTTP error: {error}")
    else:
        raise APIError(f"Network error: {error}")


def handle_json_error(error: ValueError, response_text: str) -> None:
    """
    Handle JSON parsing errors.

    Args:
        error: The JSON parsing error
        response_text: The response text that failed to parse

    Raises:
        APIError: With appropriate error message
    """
    raise APIError(f"Invalid response format: {response_text}")


def safe_exit(message: str, exit_code: int = 1) -> None:
    """
    Print error message and exit with the specified code.

    Args:
        message: Error message to display
        exit_code: Exit code (default: 1)
    """
    click.echo(f"Error: {message}", err=True)
    sys.exit(exit_code)


def handle_config_error(profile: str) -> None:
    """
    Handle configuration-related errors.

    Args:
        profile: The profile name that was not found

    Raises:
        ConfigurationError: With appropriate error message
    """
    raise ConfigurationError(
        f"Profile '{profile}' not found. Please run 'okta-cli configure --profile {profile}' to set up the profile."
    )


def handle_corrupted_config() -> None:
    """
    Handle corrupted configuration file errors.

    Raises:
        ConfigurationError: With appropriate error message
    """
    raise ConfigurationError(
        "Configuration file is corrupted. Please run 'okta-cli configure' to recreate it."
    )


def with_error_handling(func):
    """
    Decorator to add comprehensive error handling to CLI commands.

    Args:
        func: The function to wrap with error handling

    Returns:
        The wrapped function with error handling
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            safe_exit(str(e))
        except ConfigurationError as e:
            safe_exit(str(e))
        except APIError as e:
            safe_exit(str(e))
        except requests.exceptions.RequestException as e:
            handle_network_error(e)
        except ValueError as e:
            safe_exit(f"Invalid input: {e}")
        except Exception as e:
            safe_exit(f"Unexpected error: {e}")

    return wrapper
