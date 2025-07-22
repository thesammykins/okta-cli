# Okta CLI Agent Guide

This guide provides comprehensive information for AI agents on how to effectively use the Okta CLI tool for identity and access management tasks.

## Overview

The Okta CLI is a comprehensive command-line tool for managing Okta identity and access management operations. It provides extensive functionality for user management, application management, security policies, session management, and more.

## 🤖 AI Agent Rules and Guidelines

### Mandatory Pre-Action Steps

**ALWAYS perform these steps before executing any Okta CLI commands:**

1. **Verify Environment Setup**
   ```bash
   # Check if virtual environment is activated
   source venv/bin/activate
   
   # Verify CLI is available
   okta-cli --help
   ```

2. **Check Configuration Health**
   ```bash
   # MANDATORY: Always verify configuration before operations
   okta-cli config health
   okta-cli config status
   ```

3. **Validate Profile and Permissions**
   ```bash
   # Ensure you're using the correct profile
   okta-cli config show
   
   # Test connectivity
   okta-cli config validate
   ```

### Agent Operating Principles

#### 1. **Safety First**
- **NEVER** perform destructive operations without explicit user confirmation
- **ALWAYS** use `--output json` for programmatic operations to verify results
- **ALWAYS** check user/group/app existence before operations
- **ALWAYS** verify current state before making changes

#### 2. **User-Friendly Identifiers**
- **ALWAYS** use human-readable names when possible (email, login, group names)
- **NEVER** assume users know Okta internal IDs
- **ALWAYS** resolve names to IDs internally using the CLI's built-in functionality

#### 3. **Comprehensive Verification**
- **ALWAYS** show the result of operations to confirm success
- **ALWAYS** handle errors gracefully and provide clear explanations
- **ALWAYS** suggest corrective actions when errors occur

#### 4. **Audit Trail**
- **ALWAYS** log significant operations for audit purposes
- **ALWAYS** use appropriate output formats for tracking
- **ALWAYS** preserve operation history for troubleshooting

### Required Profile Parameter

**CRITICAL**: Most commands require the `--profile` parameter to work correctly. Always specify the profile:

```bash
# CORRECT - Always specify profile
okta-cli users list --profile dev-test
okta-cli users show user@example.com --profile dev-test

# INCORRECT - May fail without profile
okta-cli users list
okta-cli users show user@example.com
```

## 🔄 Agent Workflow Patterns

### Pattern 1: Creating a New User Mirroring Another User

**Scenario**: User asks to create a new user with the same permissions as an existing user.

**Required Steps**:

1. **Verify Environment and Get Source User**
   ```bash
   # Check environment
   okta-cli config health --profile PROFILE_NAME
   
   # Get source user details
   okta-cli users show SOURCE_USER_EMAIL --profile PROFILE_NAME --output json
   ```

2. **Extract Source User's Group Memberships**
   ```bash
   # Get all groups to find memberships
   okta-cli groups list --profile PROFILE_NAME --output json
   
   # Check which groups the source user belongs to
   # (Note: CLI doesn't have direct user-groups lookup, need to check each group)
   okta-cli groups list-members GROUP_NAME --profile PROFILE_NAME
   ```

3. **Create the New User**
   ```bash
   # Create new user with similar profile
   okta-cli users create \
     --first-name "NEW_FIRST_NAME" \
     --last-name "NEW_LAST_NAME" \
     --email "NEW_EMAIL@company.com" \
     --login "NEW_EMAIL@company.com" \
     --profile PROFILE_NAME
   ```

4. **Apply Group Memberships**
   ```bash
   # Add new user to same groups as source user
   okta-cli groups add-user "GROUP_NAME" "NEW_EMAIL@company.com" --profile PROFILE_NAME
   ```

5. **Verify Application Assignments**
   ```bash
   # Check applications assigned to source user
   okta-cli applications list --profile PROFILE_NAME --output json
   
   # Assign same applications to new user (if supported)
   okta-cli users assign-app "NEW_EMAIL@company.com" "APP_NAME" --profile PROFILE_NAME
   ```

6. **Activate the New User**
   ```bash
   # Activate the new user
   okta-cli users activate "NEW_EMAIL@company.com" --profile PROFILE_NAME
   ```

