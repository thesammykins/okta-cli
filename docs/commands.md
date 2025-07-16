# Command Reference

Complete reference guide for all Okta CLI commands and their options.

## Command Structure

The Okta CLI follows a hierarchical command structure:

```bash
okta-cli [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGUMENTS]
```

### Global Options

- `--profile PROFILE` - Specify configuration profile to use
- `--output FORMAT` - Output format (table, json, csv, yaml, text)
- `--verbose` - Enable verbose output
- `--help` - Show help message

### Output Formats

All commands support multiple output formats:

- `table` - Human-readable table format (default)
- `json` - JSON format for programmatic use
- `csv` - CSV format for spreadsheet applications
- `yaml` - YAML format for configuration files
- `text` - Plain text format

Example:
```bash
okta-cli users list --output json
okta-cli groups list --output csv
okta-cli applications list --output yaml
```

## Configuration Commands

### `okta-cli config`

Manage configuration profiles and settings.

#### `okta-cli config wizard`

Interactive configuration wizard for setting up profiles.

```bash
okta-cli config wizard
```

**Interactive prompts:**
- Profile name
- Okta domain
- API token

#### `okta-cli config create`

Create a new configuration profile.

```bash
okta-cli config create PROFILE_NAME --domain DOMAIN --token TOKEN
```

**Options:**
- `--domain` - Okta domain (e.g., company.okta.com)
- `--token` - API token

**Example:**
```bash
okta-cli config create dev --domain dev.okta.com --token your-dev-token
okta-cli config create prod --domain prod.okta.com --token your-prod-token
```

#### `okta-cli config list`

List all configuration profiles.

```bash
okta-cli config list [--output FORMAT]
```

**Example:**
```bash
okta-cli config list --output table
```

#### `okta-cli config show`

Show configuration details for a profile.

```bash
okta-cli config show [PROFILE_NAME]
```

**Example:**
```bash
okta-cli config show dev
okta-cli config show  # Shows current active profile
```

#### `okta-cli config activate`

Set the active configuration profile.

```bash
okta-cli config activate PROFILE_NAME
```

**Example:**
```bash
okta-cli config activate prod
```

#### `okta-cli config delete`

Delete a configuration profile.

```bash
okta-cli config delete PROFILE_NAME [--force]
```

**Options:**
- `--force` - Skip confirmation prompt

**Example:**
```bash
okta-cli config delete old-profile --force
```

#### `okta-cli config health`

Check configuration health and connectivity.

```bash
okta-cli config health [--profile PROFILE]
```

**Example:**
```bash
okta-cli config health --profile prod
```

#### `okta-cli config validate`

Validate configuration profile settings.

```bash
okta-cli config validate [PROFILE_NAME]
```

**Example:**
```bash
okta-cli config validate dev
```

#### `okta-cli config status`

Show current configuration status.

```bash
okta-cli config status
```

#### `okta-cli config backup`

Backup configuration to a file.

```bash
okta-cli config backup [--output FILE]
```

**Options:**
- `--output` - Output file path (default: backup.json)

**Example:**
```bash
okta-cli config backup --output ~/okta-config-backup.json
```

#### `okta-cli config restore`

Restore configuration from a backup file.

```bash
okta-cli config restore FILE [--force]
```

**Options:**
- `--force` - Skip confirmation prompt

**Example:**
```bash
okta-cli config restore ~/okta-config-backup.json --force
```

## User Management Commands

### `okta-cli users`

Manage user accounts and lifecycle operations.

#### `okta-cli users list`

List all users.

```bash
okta-cli users list [--output FORMAT] [--limit N] [--profile PROFILE]
```

**Options:**
- `--limit` - Maximum number of users to return
- `--output` - Output format
- `--profile` - Configuration profile

**Example:**
```bash
okta-cli users list --output table --limit 50
okta-cli users list --output json --profile prod
```

#### `okta-cli users show`

Show detailed information about a specific user.

```bash
okta-cli users show USER_ID [--output FORMAT] [--profile PROFILE]
```

**Arguments:**
- `USER_ID` - User ID, email, or login

**Example:**
```bash
okta-cli users show user123
okta-cli users show john.doe@example.com --output json
```

#### `okta-cli users search`

Search for users by query.

```bash
okta-cli users search --query QUERY [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--query` - Search query string

**Example:**
```bash
okta-cli users search --query "john.doe"
okta-cli users search --query "engineering" --output json
```

#### `okta-cli users create`

Create a new user account.

