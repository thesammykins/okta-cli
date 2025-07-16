# Enhanced Configuration

The Okta CLI tool includes enhanced configuration management with support for multiple profiles, environment variables, and configuration validation.

## Features Overview

### Multiple Profile Support
- **Profile Management**: Create, update, delete, and switch between multiple profiles
- **Active Profile**: Set and track the currently active profile
- **Profile Validation**: Validate profile configurations and connectivity
- **Profile Migration**: Migrate from legacy configuration formats

### Environment Variable Configuration
- **Environment Precedence**: Environment variables take precedence over profile configuration
- **Profile-Specific Variables**: Support for profile-specific environment variables
- **Complete Configuration**: Automatic detection of complete environment configuration

### Configuration Validation
- **Input Validation**: Validate domain, token, and profile name formats
- **Connectivity Testing**: Test connectivity to Okta API
- **Health Checks**: Comprehensive health checks for configurations
- **Real-time Validation**: Validate configurations before use

### Backup and Restore
- **Configuration Backup**: Create backups of profile configurations
- **Configuration Restore**: Restore from backup files
- **Import/Export**: Import and export configuration files
- **Legacy Migration**: Migrate from legacy configuration formats

## Profile Management

### Creating Profiles

Create a new profile with domain and token:

```bash
# Create a new profile
okta-cli config create dev --domain dev.okta.com --token your-dev-token

# Create and set as active profile
okta-cli config create prod --domain prod.okta.com --token your-prod-token --set-active
```

### Listing Profiles

List all configured profiles:

```bash
okta-cli config list
```

Output:
```
Configuration profiles:
* dev
    Domain: dev.okta.com
    Created: 1640995200.0
    Last Used: 1640995200.0

  prod
    Domain: prod.okta.com
    Created: 1640995300.0
    Last Used: Never
```

### Switching Profiles

Activate a specific profile:

```bash
# Set active profile
okta-cli config activate dev

# Use profile for a single command
okta-cli users list --profile prod
```

### Updating Profiles

Update profile configuration:

```bash
# Update domain
okta-cli config update dev --domain new-dev.okta.com

# Update token
okta-cli config update dev --token new-dev-token

# Update both
okta-cli config update dev --domain new-dev.okta.com --token new-dev-token
```

### Deleting Profiles

Delete a profile:

```bash
# Delete with confirmation
okta-cli config delete dev

# Force delete without confirmation
okta-cli config delete dev --force
```

### Profile Information

Show profile details:

```bash
# Show active profile
okta-cli config show

# Show specific profile
okta-cli config show dev
```

Output:
```
Profile: dev
Domain: dev.okta.com
Token: ********************...abc123
Created: 1640995200.0
Last Used: 1640995200.0
```

## Environment Variable Configuration

### Standard Environment Variables

The CLI supports standard environment variables:

```bash
# Basic configuration
export OKTA_DOMAIN=env.okta.com
export OKTA_TOKEN=your-env-token

# Profile selection
export OKTA_PROFILE=dev
```

### Profile-Specific Environment Variables

Use profile-specific environment variables:

```bash
# Development environment
export OKTA_DEV_DOMAIN=dev.okta.com
export OKTA_DEV_TOKEN=dev-token

# Production environment
export OKTA_PROD_DOMAIN=prod.okta.com
export OKTA_PROD_TOKEN=prod-token
```

### Environment Variable Precedence

Configuration precedence (highest to lowest):
1. Profile-specific environment variables (`OKTA_DEV_DOMAIN`, `OKTA_DEV_TOKEN`)
2. Standard environment variables (`OKTA_DOMAIN`, `OKTA_TOKEN`)
3. Profile configuration files
4. Default profile configuration

### Checking Environment Configuration

View current environment configuration:

```bash
okta-cli config env
```

Output:
```
Environment Configuration:
OKTA_DOMAIN: env.okta.com
OKTA_TOKEN: Set
OKTA_PROFILE: dev
✓ Complete configuration available via environment variables
```

## Configuration Validation

### Profile Validation

Validate a profile configuration:

```bash
# Validate active profile
okta-cli config validate

# Validate specific profile
okta-cli config validate dev
```

Output:
```
Profile: dev
Valid: ✓
No issues found.
```

### Health Checks

Perform comprehensive health checks:

```bash
# Health check for active profile
okta-cli config health

# Health check for specific profile
okta-cli config health dev
```

Output:
```
Running health check...
Status: healthy
Connectivity: ✓
Authentication: ✓
Response Time: 0.45s
```

### Current Configuration

View the current effective configuration:

```bash
okta-cli config current
```

Output:
```
Current Configuration:
Domain: dev.okta.com
Token: ********************...abc123
Source: Environment variables
```

## Backup and Restore

### Creating Backups

Create configuration backups:

```bash
# Create automatic backup
okta-cli config backup

# Create backup to specific file
okta-cli config backup --output /path/to/backup.json
```

### Restoring from Backup

Restore configuration from backup:

```bash
# Restore with confirmation
okta-cli config restore /path/to/backup.json

# Force restore without confirmation
okta-cli config restore /path/to/backup.json --force
```

### Export and Import

Export and import configuration:

```bash
# Export configuration
okta-cli config export /path/to/export.json

# Import configuration
okta-cli config import /path/to/export.json --force
```

## Migration

### Legacy Configuration Migration

Migrate from legacy configuration formats:

```bash
okta-cli config migrate /path/to/legacy/config.json
```

This will:
- Read the legacy configuration file
- Create a "default" profile with the legacy settings
- Preserve existing profiles

## Advanced Usage

