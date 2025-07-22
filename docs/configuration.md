# Configuration Guide

Complete guide to configuring and managing the Okta CLI tool.

## Overview

The Okta CLI uses profile-based configuration to manage multiple Okta environments. Configuration is stored securely in your home directory and supports multiple profiles for different environments (development, staging, production).

## Configuration Storage

### Configuration Directory

Configuration is stored using the enhanced configuration system:
- **Location**: `~/.okta/`
- **Main file**: `profiles.json`
- **Active profile**: `active_profile`
- **Permissions**: Automatically set to restrictive permissions (700 for directory, 600 for files)

### Configuration File Format

The enhanced configuration system uses JSON format for profiles:

```json
{
  "default": {
    "domain": "your.okta.com",
    "token": "your-api-token",
    "created_at": 1640995200.0,
    "last_used": 1640995200.0
  },
  "development": {
    "domain": "dev.okta.com",
    "token": "dev-api-token",
    "created_at": 1640995300.0,
    "last_used": 1640995300.0
  },
  "production": {
    "domain": "prod.okta.com",
    "token": "prod-api-token",
    "created_at": 1640995400.0,
    "last_used": 1640995400.0
  }
}
```

## Profile Management

### Creating Profiles

#### Interactive Configuration Wizard

The easiest way to create your first profile:

```bash
okta-cli config wizard
```

The wizard will prompt you for:
- **Profile name** (e.g., "default", "production", "development")
- **Okta domain** (e.g., "company.okta.com")
- **API token** (create one in Okta Admin Console → Security → API)

#### Manual Profile Creation

Create profiles manually:

```bash
# Create a development profile
okta-cli config create dev --domain dev.okta.com --token your-dev-token

# Create a production profile
okta-cli config create prod --domain prod.okta.com --token your-prod-token

# Create a staging profile
okta-cli config create staging --domain staging.okta.com --token your-staging-token
```

### Managing Profiles

#### List Available Profiles

```bash
okta-cli config list
```

Output shows:
- Profile names
- Associated domains
- Active status

#### Show Profile Details

```bash
# Show specific profile
okta-cli config show production

# Show current active profile
okta-cli config show
```

#### Activate a Profile

Set the default profile for commands:

```bash
okta-cli config activate production
```

Once activated, all commands will use this profile unless explicitly overridden.

#### Delete a Profile

```bash
# With confirmation
okta-cli config delete old-profile

# Skip confirmation
okta-cli config delete old-profile --force
```

## Environment Variables

### Basic Environment Variables

You can use environment variables instead of or in addition to configuration files:

```bash
# Set domain and token
export OKTA_DOMAIN=company.okta.com
export OKTA_TOKEN=your-api-token

# Set active profile
export OKTA_PROFILE=production

# Enable debug mode
export OKTA_DEBUG=true
```

### Environment-Specific Variables

For multiple environments, use profile-specific variables:

```bash
# Development environment
export OKTA_DEV_DOMAIN=dev.okta.com
export OKTA_DEV_TOKEN=dev-token

# Production environment
export OKTA_PROD_DOMAIN=prod.okta.com
export OKTA_PROD_TOKEN=prod-token

# Staging environment
export OKTA_STAGING_DOMAIN=staging.okta.com
export OKTA_STAGING_TOKEN=staging-token
```

### Priority Order

Configuration values are resolved in this order (highest to lowest priority):

1. **Command-line options** (`--profile`, `--domain`, `--token`)
2. **Environment variables** (`OKTA_PROFILE`, `OKTA_DOMAIN`, `OKTA_TOKEN`)
3. **Profile configuration** (`~/.okta/profiles.json`)
4. **Default values**

## API Token Management

### Creating API Tokens

1. Log in to your Okta Admin Console
2. Go to **Security** → **API**
3. Click **Create Token**
4. Enter a descriptive name
5. Copy the token value (it will only be shown once)

### Token Permissions

Ensure your API token has the appropriate permissions:

#### Required Permissions

- **User Management**: Read, Create, Update, Delete users
- **Group Management**: Read, Create, Update, Delete groups
- **Application Management**: Read, Create, Update applications
- **Policy Management**: Read policies and rules
- **Log Management**: Read system logs
- **Session Management**: Read and manage user sessions