```bash
okta-cli users create --first-name FIRST --last-name LAST --email EMAIL --login LOGIN [OPTIONS]
```

**Required Options:**
- `--first-name` - User's first name
- `--last-name` - User's last name
- `--email` - User's email address
- `--login` - User's login identifier

**Optional Options:**
- `--profile` - Configuration profile
- `--output` - Output format

**Example:**
```bash
okta-cli users create \
  --first-name John \
  --last-name Doe \
  --email john.doe@example.com \
  --login john.doe@example.com \
  --profile prod
```

#### `okta-cli users update`

Update an existing user's information.

```bash
okta-cli users update USER_ID [OPTIONS]
```

**Options:**
- `--first-name` - Update first name
- `--last-name` - Update last name
- `--email` - Update email address
- `--profile` - Configuration profile

**Example:**
```bash
okta-cli users update user123 \
  --first-name Jonathan \
  --email new.email@example.com \
  --profile prod
```

#### `okta-cli users activate`

Activate a user account.

```bash
okta-cli users activate USER_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli users activate user123 --profile prod
okta-cli users activate john.doe@example.com
```

#### `okta-cli users deactivate`

Deactivate a user account.

```bash
okta-cli users deactivate USER_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli users deactivate user123 --profile prod
```

#### `okta-cli users suspend`

Suspend a user account.

```bash
okta-cli users suspend USER_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli users suspend user123 --profile prod
```

#### `okta-cli users unsuspend`

Unsuspend a user account.

```bash
okta-cli users unsuspend USER_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli users unsuspend user123 --profile prod
```

#### `okta-cli users reset-password`

Reset a user's password.

```bash
okta-cli users reset-password USER_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli users reset-password user123 --profile prod
```

#### `okta-cli users assign-app`

Assign an application to a user.

```bash
okta-cli users assign-app USER_ID APP_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli users assign-app user123 app456 --profile prod
```

#### `okta-cli users unassign-app`

Unassign an application from a user.

```bash
okta-cli users unassign-app USER_ID APP_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli users unassign-app user123 app456 --profile prod
```

#### `okta-cli users list-app-assignments`

List application assignments for a user.

```bash
okta-cli users list-app-assignments USER_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli users list-app-assignments user123 --output json
```

## Group Management Commands

### `okta-cli groups`

Manage groups and group memberships.

#### `okta-cli groups list`

List all groups.

```bash
okta-cli groups list [--output FORMAT] [--limit N] [--profile PROFILE]
```

**Options:**
- `--limit` - Maximum number of groups to return
- `--output` - Output format
- `--profile` - Configuration profile

**Example:**
```bash
okta-cli groups list --output table
okta-cli groups list --output json --profile prod
```

#### `okta-cli groups show`

Show detailed information about a specific group.

```bash
okta-cli groups show GROUP_ID [--output FORMAT] [--profile PROFILE]
```

**Arguments:**
- `GROUP_ID` - Group ID or name

**Example:**
```bash
okta-cli groups show group123
okta-cli groups show "Engineering Team" --output json
```

#### `okta-cli groups create`

Create a new group.

```bash
okta-cli groups create --name NAME --description DESCRIPTION [--profile PROFILE]
```

**Options:**
- `--name` - Group name (required)
- `--description` - Group description (required)
- `--profile` - Configuration profile

**Example:**
```bash
okta-cli groups create \
  --name "Engineering Team" \
  --description "Software engineers" \
  --profile prod
```

#### `okta-cli groups update`

Update an existing group.

```bash
okta-cli groups update GROUP_ID [OPTIONS]
```

**Options:**
- `--name` - Update group name
- `--description` - Update group description
- `--profile` - Configuration profile

**Example:**
```bash
okta-cli groups update group123 \
  --name "Senior Engineering Team" \
  --description "Senior software engineers" \
  --profile prod
```

#### `okta-cli groups delete`

Delete a group.

```bash
okta-cli groups delete GROUP_ID [--force] [--profile PROFILE]
```

**Options:**
- `--force` - Skip confirmation prompt

**Example:**
```bash
okta-cli groups delete group123 --force --profile prod
```

#### `okta-cli groups add-user`

Add a user to a group.

```bash
okta-cli groups add-user GROUP_ID USER_ID [--profile PROFILE]
```

**Arguments:**
- `GROUP_ID` - Group ID or name
- `USER_ID` - User ID, email, or login

**Example:**
```bash
okta-cli groups add-user group123 user456 --profile prod
okta-cli groups add-user "Engineering Team" john.doe@example.com
```

