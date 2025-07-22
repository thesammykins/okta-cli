# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Removed legacy INI configuration system; enhanced system is now mandatory.

### Added
- Initial release of Okta CLI tool
- Comprehensive user management commands
- Group management functionality
- Application management capabilities
- Session management features
- Security policy and group rules management
- Authorization server management
- Event log analysis and security monitoring
- Multi-factor authentication management
- Multiple output formats (JSON, CSV, YAML, table, text)
- Profile-based configuration system
- Interactive configuration wizard
- Enhanced error handling and recovery
- Comprehensive test suite
- GitHub Actions CI/CD pipeline
- Docker containerization support
- Automated release management
- Security scanning and vulnerability detection
- Documentation and user guides

### Features
- **Configuration Management**: Multi-profile support with health checks
- **User Operations**: Complete lifecycle management (create, activate, deactivate, suspend)
- **Group Operations**: Full group management with membership controls
- **Application Management**: Application provisioning and assignment
- **Session Control**: Active session monitoring and management
- **Security Policies**: Policy and group rule administration
- **OAuth Management**: Authorization server and scope management
- **Security Monitoring**: Event log analysis and threat detection
- **MFA Support**: Factor enrollment and verification
- **Flexible Output**: Multiple format support for different use cases
- **Error Recovery**: Comprehensive error handling with suggestions
- **API Integration**: Full Okta REST API coverage

### Security
- Encrypted credential storage with AES-256 encryption
- PBKDF2 key derivation for password protection
- Secure file permissions (700/600)
- Rate limiting to prevent API abuse
- Token validation and permission checking
- Master password protection for all credentials
- Backup and restore functionality for configurations
- Comprehensive secret detection in CI/CD

### Developer Experience
- Python 3.8+ compatibility
- Click framework for CLI interface
- Comprehensive test coverage
- Type hints and documentation
- Code formatting with black and flake8
- Security scanning with bandit and safety
- Automated dependency management
- Docker support for containerized deployments

## [1.0.0] - 2024-07-16

### Added
- Initial public release
- Core CLI functionality
- Complete Okta API integration
- Documentation and examples
- Test suite and CI/CD pipeline
- Security features and encryption
- Multi-platform support
- Docker containerization

---

## Release Notes

### v1.0.0 - Initial Release

This is the first public release of the Okta CLI tool, providing a comprehensive command-line interface for managing Okta identity and access management operations.

#### Key Features
- Complete user lifecycle management
- Group and application management
- Session and policy control
- Security monitoring and logging
- Multi-factor authentication support
- Flexible output formats
- Profile-based configuration
- Enhanced error handling

#### Installation
```bash
pip install okta-cli
```

#### Docker
```bash
docker pull ghcr.io/thesammykins/okta-cli:latest
```

#### Quick Start
```bash
okta-cli config wizard
okta-cli users list
```

For detailed documentation, see the [docs directory](docs/) and [README.md](README.md).

#### Security
This release includes comprehensive security features including encrypted credential storage, secure file permissions, and rate limiting. All credentials are protected with AES-256 encryption and PBKDF2 key derivation.

#### Contributing
We welcome contributions! Please see our [Contributing Guide](README.md#contributing) for details on how to get started.

#### Support
- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/thesammykins/okta-cli/issues)
- **Releases**: [GitHub Releases](https://github.com/thesammykins/okta-cli/releases)