### Pattern 2: User Onboarding Workflow

**Scenario**: Complete user onboarding process.

**Required Steps**:

1. **Pre-Onboarding Verification**
   ```bash
   # Check if user already exists
   okta-cli users show "NEW_EMAIL@company.com" --profile PROFILE_NAME
   # (Should return error if user doesn't exist)
   ```

2. **Create User**
   ```bash
   okta-cli users create \
     --first-name "FIRST_NAME" \
     --last-name "LAST_NAME" \
     --email "NEW_EMAIL@company.com" \
     --login "NEW_EMAIL@company.com" \
     --profile PROFILE_NAME
   ```

3. **Add to Standard Groups**
   ```bash
   # Add to everyone/all-employees group
   okta-cli groups add-user "Everyone" "NEW_EMAIL@company.com" --profile PROFILE_NAME
   
   # Add to department-specific groups
   okta-cli groups add-user "DEPARTMENT_NAME" "NEW_EMAIL@company.com" --profile PROFILE_NAME
   ```

4. **Assign Applications**
   ```bash
   # Assign standard applications
   okta-cli users assign-app "NEW_EMAIL@company.com" "STANDARD_APP" --profile PROFILE_NAME
   ```

5. **Activate User**
   ```bash
   okta-cli users activate "NEW_EMAIL@company.com" --profile PROFILE_NAME
   ```

6. **Generate Report**
   ```bash
   # Create onboarding report
   okta-cli users show "NEW_EMAIL@company.com" --profile PROFILE_NAME --output json
   ```

### Pattern 3: User Offboarding Workflow

**Scenario**: Complete user offboarding process.

**Required Steps**:

1. **Verify User Exists and Get Current State**
   ```bash
   okta-cli users show "USER_EMAIL@company.com" --profile PROFILE_NAME --output json
   ```

2. **Clear Active Sessions**
   ```bash
   okta-cli sessions clear "USER_EMAIL@company.com" --profile PROFILE_NAME --force
   ```

3. **Remove from Groups**
   ```bash
   # List all groups first
   okta-cli groups list --profile PROFILE_NAME --output json
   
   # Remove from each group (check membership first)
   okta-cli groups remove-user "GROUP_NAME" "USER_EMAIL@company.com" --profile PROFILE_NAME
   ```

4. **Unassign Applications**
   ```bash
   # Unassign applications
   okta-cli users unassign-app "USER_EMAIL@company.com" "APP_NAME" --profile PROFILE_NAME
   ```

5. **Deactivate User**
   ```bash
   okta-cli users deactivate "USER_EMAIL@company.com" --profile PROFILE_NAME
   ```

6. **Generate Offboarding Report**
   ```bash
   # Verify final state
   okta-cli users show "USER_EMAIL@company.com" --profile PROFILE_NAME --output json
   ```

### Pattern 4: Bulk Operations

**Scenario**: Performing operations on multiple users.

**Required Steps**:

1. **Get User List**
   ```bash
   # Export users to work with
   okta-cli users list --profile PROFILE_NAME --output json > users.json
   ```

2. **Process Each User**
   ```bash
   # Use JSON output for programmatic processing
   # Parse JSON and iterate through users
   # Apply operations to each user individually
   ```

3. **Verify Results**
   ```bash
   # Check results for each user
   okta-cli users show "USER_EMAIL" --profile PROFILE_NAME --output json
   ```

### Pattern 5: Security Audit

**Scenario**: Performing security audits and monitoring.

**Required Steps**:

1. **Check Failed Logins**
   ```bash
   okta-cli logs failed-logins --days 7 --profile PROFILE_NAME --output json
   ```

2. **Monitor Suspicious Activities**
   ```bash
   okta-cli logs suspicious --days 7 --profile PROFILE_NAME --output json
   ```

3. **Check MFA Adoption**
   ```bash
   okta-cli factors stats --profile PROFILE_NAME --output json
   ```

4. **Review User Sessions**
   ```bash
   okta-cli sessions active --profile PROFILE_NAME --output json
   ```

### Pattern 6: Group Management

**Scenario**: Managing groups and memberships.