#### `okta-cli groups remove-user`

Remove a user from a group.

```bash
okta-cli groups remove-user GROUP_ID USER_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli groups remove-user group123 user456 --profile prod
okta-cli groups remove-user "Engineering Team" john.doe@example.com
```

#### `okta-cli groups list-users`

List users in a group.

```bash
okta-cli groups list-users GROUP_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli groups list-users group123 --output json
okta-cli groups list-users "Engineering Team" --output table
```

## Application Management Commands

### `okta-cli applications`

Manage applications and their configurations.

#### `okta-cli applications list`

List all applications.

```bash
okta-cli applications list [--output FORMAT] [--limit N] [--profile PROFILE]
```

**Options:**
- `--limit` - Maximum number of applications to return
- `--output` - Output format
- `--profile` - Configuration profile

**Example:**
```bash
okta-cli applications list --output table
okta-cli applications list --output json --profile prod
```

#### `okta-cli applications show`

Show detailed information about a specific application.

```bash
okta-cli applications show APP_ID [--output FORMAT] [--profile PROFILE]
```

**Arguments:**
- `APP_ID` - Application ID or name

**Example:**
```bash
okta-cli applications show app123
okta-cli applications show "My Application" --output json
```

#### `okta-cli applications create`

Create a new application.

```bash
okta-cli applications create --name NAME --label LABEL --sign-on-mode MODE [--profile PROFILE]
```

**Options:**
- `--name` - Application name (required)
- `--label` - Application label (required)
- `--sign-on-mode` - Sign-on mode (required)
- `--profile` - Configuration profile

**Sign-on modes:**
- `BOOKMARK`
- `BASIC_AUTH`
- `BROWSER_PLUGIN`
- `SECURE_PASSWORD_STORE`
- `SAML_2_0`
- `WS_FEDERATION`
- `AUTO_LOGIN`

**Example:**
```bash
okta-cli applications create \
  --name "My App" \
  --label "My Application" \
  --sign-on-mode SAML_2_0 \
  --profile prod
```

#### `okta-cli applications update`

Update an existing application.

```bash
okta-cli applications update APP_ID [OPTIONS]
```

**Options:**
- `--name` - Update application name
- `--label` - Update application label
- `--status` - Update application status
- `--profile` - Configuration profile

**Example:**
```bash
okta-cli applications update app123 \
  --name "Updated App Name" \
  --status ACTIVE \
  --profile prod
```

#### `okta-cli applications delete`

Delete an application.

```bash
okta-cli applications delete APP_ID [--force] [--profile PROFILE]
```

**Options:**
- `--force` - Skip confirmation prompt

**Example:**
```bash
okta-cli applications delete app123 --force --profile prod
```

#### `okta-cli applications activate`

Activate an application.

```bash
okta-cli applications activate APP_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli applications activate app123 --profile prod
```

#### `okta-cli applications deactivate`

Deactivate an application.

```bash
okta-cli applications deactivate APP_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli applications deactivate app123 --profile prod
```

#### `okta-cli applications list-users`

List users assigned to an application.

```bash
okta-cli applications list-users APP_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli applications list-users app123 --output json
```

#### `okta-cli applications list-groups`

List groups assigned to an application.

```bash
okta-cli applications list-groups APP_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli applications list-groups app123 --output json
```

## Session Management Commands

### `okta-cli sessions`

Manage user sessions and session lifecycle.

#### `okta-cli sessions list`

List sessions for a user.

```bash
okta-cli sessions list USER_ID [--output FORMAT] [--profile PROFILE]
```

**Arguments:**
- `USER_ID` - User ID, email, or login

**Example:**
```bash
okta-cli sessions list user123 --output table
okta-cli sessions list john.doe@example.com --output json
```

#### `okta-cli sessions show`

Show detailed information about a specific session.

```bash
okta-cli sessions show USER_ID SESSION_ID [--output FORMAT] [--profile PROFILE]
```

**Arguments:**
- `USER_ID` - User ID, email, or login
- `SESSION_ID` - Session ID

**Example:**
```bash
okta-cli sessions show user123 session456 --output json
```

#### `okta-cli sessions extend`

Extend a user session.

```bash
okta-cli sessions extend USER_ID SESSION_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli sessions extend user123 session456 --profile prod
```

#### `okta-cli sessions clear`

Clear all sessions for a user.

```bash
okta-cli sessions clear USER_ID [--force] [--oauth-only] [--profile PROFILE]
```