#### Recommended Permissions

- **Super Admin**: Full access to all features
- **Organization Admin**: Access to most features
- **API Access Management Admin**: For authorization server management
- **Help Desk Admin**: For user support operations

### Token Security Best Practices

1. **Use unique tokens** for each environment
2. **Rotate tokens regularly** (every 90 days recommended)
3. **Use minimal required permissions**
4. **Store tokens securely** (use environment variables or secure vaults)
5. **Monitor token usage** through audit logs
6. **Revoke unused tokens** immediately

## Configuration Validation

### Health Checks

Verify your configuration is working correctly:

```bash
# Check all aspects of configuration
okta-cli config health

# Check specific profile
okta-cli config health --profile production
```

Health check verifies:
- Configuration file exists and is readable
- Profile exists and is complete
- Domain is accessible
- API token is valid
- Network connectivity is working

### Profile Validation

Validate specific profiles:

```bash
# Validate active profile
okta-cli config validate

# Validate specific profile
okta-cli config validate production
```

Validation checks:
- Profile exists in configuration
- Domain format is correct
- Token format is valid
- API connectivity works
- Required permissions are available

### Configuration Status

Check current configuration status:

```bash
okta-cli config status
```

Shows:
- Active profile
- Configuration file location
- Profile validity
- Last validation time

## Advanced Configuration

### Multiple Environment Setup

Set up a complete multi-environment configuration:

```bash
# Development environment
okta-cli config create dev \
  --domain dev.okta.com \
  --token $DEV_TOKEN

# Staging environment
okta-cli config create staging \
  --domain staging.okta.com \
  --token $STAGING_TOKEN

# Production environment
okta-cli config create prod \
  --domain prod.okta.com \
  --token $PROD_TOKEN

# Set production as default
okta-cli config activate prod
```

### Per-Command Profile Override

Use different profiles for specific commands:

```bash
# Use development profile for testing
okta-cli users list --profile dev

# Use production profile for actual operations
okta-cli users create --first-name John --last-name Doe --email john@example.com --login john@example.com --profile prod

# Use staging for validation
okta-cli users show john@example.com --profile staging
```

### Profile-Based Configuration Examples

Set up common profile configurations:

#### Development Environment Setup

```bash
# Create development profiles
okta-cli config create dev --domain dev.okta.com --token dev-token-here
okta-cli config create dev-test --domain dev.okta.com --token dev-test-token-here
```

#### Production Environment Setup

```bash
# Create production profiles
okta-cli config create production --domain company.okta.com --token prod-token-here
okta-cli config create prod-readonly --domain company.okta.com --token readonly-token-here
```

## Backup and Restore

### Backup Configuration

Create backups of your configuration:

```bash
# Backup to default file
okta-cli config backup

# Backup to specific file
okta-cli config backup --output ~/backups/okta-config-$(date +%Y%m%d).json
```

Backup includes:
- All profiles
- Profile settings
- Metadata (creation times, etc.)

### Restore Configuration

Restore from backup:

```bash
# Restore from backup file
okta-cli config restore backup.json

# Force restore (overwrite existing)
okta-cli config restore backup.json --force
```

### Automated Backup

Set up automated backups:

```bash
#!/bin/bash
# Create daily backup
BACKUP_DIR=~/okta-cli-backups
mkdir -p $BACKUP_DIR

okta-cli config backup --output $BACKUP_DIR/config-$(date +%Y%m%d).json

# Keep only last 30 days
find $BACKUP_DIR -name "config-*.json" -mtime +30 -delete
```

## Security Configuration

### Encrypted Credential Storage

The CLI supports encrypted credential storage:

```bash
# Enable encryption (will prompt for master password)
okta-cli config encrypt

# Decrypt credentials
okta-cli config decrypt
```

### File Permissions

The CLI automatically sets secure file permissions:

- **Directory**: `700` (owner read/write/execute only)
- **Config file**: `600` (owner read/write only)
- **Backup files**: `600` (owner read/write only)

### Network Security

Configure network security options:

