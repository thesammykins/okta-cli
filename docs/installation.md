# Installation Guide

This guide covers all the different ways to install the Okta CLI tool.

## Prerequisites

- **Python 3.8 or higher** - Check your version with `python --version`
- **pip package manager** - Usually comes with Python
- **Valid Okta account** with API token access

## Installation Methods

### From PyPI (Recommended)

The easiest way to install the Okta CLI is from PyPI:

```bash
pip install okta-cli
```

To upgrade to the latest version:

```bash
pip install --upgrade okta-cli
```

### From GitHub Releases

1. Go to the [releases page](https://github.com/thesammykins/okta-cli/releases)
2. Download the latest `.whl` file
3. Install it with pip:

```bash
pip install okta-cli-*.whl
```

### From Source (Development)

For development or to get the latest unreleased features:

```bash
# Clone the repository
git clone https://github.com/thesammykins/okta-cli.git
cd okta-cli

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Docker Installation

#### Pull from GitHub Container Registry

```bash
# Pull the latest image
docker pull ghcr.io/thesammykins/okta-cli:latest

# Pull a specific version
docker pull ghcr.io/thesammykins/okta-cli:v1.0.0
```

#### Running with Docker

```bash
# Run interactively
docker run -it -v ~/.okta-cli:/home/oktauser/.okta-cli ghcr.io/thesammykins/okta-cli:latest

# Run a specific command
docker run -v ~/.okta-cli:/home/oktauser/.okta-cli ghcr.io/thesammykins/okta-cli:latest users list --profile prod

# Run with environment variables
docker run -e OKTA_DOMAIN=company.okta.com -e OKTA_TOKEN=your-token ghcr.io/thesammykins/okta-cli:latest users list
```

## Post-Installation Setup

After installation, you need to configure the CLI:

### Quick Setup

Run the interactive configuration wizard:

```bash
okta-cli config wizard
```

### Manual Configuration

```bash
# Configure with specific profile
okta-cli config create production --domain company.okta.com --token your-api-token

# Activate the profile
okta-cli config activate production
```

## Verification

Test your installation:

```bash
# Check version
okta-cli --version

# Check configuration
okta-cli config health

# Test basic functionality
okta-cli users list --limit 5
```

## Virtual Environment (Recommended)

For better package management, use a virtual environment:

```bash
# Create virtual environment
python -m venv okta-cli-env

# Activate it
source okta-cli-env/bin/activate  # On Windows: okta-cli-env\Scripts\activate

# Install okta-cli
pip install okta-cli

# When done, deactivate
deactivate
```

## Platform-Specific Notes

### macOS

```bash
# If using Homebrew Python
brew install python
pip3 install okta-cli

# If using system Python, you might need
sudo pip3 install okta-cli
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip
pip3 install okta-cli

# RHEL/CentOS/Fedora
sudo dnf install python3 python3-pip
pip3 install okta-cli
```

### Windows

```bash
# Using Python from python.org
python -m pip install okta-cli

# Using Windows Subsystem for Linux (WSL)
pip3 install okta-cli
```

## Troubleshooting Installation

### Common Issues

1. **Permission Errors**
   ```bash
   # Use --user flag
   pip install --user okta-cli
   
   # Or use virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate
   pip install okta-cli
   ```

2. **Python Version Issues**
   ```bash
   # Check Python version
   python --version
   
   # Use specific Python version
   python3.9 -m pip install okta-cli
   ```

3. **Network/Proxy Issues**
   ```bash
   # Use proxy
   pip install --proxy https://proxy.company.com:8080 okta-cli
   
   # Skip SSL verification (not recommended)
   pip install --trusted-host pypi.org --trusted-host pypi.python.org okta-cli
   ```

4. **Docker Permission Issues**
   ```bash
   # Add user to docker group (Linux)
   sudo usermod -aG docker $USER
   
   # Or run with sudo
   sudo docker run ...
   ```

### Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Search [existing issues](https://github.com/thesammykins/okta-cli/issues)
3. Create a [new issue](https://github.com/thesammykins/okta-cli/issues/new/choose)

## Next Steps

After installation:

1. [Configure the CLI](configuration.md)
2. Follow the [Quick Start Guide](quickstart.md)
3. Explore [Command Reference](commands.md)
4. Review [Common Use Cases](use-cases.md)