**Options:**
- `--force` - Skip confirmation prompt
- `--oauth-only` - Clear only OAuth sessions

**Example:**
```bash
okta-cli sessions clear user123 --force --profile prod
okta-cli sessions clear user123 --oauth-only
```

#### `okta-cli sessions stats`

Show session statistics.

```bash
okta-cli sessions stats [--days N] [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--days` - Number of days to analyze (default: 30)

**Example:**
```bash
okta-cli sessions stats --days 30 --output json
```

#### `okta-cli sessions active`

List active sessions.

```bash
okta-cli sessions active [--limit N] [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--limit` - Maximum number of sessions to return

**Example:**
```bash
okta-cli sessions active --limit 50 --output table
```

## Policy Management Commands

### `okta-cli policies`

Manage policies and group rules.

#### `okta-cli policies list`

List policies by type.

```bash
okta-cli policies list --type TYPE [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--type` - Policy type (required)

**Policy types:**
- `OKTA_SIGN_ON`
- `PASSWORD`
- `MFA_ENROLL`
- `OAUTH_AUTHORIZATION_POLICY`
- `IDP_DISCOVERY`

**Example:**
```bash
okta-cli policies list --type PASSWORD --output table
okta-cli policies list --type OKTA_SIGN_ON --output json
```

#### `okta-cli policies show`

Show detailed information about a specific policy.

```bash
okta-cli policies show POLICY_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli policies show policy123 --output json
```

#### `okta-cli policies activate`

Activate a policy.

```bash
okta-cli policies activate POLICY_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli policies activate policy123 --profile prod
```

#### `okta-cli policies deactivate`

Deactivate a policy.

```bash
okta-cli policies deactivate POLICY_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli policies deactivate policy123 --profile prod
```

### Group Rules Management

#### `okta-cli policies rules list`

List all group rules.

```bash
okta-cli policies rules list [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli policies rules list --output table
```

#### `okta-cli policies rules show`

Show detailed information about a specific group rule.

```bash
okta-cli policies rules show RULE_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli policies rules show rule123 --output json
```

#### `okta-cli policies rules create`

Create a new group rule.

```bash
okta-cli policies rules create --name NAME --expression EXPRESSION --group-id GROUP_ID [--profile PROFILE]
```

**Options:**
- `--name` - Rule name (required)
- `--expression` - Rule expression (required)
- `--group-id` - Target group ID (required)

**Example:**
```bash
okta-cli policies rules create \
  --name "Engineering Rule" \
  --expression 'user.department=="Engineering"' \
  --group-id group123 \
  --profile prod
```

#### `okta-cli policies rules activate`

Activate a group rule.

```bash
okta-cli policies rules activate RULE_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli policies rules activate rule123 --profile prod
```

#### `okta-cli policies rules deactivate`

Deactivate a group rule.

```bash
okta-cli policies rules deactivate RULE_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli policies rules deactivate rule123 --profile prod
```

#### `okta-cli policies rules delete`

Delete a group rule.

```bash
okta-cli policies rules delete RULE_ID [--force] [--profile PROFILE]
```

**Options:**
- `--force` - Skip confirmation prompt

**Example:**
```bash
okta-cli policies rules delete rule123 --force --profile prod
```

## Authorization Server Management Commands

### `okta-cli authorization`

Manage OAuth authorization servers and scopes.

#### `okta-cli authorization list`

List all authorization servers.

```bash
okta-cli authorization list [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli authorization list --output table
okta-cli authorization list --output json --profile prod
```

#### `okta-cli authorization show`

Show detailed information about a specific authorization server.

```bash
okta-cli authorization show SERVER_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli authorization show server123 --output json
```

#### `okta-cli authorization create`

Create a new authorization server.

```bash
okta-cli authorization create --name NAME --audience AUDIENCE [--description DESC] [--profile PROFILE]
```

**Options:**
- `--name` - Server name (required)
- `--audience` - Audience identifier (required)
- `--description` - Server description

**Example:**
```bash
okta-cli authorization create \
  --name "My API Server" \
  --description "API authorization server" \
  --audience "api://my-api" \
  --profile prod
```

#### `okta-cli authorization activate`

Activate an authorization server.

```bash
okta-cli authorization activate SERVER_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli authorization activate server123 --profile prod
```

#### `okta-cli authorization deactivate`

Deactivate an authorization server.

```bash
okta-cli authorization deactivate SERVER_ID [--profile PROFILE]
```

**Example:**
```bash
okta-cli authorization deactivate server123 --profile prod
```

