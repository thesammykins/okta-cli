# Okta CLI Tool

**This tool is still a work-in-progress and should only be used in sandbox environments, please log issues if you are actively testing or using this tool.**

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

## Quick Start

### Installation

```bash
# From PyPI (Recommended)
pip install okta-cli

# From source
git clone https://github.com/thesammykins/okta-cli.git
cd okta-cli
pip install -e .
```

### Configuration

```bash
# Interactive setup with enhanced configuration system
okta-cli config wizard

# Or create profiles directly
okta-cli config create dev --domain dev.okta.com --token your-token

# Or use environment variables
export OKTA_DOMAIN=your.okta.com
export OKTA_TOKEN=your-api-token
```

### Basic Usage

```bash
# List users
okta-cli users list

# Create a new user
okta-cli users create \
  --first-name John \
  --last-name Doe \
  --email john.doe@example.com \
  --login john.doe@example.com

# List groups
okta-cli groups list

# Get security logs
okta-cli logs failed-logins --days 7
```

## Documentation

### Complete Documentation

- **[Installation Guide](docs/installation.md)** - Installation methods, setup, and requirements
- **[Quick Start Guide](docs/quickstart.md)** - Getting started with basic usage
- **[Command Reference](docs/commands.md)** - Complete command reference with examples
- **[Configuration Guide](docs/configuration.md)** - Profile management and configuration options
- **[Common Use Cases](docs/use-cases.md)** - Real-world examples and workflows
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[Development Guide](docs/development.md)** - Development setup and contributing

### Key Topics

- **Installation**: Multiple installation methods including PyPI, Docker, and source
- **Configuration**: Multi-profile support for different environments
- **User Management**: Complete user lifecycle operations
- **Group Management**: Group creation and membership management
- **Application Management**: Application provisioning and assignment
- **Security Monitoring**: Event log analysis and security reporting
- **Multi-Factor Authentication**: MFA factor management and statistics
- **Bulk Operations**: Mass operations and data export
- **CI/CD Integration**: Automation and integration examples
- **Error Handling**: Comprehensive error handling and recovery

## Common Operations

### User Lifecycle

```bash
# Create and activate user
okta-cli users create --first-name Jane --last-name Smith --email jane@company.com --login jane@company.com
okta-cli groups add-user "All Employees" jane@company.com
okta-cli users activate jane@company.com

# Deactivate user
okta-cli users deactivate jane@company.com
okta-cli sessions clear jane@company.com --force
```

### Security Monitoring

```bash
# Check failed logins
okta-cli logs failed-logins --days 1 --output json

# Monitor suspicious activities
okta-cli logs suspicious --days 7 --output table

# Check MFA adoption
okta-cli factors stats --output json
```

### Bulk Operations

```bash
# Export data
okta-cli users list --output csv > users.csv
okta-cli groups list --output json > groups.json
okta-cli logs search --days 30 --output json > logs.json
```

## Configuration

### Multiple Environments

```bash
# Create profiles for different environments
okta-cli config create dev --domain dev.okta.com --token dev-token
okta-cli config create prod --domain prod.okta.com --token prod-token

# Switch environments
okta-cli config activate dev
okta-cli users list --profile prod
```

### Environment Variables

```bash
export OKTA_DOMAIN=company.okta.com
export OKTA_TOKEN=your-api-token
export OKTA_PROFILE=production
export OKTA_DEBUG=true  # Enable debug mode
```

## Output Formats

All commands support multiple output formats:

```bash
okta-cli users list --output table    # Human-readable (default)
okta-cli users list --output json     # JSON for scripts
okta-cli users list --output csv      # CSV for spreadsheets
okta-cli users list --output yaml     # YAML format
```

## Getting Help

```bash
# General help
okta-cli --help

# Command-specific help
okta-cli users --help
okta-cli users create --help

# Check configuration health
okta-cli config health

# Validate configuration
okta-cli config validate
```

## Development

### Running Tests

```bash
pytest                    # Run all tests
pytest tests/test_users.py  # Run specific tests
pytest --cov=okta_cli       # Run with coverage
```

### Project Structure

```
okta_cli/
├── main.py              # Main CLI entry point
├── config.py            # Configuration management
├── users.py             # User management commands
├── groups.py            # Group management commands
├── applications.py      # Application management
├── sessions.py          # Session management
├── policies.py          # Policy management
├── authorization.py     # Authorization servers
├── logs.py              # Event log analysis
├── factors.py           # MFA management
├── errors.py            # Error handling
├── formatting.py        # Output formatting
└── security.py          # Security utilities
```

## Security

- **API Token Security**: Store tokens securely, rotate regularly
- **Network Security**: HTTPS for all API calls, proper certificate validation
- **Access Control**: Role-based access, audit logging
- **Data Protection**: Encryption in transit and at rest

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

See the [Development Guide](docs/development.md) for detailed contribution instructions.

## Support

- **Documentation**: Comprehensive guides in the [docs/](docs/) directory
- **Configuration Help**: Use `okta-cli config wizard` for setup
- **Troubleshooting**: See [Troubleshooting Guide](docs/troubleshooting.md)
- **Issues**: Report issues on [GitHub](https://github.com/thesammykins/okta-cli/issues)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For detailed usage examples and advanced configuration options, see the comprehensive documentation in the [docs/](docs/) directory.