**Required Steps**:

1. **List Groups**
   ```bash
   okta-cli groups list --profile PROFILE_NAME --output json
   ```

2. **Create New Group**
   ```bash
   okta-cli groups create \
     --name "NEW_GROUP_NAME" \
     --description "Group description" \
     --profile PROFILE_NAME
   ```

3. **Add Users to Group**
   ```bash
   okta-cli groups add-user "GROUP_NAME" "USER_EMAIL@company.com" --profile PROFILE_NAME
   ```

4. **Verify Group Membership**
   ```bash
   okta-cli groups list-members "GROUP_NAME" --profile PROFILE_NAME
   ```

## ⚠️ Agent Error Handling and Recovery

### Common Error Scenarios and Solutions

#### 1. **Configuration Issues**

**Error**: "Profile 'default' not found"
**Solution**:
```bash
# Check available profiles
okta-cli config list --profile PROFILE_NAME

# Use correct profile name
okta-cli users list --profile dev-test
```

#### 2. **User Not Found Errors**

**Error**: "User not found with identifier 'user@example.com'"
**Solution**:
```bash
# Verify user exists first
okta-cli users list --profile PROFILE_NAME --output json | grep "user@example.com"

# Try different identifier (login vs email)
okta-cli users show "user@example.com" --profile PROFILE_NAME
```

#### 3. **Permission Errors**

**Error**: "Permission denied: Your API token may not have the required permissions"
**Solution**:
```bash
# Check token permissions
okta-cli config validate --profile PROFILE_NAME

# Verify configuration
okta-cli config health --profile PROFILE_NAME
```

#### 4. **Application Assignment Errors**

**Error**: "App instance operation not allowed"
**Solution**:
```bash
# Check if application supports assignments
okta-cli applications show "APP_NAME" --profile PROFILE_NAME --output json

# Some built-in Okta apps don't support manual assignment
# Try with custom applications instead
```

#### 5. **Session Management Errors**

**Error**: "Method not allowed" for session operations
**Solution**:
```bash
# Session management may have limitations in demo environments
# Focus on user lifecycle operations instead
okta-cli users activate "user@example.com" --profile PROFILE_NAME
```

### Agent Recovery Procedures

#### When Operations Fail:

1. **Check Environment**
   ```bash
   okta-cli config health --profile PROFILE_NAME
   ```

2. **Verify Resource Existence**
   ```bash
   # For users
   okta-cli users show "identifier" --profile PROFILE_NAME
   
   # For groups
   okta-cli groups show "group_name" --profile PROFILE_NAME
   
   # For applications
   okta-cli applications show "app_name" --profile PROFILE_NAME
   ```

3. **Use JSON Output for Debugging**
   ```bash
   # Always use JSON for programmatic operations
   okta-cli users list --profile PROFILE_NAME --output json
   ```

4. **Check Audit Logs**
   ```bash
   # Review recent operations
   okta-cli logs list --profile PROFILE_NAME --limit 10
   ```

### Mandatory Error Reporting

When operations fail, agents MUST:

1. **Report the exact error message**
2. **Show the command that failed**
3. **Provide suggested corrective actions**
4. **Verify environment state**

Example error reporting format:
```
❌ Operation Failed: Creating user john.doe@example.com
Command: okta-cli users create --first-name John --last-name Doe --email john.doe@example.com --login john.doe@example.com --profile dev-test
Error: User already exists
Recovery: Check existing user with: okta-cli users show john.doe@example.com --profile dev-test
```

## 🔧 Environment Setup for Agents

### Initial Environment Verification

**Before any operations, agents must verify:**

1. **Python Virtual Environment**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Verify Python version
   python --version
   
   # Check installed packages
   pip list | grep okta
   ```

2. **CLI Installation**
   ```bash
   # Verify CLI is installed
   okta-cli --version
   
   # Check command availability
   okta-cli --help
   ```

3. **Configuration State**
   ```bash
   # Check configuration directory
   ls -la ~/.okta-cli/
   
   # Verify profiles
   okta-cli config list
   
   # Check active profile
   okta-cli config status
   ```

### Profile Management

**Agents must understand profile context:**

```bash
# List available profiles
okta-cli config list

