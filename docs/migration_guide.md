# Legacy Configuration Migration Guide

This guide helps users migrate from the legacy INI-based configuration system to the enhanced profile-based configuration system.

## Overview

The Okta CLI has transitioned from a legacy INI-based configuration system to an enhanced profile-based configuration system. This migration provides:

- **Better Security**: Enhanced encryption and secure credential storage
- **Multi-Environment Support**: Easy switching between development, staging, and production
- **Profile Management**: Complete lifecycle management of configuration profiles
- **Environment Variables**: Full support for environment-based configuration
- **Validation and Health Checks**: Built-in configuration validation

## What Changed

### Legacy System (Deprecated)
- **Location**: `~/.okta-cli/config.ini`
- **Format**: INI file format
- **Profiles**: Limited profile support
- **Validation**: Basic validation only

### Enhanced System (Current)
- **Location**: `~/.okta/profiles.json` and `~/.okta/active_profile`
- **Format**: JSON-based profile storage
- **Profiles**: Full profile lifecycle management
- **Validation**: Comprehensive health checks and validation

## Migration Steps

### Step 1: Check Current Configuration

First, determine if you're using the legacy system:

```bash
# Check if legacy configuration exists
ls ~/.okta-cli/config.ini 2>/dev/null && echo "Legacy config found" || echo "No legacy config"

# Check if enhanced configuration exists
ls ~/.okta/profiles.json 2>/dev/null && echo "Enhanced config found" || echo "No enhanced config"
```

### Step 2: Create Your First Enhanced Profile

If you have existing legacy configuration, create a new profile with the same settings:

```bash
# Interactive setup (recommended)
okta-cli config wizard

# Or manual setup
okta-cli config create default --domain your.okta.com --token your-api-token
```

### Step 3: Migrate Environment Variables

Update any scripts or CI/CD configurations:

**Legacy Environment Variables (Still Supported)**:
```bash
export OKTA_DOMAIN=your.okta.com
export OKTA_TOKEN=your-api-token
```

**Enhanced Environment Variables**:
```bash
# Profile-specific variables
export OKTA_DEV_DOMAIN=dev.okta.com
export OKTA_DEV_TOKEN=dev-token
export OKTA_PROD_DOMAIN=prod.okta.com
export OKTA_PROD_TOKEN=prod-token

# Active profile selection
export OKTA_PROFILE=production
```

### Step 4: Validate New Configuration

Test your new configuration:

```bash
# Check configuration health
okta-cli config health

# List all profiles
okta-cli config list

# Test connectivity
okta-cli users list --limit 3
```

### Step 5: Update Scripts and Automation

Update any existing scripts:

**Before (Legacy)**:
```bash
#!/bin/bash
# Scripts assumed config.ini existed
okta-cli users list
```

**After (Enhanced)**:
```bash
#!/bin/bash
# Validate configuration first
if ! okta-cli config health; then
    echo "Configuration invalid"
    exit 1
fi

# Use specific profile
okta-cli users list --profile production
```

## New Features Available

### Profile Management

```bash
# Create multiple profiles for different environments
okta-cli config create dev --domain dev.okta.com --token dev-token
okta-cli config create prod --domain prod.okta.com --token prod-token

# Switch between environments
okta-cli config activate dev
okta-cli users list  # Uses dev profile

okta-cli config activate prod
okta-cli users list  # Uses prod profile
```

### Configuration Validation

```bash
# Comprehensive health checks
okta-cli config health

# Profile-specific validation
okta-cli config validate production
```

### Backup and Restore

```bash
# Backup configuration
okta-cli config backup --output backup.json

# Restore configuration
okta-cli config restore backup.json
```

## Troubleshooting

### Common Migration Issues

#### 1. "Profile not found" Error

```bash
# Error: Profile 'default' not found
# Solution: Create a default profile
okta-cli config create default --domain your.okta.com --token your-token
```

#### 2. Environment Variables Not Working

```bash
# Check current configuration source
okta-cli config current

# Verify environment variables are set
env | grep OKTA_
```

#### 3. Legacy Configuration Conflicts

```bash
# If experiencing issues, temporarily rename legacy config
mv ~/.okta-cli ~/.okta-cli.backup

# Create fresh enhanced configuration
okta-cli config wizard
```

### Getting Help

```bash
# Configuration help
okta-cli config --help

# Health check for debugging
okta-cli config health --verbose

# List available commands
okta-cli --help
```

## Benefits of Enhanced Configuration

### 1. Better Security
- Secure file permissions (700/600)
- Encrypted credential storage support
- Token validation and health checks

### 2. Multi-Environment Support
- Easy environment switching
- Profile-specific environment variables
- Environment isolation

### 3. Improved Developer Experience
- Interactive configuration wizard
- Comprehensive validation
- Better error messages and troubleshooting

### 4. Enterprise Features
- Backup and restore functionality
- Configuration templates
- Audit and compliance features

## Frequently Asked Questions

### Q: Can I still use environment variables?
A: Yes! Environment variables are fully supported and take precedence over profile configuration.

### Q: What happens to my legacy config.ini file?
A: The legacy file remains untouched. You can safely remove it after migrating to the enhanced system.

### Q: Can I migrate back to the legacy system?
A: The legacy system is deprecated and no longer supported. We recommend using the enhanced system for all new configurations.

### Q: How do I migrate CI/CD pipelines?
A: Environment variables continue to work. For better security, consider using profile-specific variables:

```bash
# In CI/CD
export OKTA_PROD_DOMAIN=$OKTA_PRODUCTION_DOMAIN
export OKTA_PROD_TOKEN=$OKTA_PRODUCTION_TOKEN
export OKTA_PROFILE=prod
```

### Q: Where can I get more help?
A: See the [Configuration Guide](configuration.md) for detailed documentation, or use `okta-cli config --help` for command-specific help.

## Summary

The enhanced configuration system provides:
- ✅ Better security and encryption
- ✅ Multi-environment profile management
- ✅ Comprehensive validation and health checks
- ✅ Backward compatibility with environment variables
- ✅ Enterprise features like backup/restore

For detailed configuration options, see the [Configuration Guide](configuration.md).

For troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).
