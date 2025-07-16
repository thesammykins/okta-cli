# Okta CLI Tool

A comprehensive command-line interface for managing Okta identity and access management operations. Built with Python and Click, this tool provides extensive functionality for user management, application management, security policies, session management, and more.

## Features

- **Configuration Management**: Multi-profile support with validation and health checks
- **User Management**: Complete user lifecycle operations (create, update, activate, deactivate, suspend)
- **Group Management**: Group creation, membership management, and lifecycle operations
- **Application Management**: Application provisioning, assignment, and lifecycle management
- **Session Management**: Active session monitoring and control
- **Security Policies**: Policy and group rule management
- **Authorization Servers**: OAuth authorization server and scope management
- **Security Monitoring**: Event log analysis and threat detection
- **Multi-Factor Authentication**: Factor enrollment, verification, and management
- **Multiple Output Formats**: JSON, table, CSV, YAML, and text output support
- **Interactive Configuration**: Wizard-based setup for easy configuration
- **Comprehensive Error Handling**: Detailed error messages and troubleshooting guidance

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### From PyPI (Recommended)

```bash
pip install okta-cli
```

### From GitHub Releases

1. Download the latest release from the [releases page](https://github.com/thesammykins/okta-cli/releases)
2. Install the wheel file:
```bash
pip install okta-cli-*.whl
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/thesammykins/okta-cli.git
cd okta-cli
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install in development mode:
```bash
pip install -e .
```

### Docker

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/thesammykins/okta-cli:latest

# Run interactively
docker run -it -v ~/.okta-cli:/home/oktauser/.okta-cli ghcr.io/thesammykins/okta-cli:latest

# Run a specific command
docker run -v ~/.okta-cli:/home/oktauser/.okta-cli ghcr.io/thesammykins/okta-cli:latest users list --profile prod
```

### Setup

After installation, run the configuration wizard:
```bash
okta-cli config wizard
```

## Quick Start

### Initial Configuration

Use the interactive configuration wizard to set up your first profile:

```bash
python -m okta_cli config wizard
```

Or configure manually:

```bash
python -m okta_cli configure --profile default
```

### Environment Variables

You can also use environment variables for configuration:

```bash
export OKTA_DOMAIN=your.okta.com
export OKTA_TOKEN=your-api-token
export OKTA_PROFILE=production
```

### Basic Usage

```bash
# List users
python -m okta_cli users list

# Create a new user
python -m okta_cli users create \
  --first-name John \
  --last-name Doe \
  --email john.doe@example.com \
  --login john.doe@example.com

# List groups
python -m okta_cli groups list

# Create a new group
python -m okta_cli groups create \
  --name "Engineering Team" \
  --description "Software engineers"

# List applications
python -m okta_cli applications list

# Get security logs
python -m okta_cli logs failed-logins --days 7
```

## Command Reference

### Configuration Commands

```bash
# Configuration wizard
python -m okta_cli config wizard

# Profile management
python -m okta_cli config create dev --domain dev.okta.com --token your-token
python -m okta_cli config list
python -m okta_cli config activate dev
python -m okta_cli config show dev
python -m okta_cli config delete dev --force

# Health checks
python -m okta_cli config health
python -m okta_cli config validate dev
python -m okta_cli config status

# Backup and restore
python -m okta_cli config backup --output backup.json
python -m okta_cli config restore backup.json --force
```

### User Management

```bash
# List and search users
python -m okta_cli users list --output table
python -m okta_cli users show user123
python -m okta_cli users search --query "john.doe"

# Create users
python -m okta_cli users create \
  --first-name John \
  --last-name Doe \
  --email john.doe@example.com \
  --login john.doe@example.com

# User lifecycle
python -m okta_cli users activate user123
python -m okta_cli users deactivate user123
python -m okta_cli users suspend user123
python -m okta_cli users unsuspend user123
python -m okta_cli users reset-password user123

# User updates
python -m okta_cli users update user123 \
  --first-name Jonathan \
  --email new.email@example.com

# Application assignments
python -m okta_cli users assign-app user123 app456
python -m okta_cli users unassign-app user123 app456
python -m okta_cli users list-app-assignments app456
```

### Group Management

```bash
# List and show groups
python -m okta_cli groups list --output table
python -m okta_cli groups show group123

# Create and update groups
python -m okta_cli groups create \
  --name "Engineering Team" \
  --description "Software engineers"

python -m okta_cli groups update group123 \
  --name "Senior Engineering Team"

# Group membership
python -m okta_cli groups add-user group123 user456
python -m okta_cli groups remove-user group123 user456
python -m okta_cli groups list-users group123

# Group lifecycle
python -m okta_cli groups delete group123 --force
```

### Application Management

```bash
# List and show applications
python -m okta_cli applications list --output table
python -m okta_cli applications show app123

# Create applications
python -m okta_cli applications create \
  --name "My App" \
  --label "My Application" \
  --sign-on-mode SAML_2_0

# Application lifecycle
python -m okta_cli applications activate app123
python -m okta_cli applications deactivate app123
python -m okta_cli applications delete app123 --force

# Application assignments
python -m okta_cli applications list-users app123
python -m okta_cli applications list-groups app123

# Update applications
python -m okta_cli applications update app123 \
  --name "Updated App Name" \
  --status ACTIVE
```

### Session Management

```bash
# List and show sessions
python -m okta_cli sessions list user123 --output table
python -m okta_cli sessions show user123 session456

# Session operations
python -m okta_cli sessions extend user123 session456
python -m okta_cli sessions clear user123 --force
python -m okta_cli sessions clear user123 --oauth-only

# Session analytics
python -m okta_cli sessions stats --days 30
python -m okta_cli sessions active --limit 50
```

### Policy and Group Rules Management

```bash
# List policies
python -m okta_cli policies list --type PASSWORD --output table
python -m okta_cli policies show policy123

# Policy operations
python -m okta_cli policies activate policy123
python -m okta_cli policies deactivate policy123

# Group rules
python -m okta_cli policies rules list --output table
python -m okta_cli policies rules show rule123

# Create group rules
python -m okta_cli policies rules create \
  --name "Engineering Rule" \
  --expression 'user.department=="Engineering"' \
  --group-id group123

# Group rule lifecycle
python -m okta_cli policies rules activate rule123
python -m okta_cli policies rules deactivate rule123
python -m okta_cli policies rules delete rule123 --force
```

### Authorization Server Management

```bash
# List authorization servers
python -m okta_cli authorization list --output table
python -m okta_cli authorization show server123

# Create authorization server
python -m okta_cli authorization create \
  --name "My API Server" \
  --description "API authorization server" \
  --audience "api://my-api"

# Authorization server operations
python -m okta_cli authorization activate server123
python -m okta_cli authorization deactivate server123
python -m okta_cli authorization delete server123 --force

# Scope management
python -m okta_cli authorization scopes list server123
python -m okta_cli authorization scopes create server123 \
  --name "read:users" \
  --description "Read user data" \
  --consent REQUIRED
```

### Event Log Analysis

```bash
# List and search logs
python -m okta_cli logs list --limit 100 --output table
python -m okta_cli logs show log-uuid-123

# Advanced search
python -m okta_cli logs search \
  --event-type "user.session.start" \
  --outcome SUCCESS \
  --days 7

# Security monitoring
python -m okta_cli logs failed-logins --days 1
python -m okta_cli logs suspicious --days 7

# Log analytics
python -m okta_cli logs stats --days 30 --output json
```

### Multi-Factor Authentication

```bash
# List user factors
python -m okta_cli factors list user123 --output table
python -m okta_cli factors show user123 factor456

# Factor enrollment
python -m okta_cli factors enroll user123 \
  --factor-type sms \
  --phone-number "+1234567890"

python -m okta_cli factors enroll user123 \
  --factor-type token:software:totp

# Factor operations
python -m okta_cli factors activate user123 factor456 --passcode 123456
python -m okta_cli factors verify user123 factor456 --passcode 123456
python -m okta_cli factors reset user123 factor456 --force

# Factor analytics
python -m okta_cli factors stats --limit 1000
python -m okta_cli factors catalog list user123
```

## Output Formats

All commands support multiple output formats:

- `--output table` - Human-readable table format (default)
- `--output json` - JSON format for programmatic use
- `--output csv` - CSV format for spreadsheet applications
- `--output yaml` - YAML format for configuration files
- `--output text` - Plain text format

Example:
```bash
python -m okta_cli users list --output json
python -m okta_cli groups list --output csv
python -m okta_cli applications list --output yaml
```

## Configuration

### Profile Management

The CLI supports multiple configuration profiles for different environments:

```bash
# Create profiles for different environments
python -m okta_cli config create dev --domain dev.okta.com --token dev-token
python -m okta_cli config create staging --domain staging.okta.com --token staging-token
python -m okta_cli config create prod --domain prod.okta.com --token prod-token

# Switch between environments
python -m okta_cli config activate dev
python -m okta_cli users list

python -m okta_cli config activate prod
python -m okta_cli users list --profile prod
```

### Environment Variables

- `OKTA_DOMAIN` - Your Okta domain
- `OKTA_TOKEN` - Your API token
- `OKTA_PROFILE` - Active profile name
- `OKTA_DEBUG` - Enable debug output

### Configuration File

Configuration is stored in `~/.okta-cli/config.ini`:

```ini
[default]
domain = your.okta.com
token = your-api-token

[production]
domain = prod.okta.com
token = prod-api-token
```

## Common Use Cases

### User Onboarding

```bash
# Create user
python -m okta_cli users create \
  --first-name "Jane" \
  --last-name "Smith" \
  --email "jane.smith@company.com" \
  --login "jane.smith@company.com"

# Add to groups
python -m okta_cli groups add-user engineering-team user123
python -m okta_cli groups add-user all-employees user123

# Assign applications
python -m okta_cli users assign-app user123 app456
python -m okta_cli users assign-app user123 app789

# Activate user
python -m okta_cli users activate user123
```

### User Offboarding

```bash
# Deactivate user
python -m okta_cli users deactivate user123

# Clear active sessions
python -m okta_cli sessions clear user123 --force

# Remove from groups
python -m okta_cli groups remove-user engineering-team user123
python -m okta_cli groups remove-user all-employees user123

# Unassign applications
python -m okta_cli users unassign-app user123 app456
python -m okta_cli users unassign-app user123 app789
```

### Security Monitoring

```bash
# Check for failed login attempts
python -m okta_cli logs failed-logins --days 1 --output json

# Monitor suspicious activities
python -m okta_cli logs suspicious --days 7 --output table

# Analyze login patterns
python -m okta_cli logs search \
  --event-type "user.session.start" \
  --days 30 \
  --output csv

# Check MFA adoption
python -m okta_cli factors stats --output json
```

### Bulk Operations

```bash
# Export users to CSV
python -m okta_cli users list --output csv > users.csv

# Export groups to JSON
python -m okta_cli groups list --output json > groups.json

# Export application assignments
python -m okta_cli applications list-users app123 --output csv > app_users.csv

# Export security logs
python -m okta_cli logs search --days 30 --output json > security_logs.json
```

## Error Handling

The CLI provides comprehensive error handling:

```bash
# Check configuration health
python -m okta_cli config health

# Validate profiles
python -m okta_cli config validate production

# Test connectivity
python -m okta_cli config show production
```

Common error scenarios:
- **Invalid credentials**: Use `python -m okta_cli config validate` to verify
- **Network issues**: Check domain and connectivity
- **Permission errors**: Verify API token permissions
- **Resource not found**: Check resource IDs and filters

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_phase5.py

# Run with coverage
pytest --cov=okta_cli
```

### Project Structure

```
okta_cli/
├── __init__.py
├── main.py                 # Main CLI entry point
├── config.py              # Configuration management
├── config_commands.py     # Configuration CLI commands
├── enhanced_config.py     # Enhanced configuration features
├── users.py               # User management commands
├── groups.py              # Group management commands
├── applications.py        # Application management commands
├── sessions.py            # Session management commands
├── policies.py            # Policy and group rules commands
├── authorization.py       # Authorization server commands
├── logs.py                # Event log analysis commands
├── factors.py             # MFA factor management commands
├── errors.py              # Error handling utilities
├── formatting.py          # Output formatting utilities
├── progress.py            # Progress indicator utilities
└── interactive.py         # Interactive prompt utilities

tests/
├── test_config.py         # Configuration tests
├── test_users.py          # User management tests
├── test_groups.py         # Group management tests
└── test_phase5.py         # Phase 5 feature tests
```

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

## Troubleshooting

### Debug Mode

Enable debug output:
```bash
export OKTA_DEBUG=true
python -m okta_cli users list

# Or use verbose flag
python -m okta_cli --verbose users list
```

### Common Issues

1. **Authentication errors**
   ```bash
   # Check token validity
   python -m okta_cli config validate
   python -m okta_cli config health
   ```

2. **Network connectivity**
   ```bash
   # Test connectivity
   python -m okta_cli config health
   # Check domain configuration
   python -m okta_cli config show
   ```

3. **Permission issues**
   ```bash
   # Check API token permissions
   python -m okta_cli logs search --event-type "system.api_token.create"
   ```

## API Reference

The CLI interacts with the following Okta API endpoints:

- **Users API**: `/api/v1/users`
- **Groups API**: `/api/v1/groups`
- **Applications API**: `/api/v1/apps`
- **Sessions API**: `/api/v1/users/{userId}/sessions`
- **Policies API**: `/api/v1/policies`
- **Authorization Servers API**: `/api/v1/authorizationServers`
- **System Log API**: `/api/v1/logs`
- **Factors API**: `/api/v1/users/{userId}/factors`

## Support

- **Configuration**: Use `python -m okta_cli config wizard` for initial setup
- **Help**: Run `python -m okta_cli --help` or `python -m okta_cli {command} --help` for detailed usage
- **Health checks**: Use `python -m okta_cli config health` to verify configuration
- **Status**: Use `python -m okta_cli config status` to see current configuration state
- **Testing**: Use `python -m okta_cli config validate` to test profile configurations

## Releases

### Automated Releases

This project uses GitHub Actions for automated releases:

- **Version Bumping**: Use the "Version Bump" workflow to automatically update versions
- **Release Creation**: Tag a commit with `v*.*.*` to trigger automatic release
- **Package Publishing**: Releases are automatically published to PyPI and GitHub Container Registry

### Manual Release

For manual releases, use the provided script:

```bash
./scripts/release.sh
```

See [docs/RELEASING.md](docs/RELEASING.md) for detailed release instructions.

### Release Assets

Each release includes:
- Python wheel (`.whl`) for pip installation
- Source distribution (`.tar.gz`) for manual installation
- Docker image published to GitHub Container Registry

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/okta-cli.git
cd okta-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For detailed usage examples and advanced configuration options, see the [AGENT.md](docs/AGENT.md) file.