#### `okta-cli authorization delete`

Delete an authorization server.

```bash
okta-cli authorization delete SERVER_ID [--force] [--profile PROFILE]
```

**Options:**
- `--force` - Skip confirmation prompt

**Example:**
```bash
okta-cli authorization delete server123 --force --profile prod
```

### Scope Management

#### `okta-cli authorization scopes list`

List scopes for an authorization server.

```bash
okta-cli authorization scopes list SERVER_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli authorization scopes list server123 --output json
```

#### `okta-cli authorization scopes create`

Create a new scope.

```bash
okta-cli authorization scopes create SERVER_ID --name NAME --description DESC [--consent CONSENT] [--profile PROFILE]
```

**Options:**
- `--name` - Scope name (required)
- `--description` - Scope description (required)
- `--consent` - Consent requirement (REQUIRED, IMPLICIT)

**Example:**
```bash
okta-cli authorization scopes create server123 \
  --name "read:users" \
  --description "Read user data" \
  --consent REQUIRED \
  --profile prod
```

## Event Log Analysis Commands

### `okta-cli logs`

Query and analyze event logs.

#### `okta-cli logs list`

List recent log events.

```bash
okta-cli logs list [--limit N] [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--limit` - Maximum number of events to return

**Example:**
```bash
okta-cli logs list --limit 100 --output table
okta-cli logs list --output json --profile prod
```

#### `okta-cli logs show`

Show detailed information about a specific log event.

```bash
okta-cli logs show LOG_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli logs show log-uuid-123 --output json
```

#### `okta-cli logs search`

Search logs with advanced filters.

```bash
okta-cli logs search [--event-type TYPE] [--outcome OUTCOME] [--days N] [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--event-type` - Filter by event type
- `--outcome` - Filter by outcome (SUCCESS, FAILURE, SKIPPED, ALLOW, DENY, CHALLENGE, UNKNOWN)
- `--days` - Number of days to search back

**Common event types:**
- `user.session.start`
- `user.session.end`
- `user.authentication.sso`
- `user.authentication.auth_via_mfa`
- `user.account.lock`
- `user.account.unlock`
- `application.user_membership.add`
- `application.user_membership.remove`

**Example:**
```bash
okta-cli logs search \
  --event-type "user.session.start" \
  --outcome SUCCESS \
  --days 7 \
  --output json
```

#### `okta-cli logs failed-logins`

Get failed login attempts.

```bash
okta-cli logs failed-logins [--days N] [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--days` - Number of days to analyze (default: 1)

**Example:**
```bash
okta-cli logs failed-logins --days 1 --output json
okta-cli logs failed-logins --days 7 --output table
```

#### `okta-cli logs suspicious`

Get suspicious activities.

```bash
okta-cli logs suspicious [--days N] [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--days` - Number of days to analyze (default: 7)

**Example:**
```bash
okta-cli logs suspicious --days 7 --output table
okta-cli logs suspicious --days 30 --output json
```

#### `okta-cli logs stats`

Generate log statistics.

```bash
okta-cli logs stats [--days N] [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--days` - Number of days to analyze (default: 30)

**Example:**
```bash
okta-cli logs stats --days 30 --output json
```

## Multi-Factor Authentication Commands

### `okta-cli factors`

Manage MFA factors and enrollment.

#### `okta-cli factors list`

List MFA factors for a user.

```bash
okta-cli factors list USER_ID [--output FORMAT] [--profile PROFILE]
```

**Arguments:**
- `USER_ID` - User ID, email, or login

**Example:**
```bash
okta-cli factors list user123 --output table
okta-cli factors list john.doe@example.com --output json
```

#### `okta-cli factors show`

Show detailed information about a specific factor.

```bash
okta-cli factors show USER_ID FACTOR_ID [--output FORMAT] [--profile PROFILE]
```

**Arguments:**
- `USER_ID` - User ID, email, or login
- `FACTOR_ID` - Factor ID

**Example:**
```bash
okta-cli factors show user123 factor456 --output json
```

#### `okta-cli factors enroll`

Enroll a user in an MFA factor.

```bash
okta-cli factors enroll USER_ID --factor-type TYPE [OPTIONS] [--profile PROFILE]
```

**Options:**
- `--factor-type` - Factor type (required)
- `--phone-number` - Phone number (for SMS/voice factors)
- `--profile` - Configuration profile