# Get current active profile
okta-cli config status

# Show specific profile details
okta-cli config show PROFILE_NAME

# Validate profile connectivity
okta-cli config validate PROFILE_NAME
```

### Required Environment Variables

**For automation, agents should set:**

```bash
# Set profile explicitly
export OKTA_PROFILE=dev-test

# Enable debug mode for troubleshooting
export OKTA_DEBUG=true

# Set timeout for operations
export OKTA_TIMEOUT=30
```

### Command Construction Rules

**Agents must follow these patterns:**

1. **Always specify profile**
   ```bash
   okta-cli COMMAND --profile PROFILE_NAME
   ```

2. **Use appropriate output format**
   ```bash
   # For display
   okta-cli COMMAND --profile PROFILE_NAME --output table
   
   # For processing
   okta-cli COMMAND --profile PROFILE_NAME --output json
   ```

3. **Include error handling**
   ```bash
   # Check command success
   if okta-cli COMMAND --profile PROFILE_NAME; then
     echo "✅ Operation successful"
   else
     echo "❌ Operation failed"
     okta-cli config health --profile PROFILE_NAME
   fi
   ```

### Agent Validation Checklist

**Before executing any workflow, verify:**

- [ ] Virtual environment is activated
- [ ] CLI is available and functional
- [ ] Configuration is healthy
- [ ] Profile is valid and accessible
- [ ] Required permissions are available
- [ ] Network connectivity is working
- [ ] Target resources exist (if applicable)

### Required Command Patterns

**Agents must use these specific patterns:**

```bash
# Pattern for all user operations
okta-cli users OPERATION "user@example.com" --profile PROFILE_NAME

# Pattern for all group operations
okta-cli groups OPERATION "Group Name" --profile PROFILE_NAME

# Pattern for all application operations
okta-cli applications OPERATION "App Name" --profile PROFILE_NAME

# Pattern for policy operations (note: --type is required)
okta-cli policies list --type POLICY_TYPE --profile PROFILE_NAME
```

## Quick Start

### Installation and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI
python -m okta_cli --help

# First-time setup - use the interactive wizard
python -m okta_cli config wizard
```

### Basic Configuration

```bash
# Configure with interactive wizard (recommended)
okta-cli config wizard

# Manual configuration
okta-cli configure --profile default

# List profiles
okta-cli config list

# Set active profile
okta-cli config activate production
```

## Core Commands Structure

The CLI is organized into the following main command groups:

1. **config** - Configuration and profile management
2. **users** - User management operations
3. **groups** - Group management operations
4. **applications** - Application management
5. **sessions** - User session management
6. **policies** - Policy and group rules management
7. **authorization** - Authorization server management
8. **logs** - Event log querying and analysis
9. **factors** - Multi-factor authentication management

## Command Reference

### Configuration Management

```bash
# Profile Management
okta-cli config create dev --domain dev.okta.com --token your-token
okta-cli config list --output table
okta-cli config activate dev
okta-cli config show dev
okta-cli config delete dev --force

# Environment Variables
export OKTA_DOMAIN=your.okta.com
export OKTA_TOKEN=your-api-token
export OKTA_PROFILE=production

# Health Checks
okta-cli config health
okta-cli config validate dev
okta-cli config status

# Backup and Restore
okta-cli config backup --output backup.json
okta-cli config restore backup.json --force
```

### User Management

```bash
# List and Search Users
okta-cli users list --output table
okta-cli users list --profile production --output json
okta-cli users show user123 --output yaml

# Create Users
okta-cli users create \
  --first-name John \
  --last-name Doe \
  --email john.doe@example.com \
  --login john.doe@example.com

# User Lifecycle
okta-cli users activate user123
okta-cli users deactivate user123
okta-cli users suspend user123
okta-cli users unsuspend user123
okta-cli users reset-password user123

# User Updates
okta-cli users update user123 \
  --first-name Jonathan \
  --email new.email@example.com

# Application Assignments
okta-cli users assign-app user123 app456
okta-cli users unassign-app user123 app456
okta-cli users list-app-assignments app456
```

### Group Management

