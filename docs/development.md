# Development Guide

Complete guide for developing, testing, and contributing to the Okta CLI project.

## Development Environment Setup

### Prerequisites

- **Python 3.8 or higher** - Check your version with `python --version`
- **pip package manager** - Usually comes with Python
- **Git** - For version control
- **Virtual environment** - Recommended for isolation

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thesammykins/okta-cli.git
   cd okta-cli
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install in development mode:**
   ```bash
   pip install -e .
   ```

5. **Verify installation:**
   ```bash
   okta-cli --version
   okta-cli --help
   ```

### Development Dependencies

Install additional development dependencies:

```bash
# Install development requirements
pip install -r requirements-dev.txt

# Or install individual packages
pip install pytest pytest-cov black flake8 mypy
```

## Project Structure

```
okta-cli/
├── okta_cli/                   # Main package directory
│   ├── __init__.py
│   ├── main.py                 # Main CLI entry point
│   ├── config.py               # Configuration management
│   ├── config_commands.py      # Configuration CLI commands
│   ├── enhanced_config.py      # Enhanced configuration features
│   ├── users.py                # User management commands
│   ├── groups.py               # Group management commands
│   ├── applications.py         # Application management commands
│   ├── sessions.py             # Session management commands
│   ├── policies.py             # Policy and group rules commands
│   ├── authorization.py        # Authorization server commands
│   ├── logs.py                 # Event log analysis commands
│   ├── factors.py              # MFA factor management commands
│   ├── errors.py               # Error handling utilities
│   ├── formatting.py           # Output formatting utilities
│   ├── progress.py             # Progress indicator utilities
│   ├── interactive.py          # Interactive prompt utilities
│   └── security.py             # Security and encryption utilities
├── tests/                      # Test directory
│   ├── __init__.py
│   ├── test_main.py            # Main CLI tests
│   ├── test_config.py          # Configuration tests
│   ├── test_users.py           # User management tests
│   ├── test_groups.py          # Group management tests
│   ├── test_phase5.py          # Phase 5 feature tests
│   ├── test_enhanced_config.py # Enhanced configuration tests
│   ├── test_error_handling.py  # Error handling tests
│   ├── test_security.py        # Security feature tests
│   └── test_usability.py       # Usability tests
├── docs/                       # Documentation
│   ├── index.md
│   ├── installation.md
│   ├── quickstart.md
│   ├── commands.md
│   ├── configuration.md
│   ├── use-cases.md
│   ├── troubleshooting.md
│   └── development.md
├── scripts/                    # Development scripts
│   ├── release.sh             # Release automation
│   └── setup-dev.sh           # Development setup
├── pyproject.toml             # Project configuration
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── README.md                  # Project README
├── LICENSE                    # License file
└── CHANGELOG.md              # Change log
```

## Core Architecture

### Command Structure

The CLI follows a modular architecture with separate modules for each feature area:

1. **main.py** - Main CLI entry point and command group setup
2. **config.py** - Configuration management and persistence
3. **users.py** - User lifecycle operations
4. **groups.py** - Group management operations
5. **applications.py** - Application management
6. **sessions.py** - Session management
7. **policies.py** - Policy and group rules
8. **authorization.py** - Authorization servers
9. **logs.py** - Event log analysis
10. **factors.py** - MFA management

### Common Patterns

#### Configuration Loading

```python
from okta_cli.config import get_effective_config

def my_command():
    domain, token = get_effective_config(profile)
    # Use domain and token for API calls
```

#### Error Handling

```python
from okta_cli.errors import handle_api_error, handle_network_error

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    handle_network_error(e)
except Exception as e:
    handle_api_error(response)
```

#### Output Formatting

```python
from okta_cli.formatting import format_output

def my_command(output_format):
    data = get_data()
    format_output(data, output_format)
```

## Development Commands

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::test_create_user

# Run with coverage
pytest --cov=okta_cli

# Run with verbose output
pytest -v

# Run tests and generate HTML coverage report
pytest --cov=okta_cli --cov-report=html
```

### Code Quality

```bash
# Format code with Black
black okta_cli/

# Check code style with flake8
flake8 okta_cli/

# Type checking with mypy
mypy okta_cli/

# Run all quality checks
black okta_cli/ && flake8 okta_cli/ && mypy okta_cli/
```

### Package Management

```bash
# Build package
python -m build

# Install package locally
pip install -e .

# Create distribution packages
python -m build --sdist --wheel