### Using Profiles in Scripts

Environment variable approach:
```bash
#!/bin/bash
export OKTA_PROFILE=dev
okta-cli users list
```

Command-line approach:
```bash
#!/bin/bash
okta-cli users list --profile dev
okta-cli groups list --profile dev
```

### Multiple Environment Setup

Development environment:
```bash
export OKTA_DEV_DOMAIN=dev.okta.com
export OKTA_DEV_TOKEN=dev-token
okta-cli users list --profile dev
```

Production environment:
```bash
export OKTA_PROD_DOMAIN=prod.okta.com
export OKTA_PROD_TOKEN=prod-token
okta-cli users list --profile prod
```

### Configuration Validation in CI/CD

Validate configuration before use:
```bash
#!/bin/bash
if okta-cli config validate production; then
    echo "Configuration valid, proceeding..."
    okta-cli users list --profile production
else
    echo "Configuration invalid, aborting..."
    exit 1
fi
```

## Configuration File Structure

### Profile Storage

Profiles are stored in `~/.okta/profiles.json`:

```json
{
  "dev": {
    "domain": "dev.okta.com",
    "token": "dev-token",
    "created_at": 1640995200.0,
    "last_used": 1640995200.0
  },
  "prod": {
    "domain": "prod.okta.com",
    "token": "prod-token",
    "created_at": 1640995300.0,
    "last_used": 1640995300.0
  }
}
```

### Active Profile

The active profile is stored in `~/.okta/active_profile`:

```
dev
```

### File Permissions

Configuration files have restrictive permissions:
- Directory: `~/.okta/` (permissions: 700)
- Profile file: `~/.okta/profiles.json` (permissions: 600)
- Active profile file: `~/.okta/active_profile` (permissions: 600)

## Best Practices

### Profile Organization

1. **Environment-Based Profiles**: Create profiles for different environments
   ```bash
   okta-cli config create dev --domain dev.okta.com --token dev-token
   okta-cli config create staging --domain staging.okta.com --token staging-token
   okta-cli config create prod --domain prod.okta.com --token prod-token
   ```

2. **Purpose-Based Profiles**: Create profiles for different purposes
   ```bash
   okta-cli config create readonly --domain org.okta.com --token readonly-token
   okta-cli config create admin --domain org.okta.com --token admin-token
   ```

### Environment Variables

1. **Use Environment Variables in CI/CD**:
   ```bash
   export OKTA_DOMAIN=$CI_OKTA_DOMAIN
   export OKTA_TOKEN=$CI_OKTA_TOKEN
   okta-cli users list
   ```

2. **Profile-Specific Variables for Multi-Tenant**:
   ```bash
   export OKTA_TENANT1_DOMAIN=tenant1.okta.com
   export OKTA_TENANT1_TOKEN=tenant1-token
   export OKTA_TENANT2_DOMAIN=tenant2.okta.com
   export OKTA_TENANT2_TOKEN=tenant2-token
   ```

### Security Considerations

1. **Token Rotation**: Regularly rotate API tokens
2. **Backup Encryption**: Store backups securely
3. **Environment Variables**: Use secure environment variable storage
4. **Profile Cleanup**: Remove unused profiles

### Validation and Health Checks

1. **Pre-deployment Validation**:
   ```bash
   okta-cli config validate production
   okta-cli config health production
   ```

2. **Regular Health Checks**:
   ```bash
   for profile in dev staging prod; do
       echo "Checking $profile..."
       okta-cli config health $profile
   done
   ```

## Troubleshooting

### Common Issues

**Profile Not Found**
```bash
Error: Profile 'dev' not found
```
Solution: Create the profile or check the profile name

**Invalid Configuration**
```bash
Profile: dev
Valid: ✗
Issues:
  - Invalid domain format
  - Cannot connect to Okta API
```
Solution: Update the profile with correct domain and token

**Environment Variable Issues**
```bash
Error: Profile 'default' not found and no environment configuration available
```
Solution: Set environment variables or create a default profile

### Debug Mode

Enable debug mode for detailed information:
```bash
export OKTA_DEBUG=true
okta-cli config validate dev
```

### Configuration Reset

Reset configuration if needed:
```bash
# Backup current configuration
okta-cli config backup --output backup.json

# Remove all profiles (careful!)
rm ~/.okta/profiles.json ~/.okta/active_profile

# Start fresh
okta-cli config create default --domain your.okta.com --token your-token
```

## Integration Examples

### Docker Environment

```dockerfile
FROM python:3.9-slim

# Install CLI
RUN pip install okta-cli

# Set environment variables
ENV OKTA_DOMAIN=your.okta.com
ENV OKTA_TOKEN=your-token

# Use CLI
CMD ["okta-cli", "users", "list"]
```

### GitHub Actions

```yaml
name: Okta User Management
on: [push]
jobs:
  okta-operations:
    runs-on: ubuntu-latest
    steps:
      - name: Setup Okta CLI
        env:
          OKTA_DOMAIN: ${{ secrets.OKTA_DOMAIN }}
          OKTA_TOKEN: ${{ secrets.OKTA_TOKEN }}
        run: |
          pip install okta-cli
          okta-cli config health
          okta-cli users list
```

### Shell Script Integration

```bash
#!/bin/bash
set -e

# Configuration
PROFILE=${1:-default}

# Validate configuration
if ! okta-cli config validate $PROFILE; then
    echo "Configuration invalid for profile: $PROFILE"
    exit 1
fi

# Perform operations
echo "Using profile: $PROFILE"
okta-cli users list --profile $PROFILE
okta-cli groups list --profile $PROFILE
```