```bash
# List and Show Groups
okta-cli groups list --output table
okta-cli groups show group123

# Create and Update Groups
okta-cli groups create \
  --name "Engineering Team" \
  --description "Software engineers"

okta-cli groups update group123 \
  --name "Senior Engineering Team"

# Group Membership
okta-cli groups add-user group123 user456
okta-cli groups remove-user group123 user456
okta-cli groups list-users group123

# Group Lifecycle
okta-cli groups delete group123 --force
```

### Application Management

```bash
# List and Show Applications
okta-cli applications list --output table
okta-cli applications show app123

# Create Applications
okta-cli applications create \
  --name "My App" \
  --label "My Application" \
  --sign-on-mode SAML_2_0

# Application Lifecycle
okta-cli applications activate app123
okta-cli applications deactivate app123
okta-cli applications delete app123 --force

# Application Assignments
okta-cli applications list-users app123
okta-cli applications list-groups app123

# Update Applications
okta-cli applications update app123 \
  --name "Updated App Name" \
  --status ACTIVE
```

### Session Management

```bash
# List and Show Sessions
okta-cli sessions list user123 --output table
okta-cli sessions show user123 session456

# Session Operations
okta-cli sessions extend user123 session456
okta-cli sessions clear user123 --force
okta-cli sessions clear user123 --oauth-only

# Session Analytics
okta-cli sessions stats --days 30
okta-cli sessions active --limit 50
```

### Policy and Group Rules Management

```bash
# List Policies
okta-cli policies list --type PASSWORD --output table
okta-cli policies show policy123

# Policy Operations
okta-cli policies activate policy123
okta-cli policies deactivate policy123

# Group Rules
okta-cli policies rules list --output table
okta-cli policies rules show rule123

# Create Group Rules
okta-cli policies rules create \
  --name "Engineering Rule" \
  --expression 'user.department=="Engineering"' \
  --group-id group123

# Group Rule Lifecycle
okta-cli policies rules activate rule123
okta-cli policies rules deactivate rule123
okta-cli policies rules delete rule123 --force
```

### Authorization Server Management

```bash
# List Authorization Servers
okta-cli authorization list --output table
okta-cli authorization show server123

# Create Authorization Server
okta-cli authorization create \
  --name "My API Server" \
  --description "API authorization server" \
  --audience "api://my-api"

# Authorization Server Operations
okta-cli authorization activate server123
okta-cli authorization deactivate server123
okta-cli authorization delete server123 --force

# Scope Management
okta-cli authorization scopes list server123
okta-cli authorization scopes create server123 \
  --name "read:users" \
  --description "Read user data" \
  --consent REQUIRED
```

### Event Log Analysis

```bash
# List and Search Logs
okta-cli logs list --limit 100 --output table
okta-cli logs show log-uuid-123

# Advanced Search
okta-cli logs search \
  --event-type "user.session.start" \
  --outcome SUCCESS \
  --days 7

# Security Monitoring
okta-cli logs failed-logins --days 1
okta-cli logs suspicious --days 7

# Log Analytics
okta-cli logs stats --days 30 --output json
```

### Multi-Factor Authentication

```bash
# List User Factors
okta-cli factors list user123 --output table
okta-cli factors show user123 factor456

# Factor Operations
okta-cli factors verify user123 factor456 --passcode 123456
okta-cli factors reset user123 factor456 --force

# Factor Analytics
okta-cli factors stats --limit 1000
okta-cli factors catalog list user123
```

## Output Formats

All commands support multiple output formats:

```bash
# Table format (default, human-readable)
okta-cli users list --output table

# JSON format (structured data)
okta-cli users list --output json

# CSV format (spreadsheet-friendly)
okta-cli users list --output csv

# YAML format (configuration-friendly)
okta-cli users list --output yaml

# Text format (plain text)
okta-cli users list --output text
```

## Common Use Cases

### User Onboarding

```bash
# Create user
okta-cli users create \
  --first-name "Jane" \
  --last-name "Smith" \
  --email "jane.smith@company.com" \
  --login "jane.smith@company.com"

# Add to groups
okta-cli groups add-user engineering-team user123
okta-cli groups add-user all-employees user123

# Assign applications
okta-cli users assign-app user123 app456
okta-cli users assign-app user123 app789

# Activate user
okta-cli users activate user123
```