# Upload to PyPI (with credentials)
twine upload dist/*
```

## Testing

### Test Structure

Tests are organized by module:

- **test_main.py** - Main CLI functionality
- **test_config.py** - Configuration management
- **test_users.py** - User management operations
- **test_groups.py** - Group management operations
- **test_phase5.py** - Advanced features (applications, sessions, policies, etc.)

### Writing Tests

#### Basic Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from okta_cli.users import users

class TestUserCommands:
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = []
    
    @patch('okta_cli.users.requests.get')
    @patch('okta_cli.users.get_effective_config')
    def test_list_users_success(self, mock_config, mock_get):
        """Test successful user listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response
        
        result = self.runner.invoke(users, ['list'])
        
        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()
```

#### Testing with Mocks

```python
from unittest.mock import Mock, patch, MagicMock

# Mock API responses
mock_response = Mock()
mock_response.status_code = 200
mock_response.json.return_value = {"id": "user123", "profile": {"email": "test@example.com"}}

# Mock configuration
with patch('okta_cli.config.get_effective_config') as mock_config:
    mock_config.return_value = ("test.okta.com", "test-token")
    # Test code here
```

#### Integration Tests

```python
def test_user_creation_workflow():
    """Test complete user creation workflow."""
    with patch('okta_cli.users.requests.post') as mock_post:
        mock_post.return_value = Mock(status_code=201, json=lambda: {"id": "user123"})
        
        result = runner.invoke(users, [
            'create',
            '--first-name', 'John',
            '--last-name', 'Doe',
            '--email', 'john.doe@example.com',
            '--login', 'john.doe@example.com'
        ])
        
        assert result.exit_code == 0
        mock_post.assert_called_once()
```

### Test Configuration

Create test configuration file (`pytest.ini`):

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## Code Standards

### Python Style Guide

Follow PEP 8 with these specific guidelines:

```python
# Imports - grouped and sorted
import os
import sys
from typing import Dict, List, Optional

import click
import requests

from okta_cli.config import get_effective_config
from okta_cli.errors import handle_api_error

# Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Functions
def create_user(first_name: str, last_name: str, email: str, login: str) -> Dict:
    """Create a new user in Okta.
    
    Args:
        first_name: User's first name
        last_name: User's last name
        email: User's email address
        login: User's login identifier
        
    Returns:
        Dict containing user data
        
    Raises:
        ApiError: If API request fails
    """
    pass

# Classes
class UserManager:
    """Manage Okta user operations."""
    
    def __init__(self, domain: str, token: str):
        self.domain = domain
        self.token = token
        self.base_url = f"https://{domain}/api/v1"
```

### Error Handling

```python
from okta_cli.errors import (
    ApiError,
    ConfigurationError,
    NetworkError,
    handle_api_error
)

def api_call():
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise NetworkError("Request timed out")
    except requests.exceptions.RequestException as e:
        handle_api_error(response, e)
    except Exception as e:
        raise ApiError(f"Unexpected error: {e}")
```

### Documentation

```python
def create_user(first_name: str, last_name: str, email: str, login: str, 
                profile: Optional[str] = None) -> Dict:
    """Create a new user in Okta.
    
    This function creates a new user account in Okta with the provided
    information. The user will be created in an ACTIVE state by default.
    
    Args:
        first_name: User's first name
        last_name: User's last name
        email: User's email address
        login: User's login identifier (usually same as email)
        profile: Configuration profile to use (optional)
        
    Returns:
        Dict containing the created user data with keys:
        - id: User ID
        - profile: User profile information
        - status: User status
        
    Raises:
        ApiError: If the API request fails
        ConfigurationError: If configuration is invalid
        NetworkError: If network request fails
        
    Examples:
        >>> user = create_user("John", "Doe", "john@example.com", "john@example.com")
        >>> print(user["id"])
        00u1234567890abcdef
        
        >>> user = create_user("Jane", "Smith", "jane@example.com", "jane@example.com", "prod")
    """
    pass
```

## Adding New Features

### 1. Planning

Before adding new features:

1. **Review existing code** for similar patterns
2. **Check API documentation** for endpoint requirements
3. **Design command structure** following existing conventions
4. **Plan test coverage** for new functionality

### 2. Implementation

#### Add New Command Module

Create new file (`okta_cli/new_feature.py`):

```python
import click
import requests
from typing import Dict, List, Optional

from okta_cli.config import get_effective_config
from okta_cli.errors import handle_api_error, handle_network_error
from okta_cli.formatting import format_output

@click.group()
def new_feature():
    """Manage new feature operations."""
    pass

@new_feature.command()
@click.option('--profile', help='Configuration profile to use')
@click.option('--output', type=click.Choice(['table', 'json', 'csv', 'yaml']), 
              default='table', help='Output format')
def list(profile, output):
    """List new feature items."""
    try:
        domain, token = get_effective_config(profile)
        
        headers = {
            'Authorization': f'SSWS {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        url = f"https://{domain}/api/v1/new-endpoint"
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        format_output(data, output)
        
    except requests.exceptions.RequestException as e:
        handle_network_error(e)
    except Exception as e:
        handle_api_error(response)
```

#### Update Main CLI

Add to `okta_cli/main.py`:

```python
from okta_cli.new_feature import new_feature

@click.group()
def cli():
    """Okta CLI tool."""
    pass

# Add new command group
cli.add_command(new_feature)
```

### 3. Testing

Create test file (`tests/test_new_feature.py`):

```python
import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from okta_cli.new_feature import new_feature

class TestNewFeature:
    def setup_method(self):
        self.runner = CliRunner()
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = []
    
    @patch('okta_cli.new_feature.requests.get')
    @patch('okta_cli.new_feature.get_effective_config')
    def test_list_success(self, mock_config, mock_get):
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response
        
        result = self.runner.invoke(new_feature, ['list'])
        
        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()
```

### 4. Documentation

Update relevant documentation:

- Add command to `docs/commands.md`
- Add examples to `docs/use-cases.md`
- Update `README.md` if needed

## Release Process

### Version Management

1. **Update version** in `pyproject.toml`:
   ```toml
   [project]
   version = "1.2.3"
   ```

2. **Update changelog** in `CHANGELOG.md`:
   ```markdown
   ## [1.2.3] - 2024-01-15
   
   ### Added
   - New feature description
   
   ### Changed
   - Changed feature description
   
   ### Fixed
   - Fixed issue description
   ```

### Automated Release

The project uses GitHub Actions for automated releases:

1. **Create release tag:**
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

2. **GitHub Actions will automatically:**
   - Run tests
   - Build packages
   - Publish to PyPI
   - Create GitHub release
   - Build and publish Docker image

### Manual Release

For manual releases:

```bash
# Run tests
pytest

# Build packages
python -m build

# Upload to PyPI
twine upload dist/*

# Create GitHub release
gh release create v1.2.3 --generate-notes
```

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch:**
   ```bash
   git checkout -b feature/new-feature-name
   ```

3. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "Add new feature description"
   ```

4. **Run tests:**
   ```bash
   pytest
   black okta_cli/
   flake8 okta_cli/
   ```

5. **Push changes:**
   ```bash
   git push origin feature/new-feature-name
   ```

6. **Create pull request**

### Pull Request Guidelines

- **Clear description** of changes
- **Include tests** for new functionality
- **Update documentation** as needed
- **Follow code style** guidelines
- **Ensure all tests pass**

### Code Review Process

1. **Automated checks** must pass
2. **Manual review** by maintainers
3. **Testing** on different environments
4. **Documentation** review
5. **Merge** after approval

## Security Considerations

### API Token Handling

- **Never log tokens** in plain text
- **Use environment variables** for testing
- **Implement secure storage** for production
- **Rotate tokens** regularly

### Input Validation

```python
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_domain(domain: str) -> bool:
    """Validate Okta domain format."""
    pattern = r'^[a-zA-Z0-9.-]+\.okta\.com$'
    return re.match(pattern, domain) is not None
```

### Error Handling

- **Don't expose sensitive data** in error messages
- **Sanitize inputs** before processing
- **Log security events** appropriately
- **Implement rate limiting** for API calls

## Best Practices

### 1. Code Organization

- **One command per function**
- **Shared utilities** in separate modules
- **Clear module boundaries**
- **Consistent naming conventions**

### 2. Error Handling

- **Specific error types** for different scenarios
- **User-friendly error messages**
- **Proper logging** for debugging
- **Graceful degradation** when possible

### 3. Testing

- **Unit tests** for individual functions
- **Integration tests** for workflows
- **Mock external dependencies**
- **Test error conditions**

### 4. Documentation

- **Clear function docstrings**
- **Example usage** in documentation
- **Keep README updated**
- **Document breaking changes**

### 5. Performance

- **Use appropriate timeouts**
- **Implement retry logic**
- **Cache configuration** when appropriate
- **Use pagination** for large datasets

This development guide provides a comprehensive overview of the development process for the Okta CLI project. Follow these guidelines to ensure consistent, high-quality contributions to the project.