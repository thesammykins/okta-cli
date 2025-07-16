# Okta CLI Tool Documentation

This documentation provides information on how to use the Okta CLI tool, as well as references to Okta API documentation and code standards.

## Table of Contents

*   [Getting Started](#getting-started)
    *   [Installation](#installation)
    *   [Configuration](#configuration)
*   [User Management](#user-management)
    *   [List Users](#list-users)
    *   [Create User](#create-user)
    *   [Show User](#show-user)
    *   [Update User](#update-user)
    *   [Suspend User](#suspend-user)
    *   [Unsuspend User](#unsuspend-user)
    *   [Deactivate User](#deactivate-user)
    *   [Activate User](#activate-user)
    *   [Reset Password](#reset-password)
    *   [Assign User to Application](#assign-user-to-application)
    *   [Unassign User from Application](#unassign-user-from-application)
    *   [List Application Assignments](#list-application-assignments)
*   [Group Management](#group-management)
    *   [List Groups](#list-groups)
    *   [Create Group](#create-group)
    *   [Show Group](#show-group)
    *   [Update Group](#update-group)
    *   [Delete Group](#delete-group)
    *   [Add User to Group](#add-user-to-group)
    *   [Remove User from Group](#remove-user-from-group)
    *   [List Group Members](#list-group-members)
*   [API References](#api-references)
*   [Error Handling](#error-handling)
*   [Security Features](#security-features)
*   [Code Standards](#code-standards)

## Getting Started

### Installation

To install the Okta CLI tool, you need Python 3.8 or higher and `pip`.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/samanthamyers/provision.git
    cd provision
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -e .
    ```

### Configuration

Before using the CLI tool, you need to configure your Okta domain and API token. You can do this using the `configure` command:

```bash
okta-cli configure
```

You will be prompted to enter your Okta domain (e.g., `your-domain.okta.com`) and your API token. The API token should be a valid Okta API token with sufficient permissions to manage users and groups.

## User Management

### List Users

To list all users in your Okta organization:

```bash
okta-cli users list
```

### Create User

To create a new user:

```bash
okta-cli users create --first-name John --last-name Doe --email john.doe@example.com --login john.doe@example.com
```

### Show User

To show details for a specific user by their ID:

```bash
okta-cli users show <user_id>
```

### Update User

To update a user's profile:

```bash
okta-cli users update <user_id> --first-name Jane --email jane.doe@example.com
```

### Suspend User

To suspend a user:

```bash
okta-cli users suspend <user_id>
```

### Unsuspend User

To unsuspend a user:

```bash
okta-cli users unsuspend <user_id>
```

### Deactivate User

To deactivate a user:

```bash
okta-cli users deactivate <user_id>
```

### Activate User

To activate a user:

```bash
okta-cli users activate <user_id>
```

### Reset Password

To reset a user's password and get a temporary password:

```bash
okta-cli users reset-password <user_id>
```

### Assign User to Application

To assign a user to an application with optional profile attributes:

```bash
okta-cli users assign-app <user_id> <app_id> --profile-attributes '{"role": "admin"}'
```

### Unassign User from Application

To unassign a user from an application:

```bash
okta-cli users unassign-app <user_id> <app_id>
```

### List Application Assignments

To list users assigned to a specific application:

```bash
okta-cli users list-app-assignments <app_id>
```

## Group Management

### List Groups

To list all groups in your Okta organization:

```bash
okta-cli groups list
```

### Create Group

To create a new group:

```bash
okta-cli groups create --name "New Group" --description "A new group for testing"
```

### Show Group

To show details for a specific group by its ID:

```bash
okta-cli groups show <group_id>
```

### Update Group

To update a group's profile:

```bash
okta-cli groups update <group_id> --name "Updated Group Name" --description "An updated description"
```

### Delete Group

To delete a group:

```bash
okta-cli groups delete <group_id>
```

### Add User to Group

To add a user to a group:

```bash
okta-cli groups add-user <group_id> <user_id>
```

### Remove User from Group

To remove a user from a group:

```bash
okta-cli groups remove-user <group_id> <user_id>
```

### List Group Members

To list members of a specific group:

```bash
okta-cli groups list-members <group_id>
```

## API References

This section provides links to the official Okta API documentation for the endpoints used in this CLI tool.

## Okta Users API

*   **List Users:** [List Users](https://developer.okta.com/docs/reference/api/users/#list-users)
*   **Create User:** [Create User](https://developer.okta.com/docs/reference/api/users/#create-user)
*   **Get User:** [Get User](https://developer.okta.com/docs/reference/api/users/#get-user)
*   **Update User:** [Update User](https://developer.okta.com/docs/reference/api/users/#update-user)
*   **Suspend User:** [Suspend User](https://developer.okta.com/docs/reference/api/users/#suspend-user)
*   **Unsuspend User:** [Unsuspend User](https://developer.okta.com/docs/reference/api/users/#unsuspend-user)
*   **Deactivate User:** [Deactivate User](https://developer.okta.com/docs/reference/api/users/#deactivate-user)
*   **Activate User:** [Activate User](https://developer.okta.com/docs/reference/api/users/#activate-user)
*   **Reset Password:** [Reset Password](https://developer.okta.com/docs/reference/api/users/#reset-password)

## Okta Groups API

*   **List Groups:** [List Groups](https://developer.okta.com/docs/reference/api/groups/#list-groups)
*   **Create Group:** [Create Group](https://developer.okta.com/docs/reference/api/groups/#create-group)
*   **Get Group:** [Get Group](https://developer.okta.com/docs/reference/api/groups/#get-group)
*   **Update Group:** [Update Group](https://developer.okta.com/docs/reference/api/groups/#update-group)
*   **Delete Group:** [Delete Group](https://developer.okta.com/docs/reference/api/groups/#delete-group)
*   **Add User to Group:** [Add User to Group](https://developer.okta.com/docs/reference/api/groups/#add-user-to-group)
*   **Remove User from Group:** [Remove User from Group](https://developer.okta.com/docs/reference/api/groups/#remove-user-from-group)
*   **List Group Members:** [List Group Members](https://developer.okta.com/docs/reference/api/groups/#list-group-members)

## Okta Application Assignments API

*   **Assign User to Application:** [Assign User to Application](https://developer.okta.com/docs/reference/api/apps/#assign-user-to-application)
*   **Unassign User from Application:** [Unassign User from Application](https://developer.okta.com/docs/reference/api/apps/#unassign-user-from-application)
*   **List Application Assignments:** [List Application Assignments](https://developer.okta.com/docs/reference/api/apps/#list-application-assignments)

## Error Handling

The Okta CLI tool includes comprehensive error handling to provide clear, actionable feedback when issues occur. All commands include:

- **Input Validation**: Email format, domain validation, and required field checks
- **API Error Handling**: Clear messages for authentication, permission, and server errors
- **Network Error Handling**: Timeout and connection error management
- **Configuration Error Handling**: Missing profile and configuration file issues

For detailed information about error types and recovery suggestions, see the [Error Handling Documentation](error_handling.md).

### Common Error Examples

```bash
# Authentication error
Error: Authentication failed: Invalid token provided

# Permission error  
Error: Permission denied: You do not have permission to access this resource

# Network error
Error: Connection timeout: Unable to connect to Okta. Please check your internet connection.

# Validation error
Error: Invalid email format: invalid-email
```

## Security Features

The Okta CLI tool includes comprehensive security features to protect your credentials and ensure safe API usage:

- **Encrypted Credential Storage**: All API tokens are encrypted using AES-256 encryption with PBKDF2 key derivation
- **Token Validation**: Validates tokens and permissions before API calls
- **Rate Limiting**: Client-side rate limiting to prevent API abuse
- **Secure File Permissions**: Restrictive file permissions on configuration files
- **Master Password Protection**: All credentials protected by a master password

### Key Security Features

```bash
# Encrypted credential storage with master password
okta-cli configure
Create master password: [hidden]
Confirm master password: [hidden]

# Automatic token validation
okta-cli users list
# Token validation occurs automatically before API calls

# Built-in rate limiting
# CLI automatically manages rate limits to prevent API violations
```

### Security Best Practices

1. **Use strong master passwords** (8+ characters with mixed case, numbers, symbols)
2. **Rotate API tokens regularly** 
3. **Keep configuration files secure** (automatic restrictive permissions)
4. **Monitor token usage** and access patterns
5. **Create encrypted backups** of your configuration

For detailed security information, see the [Security Documentation](security.md).

### Security Architecture

The CLI implements multiple security layers:
- **Transport Security**: HTTPS with certificate validation
- **Credential Encryption**: AES-256 encryption at rest  
- **Access Control**: File permissions and master password protection
- **Rate Limiting**: Prevents abuse and ensures reliable operation
- **Input Validation**: All input validated before processing
