# Quick Start Guide

Get up and running with the Okta CLI in minutes.

## Prerequisites

- Okta CLI installed ([Installation Guide](installation.md))
- Okta domain and API token ready
- Python 3.8+ environment

## Initial Setup

### 1. Configure Your First Profile

Run the interactive configuration wizard:

```bash
okta-cli config wizard
```

The wizard will prompt you for:
- **Profile name** (e.g., "production", "development")
- **Okta domain** (e.g., "company.okta.com")
- **API token** (create one in Okta Admin Console → Security → API)

### 2. Verify Configuration

Test your setup:

```bash
# Check configuration health
okta-cli config health

# View your profile
okta-cli config show

# Test connectivity
okta-cli users list --limit 3
```

## Basic Commands

### User Management

```bash
# List users
okta-cli users list

# Show specific user
okta-cli users show user@example.com

# Create a new user
okta-cli users create \
  --first-name John \
  --last-name Doe \
  --email john.doe@example.com \
  --login john.doe@example.com

# Activate a user
okta-cli users activate john.doe@example.com
```

### Group Management

```bash
# List groups
okta-cli groups list

# Create a new group
okta-cli groups create \
  --name "Engineering Team" \
  --description "Software engineers"

# Add user to group
okta-cli groups add-user "Engineering Team" john.doe@example.com
```

### Application Management

```bash
# List applications
okta-cli applications list

# Show application details
okta-cli applications show "My App"

# List users assigned to an application
okta-cli applications list-users "My App"
```

## Common Workflows

### Onboard a New User

Complete user onboarding process:

```bash
# 1. Create the user
okta-cli users create \
  --first-name "Jane" \
  --last-name "Smith" \
  --email "jane.smith@company.com" \
  --login "jane.smith@company.com"

# 2. Add to standard groups
okta-cli groups add-user "Everyone" jane.smith@company.com
okta-cli groups add-user "Engineering" jane.smith@company.com

# 3. Assign applications (if supported)
okta-cli users assign-app jane.smith@company.com "Company Portal"

# 4. Activate the user
okta-cli users activate jane.smith@company.com

# 5. Verify the setup
okta-cli users show jane.smith@company.com
```

### Security Monitoring

Check for security issues:

```bash
# Check recent failed logins
okta-cli logs failed-logins --days 1

# Monitor suspicious activities
okta-cli logs suspicious --days 7

# Check MFA adoption
okta-cli factors stats
```

### Export Data

Export data for analysis:

```bash
# Export users to CSV
okta-cli users list --output csv > users.csv

# Export groups to JSON
okta-cli groups list --output json > groups.json

# Export security logs
okta-cli logs search --days 30 --output json > security_logs.json
```

## Output Formats

The CLI supports multiple output formats:

```bash
# Human-readable table (default)
okta-cli users list --output table

# JSON for programmatic use
okta-cli users list --output json

# CSV for spreadsheets
okta-cli users list --output csv

# YAML for configuration
okta-cli users list --output yaml
```

## Getting Help

### Command Help

```bash
# General help
okta-cli --help

# Command-specific help
okta-cli users --help
okta-cli users create --help
```

### Configuration Help

```bash
# Check configuration status
okta-cli config status

# List all profiles
okta-cli config list

# Validate configuration
okta-cli config validate
```

## Environment Variables

For automation, use environment variables:

```bash
# Set environment variables
export OKTA_DOMAIN=company.okta.com
export OKTA_TOKEN=your-api-token
export OKTA_PROFILE=production

# Use in scripts
okta-cli users list --output json
```

## Multiple Environments

Manage different environments:

```bash
# Create profiles for different environments
okta-cli config create dev --domain dev.okta.com --token dev-token
okta-cli config create staging --domain staging.okta.com --token staging-token
okta-cli config create prod --domain prod.okta.com --token prod-token

# Switch between environments
okta-cli config activate dev
okta-cli users list

# Use specific profile for one command
okta-cli users list --profile prod
```

## Best Practices

### Security
- Store API tokens securely
- Use separate profiles for different environments
- Rotate API tokens regularly
- Use minimal required permissions

### Performance
- Use filters to limit data retrieval
- Use appropriate output formats
- Implement pagination for large datasets

### Automation
- Use JSON output for parsing in scripts
- Check exit codes for error handling
- Use `--force` flags for non-interactive operations

## Troubleshooting

### Common Issues

1. **Configuration Problems**
   ```bash
   # Check configuration
   okta-cli config health
   
   # Reconfigure if needed
   okta-cli config wizard
   ```

2. **Authentication Errors**
   ```bash
   # Validate token
   okta-cli config validate
   
   # Check token permissions in Okta Admin Console
   ```

3. **Network Issues**
   ```bash
   # Test connectivity
   okta-cli config health
   
   # Check domain configuration
   okta-cli config show
   ```

## Next Steps

Now that you're set up:

1. Explore the [Command Reference](commands.md)
2. Learn about [Configuration Options](configuration.md)
3. Check out [Common Use Cases](use-cases.md)
4. Review [Security Considerations](security.md)
5. Read the [Troubleshooting Guide](troubleshooting.md)