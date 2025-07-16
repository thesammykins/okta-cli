# Okta CLI Quick Setup

This directory contains scripts to quickly set up and use the Okta CLI environment.

## 🚀 Quick Start

### 1. Initial Setup

Run the setup script to create the virtual environment and install dependencies:

```bash
./setup-okta-cli.sh
```

This will:
- ✅ Create a Python virtual environment
- ✅ Install all required dependencies
- ✅ Install the Okta CLI in development mode
- ✅ Create helper scripts for easy usage
- ✅ Test the installation

### 2. Usage Options

After setup, you have three ways to use the Okta CLI:

#### Option 1: Activation Script (Recommended)
```bash
source ./activate-okta-cli.sh
```

This activates the environment and provides helpful shortcuts:
- `okta-help` - Show available helper functions
- `okta-config` - Quick configuration wizard
- `okta-status` - Show configuration status
- `okta-test` - Test connectivity
- `okta-profiles` - List all profiles
- `okta-users` - List users (requires config)
- `okta-groups` - List groups (requires config)
- `okta-apps` - List applications (requires config)
- `okta-logs` - Show recent logs (requires config)
- `okta-health` - Check system health

#### Option 2: Quick Launcher
```bash
./okta --help
./okta config wizard
./okta users list
```

#### Option 3: Manual Activation
```bash
source venv/bin/activate
okta-cli --help
```

## 📋 First-Time Configuration

After setup, configure your Okta settings:

```bash
# Using activation script
source ./activate-okta-cli.sh
okta-config

# Using quick launcher
./okta config wizard

# Manual method
source venv/bin/activate
okta-cli config wizard
```

The wizard will prompt you for:
- **Okta Domain**: Your organization's Okta domain (e.g., `company.okta.com`)
- **API Token**: Your Okta API token (create one in Admin Console → Security → API)

## 🔧 Configuration Management

### Multiple Profiles
```bash
# Create different profiles for different environments
okta-cli config create dev --domain dev.okta.com --token your-dev-token
okta-cli config create prod --domain prod.okta.com --token your-prod-token

# Switch between profiles
okta-cli config activate dev
okta-cli config activate prod

# List all profiles
okta-cli config list
```

### Environment Variables
```bash
# Set environment variables instead of profiles
export OKTA_DOMAIN=your.okta.com
export OKTA_TOKEN=your-api-token
export OKTA_PROFILE=production
```

## 🔍 Common Commands

### User Management
```bash
# List users
okta-cli users list --output table

# Create user
okta-cli users create --first-name John --last-name Doe --email john.doe@company.com

# Show user details
okta-cli users show user-id

# Activate/deactivate user
okta-cli users activate user-id
okta-cli users deactivate user-id
```

### Group Management
```bash
# List groups
okta-cli groups list

# Create group
okta-cli groups create --name "Engineering Team" --description "Software engineers"

# Add user to group
okta-cli groups add-user group-id user-id
```

### Application Management
```bash
# List applications
okta-cli applications list

# Show application details
okta-cli applications show app-id

# List application users
okta-cli applications list-users app-id
```

### Security Monitoring
```bash
# Check recent failed logins
okta-cli logs failed-logins --days 1

# Search for specific events
okta-cli logs search --event-type "user.session.start" --days 7

# Check MFA statistics
okta-cli factors stats
```

## 📊 Output Formats

All commands support multiple output formats:

```bash
# Table format (default)
okta-cli users list --output table

# JSON format
okta-cli users list --output json

# CSV format
okta-cli users list --output csv

# YAML format
okta-cli users list --output yaml
```

## 🛠️ Troubleshooting

### Health Check
```bash
# Test configuration and connectivity
okta-cli config health

# Check configuration status
okta-cli config status

# Validate specific profile
okta-cli config validate profile-name
```

### Common Issues

1. **Configuration Issues**:
   ```bash
   okta-cli config wizard  # Reconfigure
   ```

2. **Token Issues**:
   ```bash
   okta-cli config validate  # Test token
   ```

3. **Network Issues**:
   ```bash
   okta-cli config health  # Test connectivity
   ```

## 🔒 Security Best Practices

1. **Secure Token Storage**: Use environment variables in production
2. **Token Rotation**: Regularly rotate API tokens
3. **Least Privilege**: Use tokens with minimal required permissions
4. **Profile Separation**: Use different profiles for different environments
5. **Audit Logging**: Monitor CLI usage through Okta logs

## 📚 Documentation

- **Full Documentation**: See `AGENT.md` for comprehensive command reference
- **API Reference**: Commands interact with Okta REST APIs
- **Help System**: Use `--help` with any command for detailed usage

## 🔄 Updating

To update the CLI or dependencies:

```bash
# Re-run setup script
./setup-okta-cli.sh

# Or manually update
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## 📁 Files Created

The setup script creates:
- `venv/` - Python virtual environment
- `activate-okta-cli.sh` - Environment activation script with helpers
- `okta` - Quick launcher script
- `SETUP_README.md` - This documentation

## 🤝 Support

- Use `okta-help` for quick reference
- Run `okta-cli --help` for command help
- Check `AGENT.md` for detailed documentation
- Use `okta-health` for system diagnostics