### User Offboarding

```bash
# Deactivate user
okta-cli users deactivate user123

# Clear active sessions
okta-cli sessions clear user123 --force

# Remove from groups
okta-cli groups remove-user engineering-team user123
okta-cli groups remove-user all-employees user123

# Unassign applications
okta-cli users unassign-app user123 app456
okta-cli users unassign-app user123 app789
```

### Security Monitoring

```bash
# Check for failed login attempts
okta-cli logs failed-logins --days 1 --output json

# Monitor suspicious activities
okta-cli logs suspicious --days 7 --output table

# Analyze login patterns
okta-cli logs search \
  --event-type "user.session.start" \
  --days 30 \
  --output csv

# Check MFA adoption
okta-cli factors stats --output json
```

### Application Management

```bash
# List all applications
okta-cli applications list --output table

# Check application assignments
okta-cli applications list-users app123
okta-cli applications list-groups app123

# Update application settings
okta-cli applications update app123 \
  --name "Updated App" \
  --status ACTIVE
```

### Bulk Operations

```bash
# Export users to CSV
okta-cli users list --output csv > users.csv

# Export groups to JSON
okta-cli groups list --output json > groups.json

# Export application assignments
okta-cli applications list-users app123 --output csv > app_users.csv

# Export security logs
okta-cli logs search --days 30 --output json > security_logs.json
```

## Error Handling

The CLI provides comprehensive error handling:

```bash
# Check configuration health
okta-cli config health

# Validate profiles
okta-cli config validate production

# Test connectivity
okta-cli config show production
```

Common error scenarios:
- **Invalid credentials**: Use `okta-cli config validate` to verify
- **Network issues**: Check domain and connectivity
- **Permission errors**: Verify API token permissions
- **Resource not found**: Check resource IDs and filters

## Best Practices

### Security

1. **Use environment variables** for sensitive data in automation
2. **Rotate API tokens** regularly
3. **Use least privilege** - create tokens with minimal required permissions
4. **Monitor API usage** through logs and analytics
5. **Use profiles** for different environments (dev, staging, prod)

### Performance

1. **Use filters** to limit data retrieval
2. **Batch operations** when possible
3. **Use appropriate output formats** for your use case
4. **Implement pagination** for large datasets
5. **Cache configuration** when running multiple commands

### Automation

1. **Use JSON output** for parsing in scripts
2. **Check exit codes** for error handling
3. **Use --force flags** for non-interactive operations
4. **Implement retry logic** for transient failures
5. **Log operations** for audit trails

## Integration Examples

### Shell Script Integration

```bash
#!/bin/bash
set -e

# Set up environment
export OKTA_DOMAIN="company.okta.com"
export OKTA_TOKEN="$OKTA_API_TOKEN"

# Check configuration
if ! okta-cli config health; then
    echo "Configuration health check failed"
    exit 1
fi

# Perform operations
okta-cli users list --output json > /tmp/users.json
okta-cli groups list --output json > /tmp/groups.json

echo "Export completed successfully"
```

### Python Integration

```python
import subprocess
import json
import os

# Set up environment
os.environ['OKTA_DOMAIN'] = 'company.okta.com'
os.environ['OKTA_TOKEN'] = 'your-api-token'

def run_okta_cli(command):
    """Run Okta CLI command and return JSON output."""
    cmd = ['okta-cli'] + command + ['--output', 'json']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    
    return json.loads(result.stdout)

# Example usage
users = run_okta_cli(['users', 'list'])
groups = run_okta_cli(['groups', 'list'])

print(f"Found {len(users)} users and {len(groups)} groups")
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Okta User Management
on:
  workflow_dispatch:
    inputs:
      action:
        description: 'Action to perform'
        required: true
        type: choice
        options:
          - 'export-users'
          - 'security-report'

jobs:
  okta-management:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Export users
        if: github.event.inputs.action == 'export-users'
        env:
          OKTA_DOMAIN: ${{ secrets.OKTA_DOMAIN }}
          OKTA_TOKEN: ${{ secrets.OKTA_TOKEN }}
        run: |
          okta-cli users list --output csv > users.csv
          okta-cli groups list --output csv > groups.csv
      
      - name: Security report
        if: github.event.inputs.action == 'security-report'
        env:
          OKTA_DOMAIN: ${{ secrets.OKTA_DOMAIN }}
          OKTA_TOKEN: ${{ secrets.OKTA_TOKEN }}
        run: |
          okta-cli logs failed-logins --days 7 --output json > failed_logins.json
          okta-cli logs suspicious --days 7 --output json > suspicious.json
          okta-cli factors stats --output json > mfa_stats.json
```