```bash
# Set custom timeout (default: 30 seconds)
export OKTA_TIMEOUT=60

# Enable SSL verification (default: true)
export OKTA_SSL_VERIFY=true

# Set proxy settings
export OKTA_PROXY=https://proxy.company.com:8080
```

## Troubleshooting Configuration

### Common Issues

#### 1. Configuration File Not Found

```bash
# Error: Configuration file not found
# Solution: Run the configuration wizard
okta-cli config wizard
```

#### 2. Profile Not Found

```bash
# Error: Profile 'production' not found
# Solution: Check available profiles
okta-cli config list

# Create missing profile
okta-cli config create production --domain prod.okta.com --token your-token
```

#### 3. Invalid Token

```bash
# Error: Invalid API token
# Solution: Validate token
okta-cli config validate production

# Check token in Okta Admin Console
# Regenerate token if necessary
```

#### 4. Network Connectivity Issues

```bash
# Error: Unable to connect to Okta
# Solution: Check network and domain
okta-cli config health

# Verify domain is correct
okta-cli config show production
```

#### 5. Permission Errors

```bash
# Error: Insufficient permissions
# Solution: Check token permissions in Okta Admin Console
# Ensure token has required scopes
```

### Debug Configuration

Enable debug mode for detailed troubleshooting:

```bash
# Enable debug output
export OKTA_DEBUG=true

# Run command with verbose output
okta-cli --verbose config health
```

Debug output includes:
- Configuration file paths
- Profile resolution
- API requests and responses
- Error details

### Configuration Validation Script

Create a validation script for the enhanced configuration system:

```bash
#!/bin/bash
set -e

echo "Validating Okta CLI enhanced configuration..."

# Check if CLI is installed
if ! command -v okta-cli &> /dev/null; then
    echo "ERROR: okta-cli not found. Please install it first."
    exit 1
fi

# Check if enhanced configuration exists
if [ ! -d ~/.okta ]; then
    echo "INFO: Enhanced configuration directory not found. Creating initial profile..."
    okta-cli config wizard
fi

# Check for profiles
if ! okta-cli config list &> /dev/null; then
    echo "INFO: No profiles found. Run 'okta-cli config wizard' to create your first profile."
    exit 0
fi

# List profiles
echo "Available profiles:"
okta-cli config list

# Check health
echo "Configuration health check:"
okta-cli config health

echo "Enhanced configuration validation complete!"
```

## Best Practices

### 1. Environment Separation

- Use separate profiles for each environment
- Never mix development and production tokens
- Use descriptive profile names

### 2. Security

- Store tokens in environment variables for automation
- Use encrypted storage for sensitive environments
- Rotate tokens regularly
- Monitor token usage

### 3. Backup and Recovery

- Regular configuration backups
- Test restore procedures
- Document configuration changes
- Version control configuration templates

### 4. Team Collaboration

- Share configuration templates (without tokens)
- Document profile naming conventions
- Use consistent environment names
- Maintain team configuration standards

### 5. Automation

- Use environment variables in CI/CD
- Implement configuration validation in scripts
- Monitor configuration health
- Automate token rotation

## Configuration Examples

### Development Setup

```bash
# Set up development environment
okta-cli config create dev \
  --domain dev.okta.com \
  --token $DEV_TOKEN

# Test configuration
okta-cli config health --profile dev

# Use for development
okta-cli users list --profile dev --limit 5
```

### Production Setup

```bash
# Set up production environment
okta-cli config create prod \
  --domain company.okta.com \
  --token $PROD_TOKEN

# Validate production access
okta-cli config validate prod

# Set as default
okta-cli config activate prod
```

### Multi-Region Setup

```bash
# US region
okta-cli config create us \
  --domain us.okta.com \
  --token $US_TOKEN

# EU region
okta-cli config create eu \
  --domain eu.okta.com \
  --token $EU_TOKEN

# Switch between regions
okta-cli users list --profile us
okta-cli users list --profile eu
```

This comprehensive configuration guide should help you set up and manage your Okta CLI configuration effectively. For additional help, use `okta-cli config --help` or `okta-cli config COMMAND --help` for specific commands.