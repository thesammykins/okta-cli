# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Okta CLI tool built with Python and Click that provides a command-line interface for managing Okta users and groups through the Okta API. The tool supports profile-based configuration for multiple Okta environments.

## Development Commands

### Installation and Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run the CLI tool
okta-cli --help
```

### Testing
```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_users.py
pytest tests/test_groups.py
pytest tests/test_main.py
```

### Package Management
```bash
# Build package
python -m build

# Install package locally
pip install -e .
```

## Architecture

### Core Structure
- `okta_cli/main.py` - Main CLI entry point with `configure` command and CLI group setup
- `okta_cli/config.py` - Configuration management (reads/writes `~/.okta/credentials`)
- `okta_cli/users.py` - User management commands (list, create, show, suspend, etc.)
- `okta_cli/groups.py` - Group management commands (list, create, show, update, delete, etc.)

### Configuration System
- Profile-based configuration stored in `~/.okta/credentials`
- Uses Python's `configparser` for INI-style configuration
- Each profile contains `domain` and `token` for Okta API access
- Default profile is "default" but can be overridden with `--profile` option

### API Integration
- Uses `requests` library for HTTP calls to Okta API
- Comprehensive error handling with user-friendly messages
- SSWS token authentication with proper headers
- 30-second timeout for all API requests
- All commands follow pattern: input validation → config validation → API call → response handling

### Error Handling System
- Centralized error handling in `okta_cli/errors.py`
- Input validation for emails, domains, tokens, and names
- API error mapping (401, 403, 404, 429, 500, etc.)
- Network error handling (timeouts, connection failures)
- Configuration error handling (missing profiles, corrupted files)
- Consistent error message format with recovery suggestions

### Security Features
- **Encrypted Credential Storage**: AES-256 encryption with PBKDF2 key derivation in `okta_cli/security.py`
- **Token Validation**: Real-time token validation and permission checking
- **Rate Limiting**: Client-side rate limiting to prevent API abuse
- **Master Password Protection**: All credentials protected by master password
- **Secure File Permissions**: Automatic restrictive permissions (700/600)
- **Backup/Restore**: Encrypted configuration backup and restore functionality

### Command Structure
- Main CLI group with subcommands for `users` and `groups`
- Each subcommand group contains specific operations (list, create, show, update, etc.)
- Consistent `--profile` option across all commands
- User commands support lifecycle operations (activate, deactivate, suspend, etc.)
- Group commands support membership management (add-user, remove-user, list-members)

## Code Standards

The project follows PEP 8 style guide with these specifics:
- 4 spaces for indentation
- 79 character line limit
- Grouped imports (standard library, third-party, local)
- `lowercase_with_underscores` naming for functions/variables
- `CapitalizedWords` for classes
- `UPPERCASE_WITH_UNDERSCORES` for constants
- Google-style docstrings
- Type hints recommended
- Use `try-except` for error handling
- Use `logging` module instead of `print()` for production code

## Testing

Tests are located in `tests/` directory with files corresponding to each module:
- `test_main.py` - Tests for main CLI functionality
- `test_users.py` - Tests for user management commands
- `test_groups.py` - Tests for group management commands

## Entry Points

The CLI is accessible via the `okta-cli` command, defined in `pyproject.toml`:
```toml
[project.scripts]
okta-cli = "okta_cli.main:cli"
```