## Advanced Features

### Configuration Profiles

```bash
# Multiple environment setup
okta-cli config create dev --domain dev.okta.com --token dev-token
okta-cli config create staging --domain staging.okta.com --token staging-token
okta-cli config create prod --domain prod.okta.com --token prod-token

# Switch between environments
okta-cli config activate dev
okta-cli users list

okta-cli config activate prod
okta-cli users list --profile prod
```

### Environment Variables

```bash
# Profile-specific variables
export OKTA_DEV_DOMAIN=dev.okta.com
export OKTA_DEV_TOKEN=dev-token
export OKTA_PROD_DOMAIN=prod.okta.com
export OKTA_PROD_TOKEN=prod-token

# Use profile-specific variables
okta-cli users list --profile dev
okta-cli users list --profile prod
```

### Interactive Mode

```bash
# Interactive configuration wizard
okta-cli config wizard

# Interactive management
okta-cli config interactive

# Configuration status
okta-cli config status
```

## Troubleshooting

### Common Issues

1. **Authentication errors**
   ```bash
   # Check token validity
   okta-cli config validate
   okta-cli config health
   ```

2. **Network connectivity**
   ```bash
   # Test connectivity
   okta-cli config health
   # Check domain configuration
   okta-cli config show
   ```

3. **Permission issues**
   ```bash
   # Check API token permissions
   okta-cli logs search --event-type "system.api_token.create"
   ```

4. **Rate limiting**
   ```bash
   # Monitor API usage
   okta-cli logs search --event-type "system.api.request"
   ```

### Debug Mode

```bash
# Enable debug output
export OKTA_DEBUG=true
okta-cli users list

# Verbose logging
okta-cli --verbose users list
```

## API Reference

The CLI interacts with the following Okta API endpoints:

- **Users API**: `/api/v1/users`
- **Groups API**: `/api/v1/groups`
- **Applications API**: `/api/v1/apps`
- **Application Users API**: `/api/v1/apps/{appId}/users` (corrected endpoint)
- **Sessions API**: `/api/v1/sessions` (corrected endpoint)
- **Policies API**: `/api/v1/policies` (requires type parameter)
- **Group Rules API**: `/api/v1/groups/rules`
- **Authorization Servers API**: `/api/v1/authorizationServers`
- **System Log API**: `/api/v1/logs`
- **Factors API**: `/api/v1/users/{userId}/factors`

### Key Endpoint Corrections Made:

1. **User Application Assignment**: 
   - ✅ Correct: `POST /api/v1/apps/{appId}/users`
   - ❌ Previous: `POST /api/v1/apps/{appId}/assignments`

2. **Session Management**:
   - ✅ Correct: `GET /api/v1/sessions`
   - ✅ Correct: `POST /api/v1/sessions/{sessionId}/lifecycle/refresh`
   - ❌ Previous: `PUT /api/v1/users/{userId}/sessions/{sessionId}/lifecycle/refresh`

3. **Policy List**:
   - ✅ Correct: `GET /api/v1/policies?type=POLICY_TYPE` (type parameter required)
   - ❌ Previous: `GET /api/v1/policies` (without required type parameter)

### Enhanced Features:

- **Name Resolution**: All commands now accept human-readable names (emails, group names, app names) in addition to IDs
- **Error Handling**: Improved error messages with context and recovery suggestions
- **Profile Management**: All commands properly handle profile parameters

## Support and Resources