**Factor types:**
- `sms` - SMS text message
- `call` - Voice call
- `token:software:totp` - Software TOTP (like Google Authenticator)
- `token:hardware` - Hardware token
- `push` - Push notification
- `question` - Security question

**Example:**
```bash
# Enroll SMS factor
okta-cli factors enroll user123 \
  --factor-type sms \
  --phone-number "+1234567890" \
  --profile prod

# Enroll TOTP factor
okta-cli factors enroll user123 \
  --factor-type token:software:totp \
  --profile prod
```

#### `okta-cli factors activate`

Activate an enrolled factor.

```bash
okta-cli factors activate USER_ID FACTOR_ID --passcode PASSCODE [--profile PROFILE]
```

**Options:**
- `--passcode` - Activation passcode (required)

**Example:**
```bash
okta-cli factors activate user123 factor456 --passcode 123456 --profile prod
```

#### `okta-cli factors verify`

Verify a factor.

```bash
okta-cli factors verify USER_ID FACTOR_ID --passcode PASSCODE [--profile PROFILE]
```

**Options:**
- `--passcode` - Verification passcode (required)

**Example:**
```bash
okta-cli factors verify user123 factor456 --passcode 123456 --profile prod
```

#### `okta-cli factors reset`

Reset/remove a factor.

```bash
okta-cli factors reset USER_ID FACTOR_ID [--force] [--profile PROFILE]
```

**Options:**
- `--force` - Skip confirmation prompt

**Example:**
```bash
okta-cli factors reset user123 factor456 --force --profile prod
```

#### `okta-cli factors catalog list`

List available factor catalog for a user.

```bash
okta-cli factors catalog list USER_ID [--output FORMAT] [--profile PROFILE]
```

**Example:**
```bash
okta-cli factors catalog list user123 --output json
```

#### `okta-cli factors stats`

Generate MFA adoption statistics.

```bash
okta-cli factors stats [--limit N] [--output FORMAT] [--profile PROFILE]
```

**Options:**
- `--limit` - Maximum number of users to analyze

**Example:**
```bash
okta-cli factors stats --limit 1000 --output json
```

## Common Command Patterns

### Environment Variables

You can use environment variables to avoid specifying common options:

```bash
# Set profile
export OKTA_PROFILE=production

# Set domain and token
export OKTA_DOMAIN=company.okta.com
export OKTA_TOKEN=your-api-token

# Enable debug mode
export OKTA_DEBUG=true

# Then use commands without --profile
okta-cli users list
okta-cli groups list
```

### Combining Commands

Use command output in scripts:

```bash
# Export users to CSV
okta-cli users list --output csv > users.csv

# Get failed logins and save to file
okta-cli logs failed-logins --days 7 --output json > failed_logins.json

# Create user and immediately add to group
USER_EMAIL="new.user@example.com"
okta-cli users create --first-name New --last-name User --email $USER_EMAIL --login $USER_EMAIL
okta-cli groups add-user "Everyone" $USER_EMAIL
okta-cli users activate $USER_EMAIL
```

### Error Handling

Always check command success:

```bash
if okta-cli users show user@example.com > /dev/null 2>&1; then
    echo "User exists"
else
    echo "User not found"
fi
```

### Batch Operations

Process multiple items:

```bash
# Get all users and process each
okta-cli users list --output json | jq -r '.[].id' | while read user_id; do
    echo "Processing user: $user_id"
    okta-cli users show "$user_id" --output json
done
```

## Tips and Best Practices

### 1. Use Profiles for Different Environments

```bash
# Set up different environments
okta-cli config create dev --domain dev.okta.com --token dev-token
okta-cli config create prod --domain prod.okta.com --token prod-token

# Use specific profiles
okta-cli users list --profile dev
okta-cli users list --profile prod
```

### 2. Always Specify Output Format for Scripts

```bash
# For programmatic use
okta-cli users list --output json

# For human reading
okta-cli users list --output table
```

### 3. Use Limits for Large Data Sets

```bash
# Limit results to avoid overwhelming output
okta-cli users list --limit 50
okta-cli logs list --limit 100
```

### 4. Verify Operations

```bash
# Always verify after making changes
okta-cli users create --first-name John --last-name Doe --email john@example.com --login john@example.com
okta-cli users show john@example.com
```

### 5. Use Descriptive Names

```bash
# Use human-readable identifiers
okta-cli groups show "Engineering Team"
okta-cli users show "john.doe@example.com"
```

For more detailed information about each command, use the `--help` option:

```bash
okta-cli --help
okta-cli users --help
okta-cli users create --help
```