- **Configuration**: Use `okta-cli config wizard` for initial setup
- **Help**: Run `okta-cli --help` or `okta-cli {command} --help` for detailed usage
- **Health checks**: Use `okta-cli config health` to verify configuration
- **Status**: Use `okta-cli config status` to see current configuration state
- **Testing**: Use `okta-cli config validate` to test profile configurations

## Security Considerations

1. **API Token Security**
   - Store tokens securely (environment variables, secure vaults)
   - Rotate tokens regularly
   - Use minimal required permissions
   - Monitor token usage

2. **Network Security**
   - Use HTTPS for all API calls
   - Implement proper certificate validation
   - Use secure networks for CLI operations

3. **Access Control**
   - Implement role-based access to CLI usage
   - Log all CLI operations for audit
   - Use profile-based separation for different environments

4. **Data Protection**
   - Encrypt sensitive data in transit and at rest
   - Implement proper data retention policies
   - Use secure backup procedures for configuration

This guide provides comprehensive coverage of the Okta CLI capabilities. For specific use cases or advanced scenarios, refer to the command help documentation using `okta-cli {command} --help`.

## 📋 Agent Quick Reference Summary

### Essential Commands Every Agent Must Know

```bash
# Environment verification (MANDATORY before any operations)
source venv/bin/activate
okta-cli config health --profile PROFILE_NAME
okta-cli config status

# User operations with name resolution
okta-cli users show "user@example.com" --profile PROFILE_NAME
okta-cli users create --first-name "First" --last-name "Last" --email "user@example.com" --login "user@example.com" --profile PROFILE_NAME
okta-cli users activate "user@example.com" --profile PROFILE_NAME

# Group operations with name resolution
okta-cli groups show "Group Name" --profile PROFILE_NAME
okta-cli groups add-user "Group Name" "user@example.com" --profile PROFILE_NAME
okta-cli groups list-members "Group Name" --profile PROFILE_NAME

# Application operations
okta-cli applications list --profile PROFILE_NAME
okta-cli applications show "App Name" --profile PROFILE_NAME

# Policy operations (type parameter required)
okta-cli policies list --type OKTA_SIGN_ON --profile PROFILE_NAME

# Audit and monitoring
okta-cli logs list --profile PROFILE_NAME --limit 10
okta-cli logs failed-logins --days 7 --profile PROFILE_NAME
```

### Critical Agent Requirements

1. **ALWAYS** specify `--profile PROFILE_NAME` in commands
2. **ALWAYS** verify environment before operations
3. **ALWAYS** use human-readable identifiers (emails, names)
4. **ALWAYS** use `--output json` for programmatic operations
5. **ALWAYS** handle errors gracefully with recovery suggestions
6. **NEVER** perform destructive operations without confirmation
7. **NEVER** assume resource existence without verification

### Common Agent Workflows

**User Mirroring Example**:
```bash
# 1. Check environment
okta-cli config health --profile dev-test

# 2. Get source user
okta-cli users show "source@example.com" --profile dev-test --output json

# 3. Get group memberships
okta-cli groups list --profile dev-test --output json

# 4. Create new user
okta-cli users create --first-name "New" --last-name "User" --email "new@example.com" --login "new@example.com" --profile dev-test

# 5. Add to same groups
okta-cli groups add-user "Group Name" "new@example.com" --profile dev-test

# 6. Activate user
okta-cli users activate "new@example.com" --profile dev-test

# 7. Verify result
okta-cli users show "new@example.com" --profile dev-test --output json
```

**Error Recovery Pattern**:
```bash
# When any operation fails:
okta-cli config health --profile PROFILE_NAME
okta-cli users show "user@example.com" --profile PROFILE_NAME
okta-cli logs list --profile PROFILE_NAME --limit 5
```

### Agent Success Criteria

An agent operation is considered successful when:
- [ ] Environment verification passes
- [ ] All commands execute without errors
- [ ] Results are verified and reported
- [ ] Any errors are handled with recovery suggestions
- [ ] Audit trail is maintained

### Agent Failure Handling

When operations fail, agents must:
1. Report exact error message
2. Show failed command
3. Verify environment state
4. Provide recovery steps
5. Suggest alternative approaches if applicable

This comprehensive guide ensures AI agents can effectively and safely manage Okta identity operations while maintaining security, reliability, and user-friendly experiences.