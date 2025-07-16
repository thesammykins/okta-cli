#!/bin/bash

# Okta CLI Environment Setup Script
# This script sets up the okta-cli environment and provides helper functions

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
check_directory() {
    if [[ ! -f "$SCRIPT_DIR/okta_cli/main.py" ]]; then
        print_error "This script must be run from the okta-cli project directory"
        exit 1
    fi
}

# Check Python version
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_info "Using Python $python_version"
}

# Setup virtual environment
setup_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    source "$VENV_DIR/bin/activate"
    
    if [[ -f "$REQUIREMENTS_FILE" ]]; then
        pip install -r "$REQUIREMENTS_FILE"
    fi
    
    # Install the CLI in development mode
    pip install -e .
    
    print_success "Dependencies installed"
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    source "$VENV_DIR/bin/activate"
    
    if okta-cli --help &> /dev/null; then
        print_success "Okta CLI is working correctly"
    else
        print_error "Okta CLI installation failed"
        exit 1
    fi
}

# Create activation script
create_activation_script() {
    local activation_script="$SCRIPT_DIR/activate-okta-cli.sh"
    
    cat > "$activation_script" << 'EOF'
#!/bin/bash

# Okta CLI Activation Script
# Source this script to activate the environment and load helper functions

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Activate virtual environment
if [[ -f "$VENV_DIR/bin/activate" ]]; then
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✅ Okta CLI environment activated${NC}"
else
    echo -e "${RED}❌ Virtual environment not found. Run ./setup-okta-cli.sh first${NC}"
    return 1
fi

# Helper functions
okta-help() {
    echo -e "${BLUE}🔧 Okta CLI Helper Functions:${NC}"
    echo ""
    echo "  okta-help              - Show this help"
    echo "  okta-config            - Quick configuration wizard"
    echo "  okta-status            - Show configuration status"
    echo "  okta-test              - Test connectivity"
    echo "  okta-profiles          - List all profiles"
    echo "  okta-users             - List users (requires config)"
    echo "  okta-groups            - List groups (requires config)"
    echo "  okta-apps              - List applications (requires config)"
    echo "  okta-logs              - Show recent logs (requires config)"
    echo "  okta-health            - Check system health"
    echo ""
    echo -e "${YELLOW}📖 For full documentation, see: AGENT.md${NC}"
    echo -e "${YELLOW}💡 First time? Run: okta-config${NC}"
}

okta-config() {
    echo -e "${BLUE}🔧 Starting configuration wizard...${NC}"
    okta-cli config wizard
}

okta-status() {
    echo -e "${BLUE}📊 Configuration Status:${NC}"
    okta-cli config status
}

okta-test() {
    echo -e "${BLUE}🔍 Testing connectivity...${NC}"
    okta-cli config health
}

okta-profiles() {
    echo -e "${BLUE}👤 Available Profiles:${NC}"
    okta-cli config list
}

okta-users() {
    echo -e "${BLUE}👥 Users (first 20):${NC}"
    okta-cli users list --output table | head -20
}

okta-groups() {
    echo -e "${BLUE}🔍 Groups (first 20):${NC}"
    okta-cli groups list --output table | head -20
}

okta-apps() {
    echo -e "${BLUE}📱 Applications (first 20):${NC}"
    okta-cli applications list --output table | head -20
}

okta-logs() {
    echo -e "${BLUE}📋 Recent Logs (last 10):${NC}"
    okta-cli logs list --limit 10 --output table
}

okta-health() {
    echo -e "${BLUE}🏥 System Health Check:${NC}"
    echo ""
    echo "Virtual Environment: $(which python)"
    echo "Python Version: $(python --version)"
    echo "Okta CLI Version: $(okta-cli --version 2>/dev/null || echo 'Unable to determine')"
    echo ""
    okta-cli config health
}

# Show help on activation
okta-help
EOF

    chmod +x "$activation_script"
    print_success "Activation script created at: $activation_script"
}

# Create quick launcher
create_launcher() {
    local launcher_script="$SCRIPT_DIR/okta"
    
    cat > "$launcher_script" << 'EOF'
#!/bin/bash

# Okta CLI Quick Launcher
# This script allows running okta-cli commands without manual activation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    echo "❌ Virtual environment not found. Run ./setup-okta-cli.sh first"
    exit 1
fi

# Activate environment and run command
source "$VENV_DIR/bin/activate"
okta-cli "$@"
EOF

    chmod +x "$launcher_script"
    print_success "Quick launcher created at: $launcher_script"
}

# Main setup function
main() {
    print_info "Setting up Okta CLI environment..."
    echo ""
    
    check_directory
    check_python
    setup_venv
    install_dependencies
    test_installation
    create_activation_script
    create_launcher
    
    echo ""
    print_success "🎉 Okta CLI environment setup complete!"
    echo ""
    print_info "Usage options:"
    echo "  1. Source the activation script: source ./activate-okta-cli.sh"
    echo "  2. Use the quick launcher: ./okta --help"
    echo "  3. Manual activation: source venv/bin/activate && okta-cli"
    echo ""
    print_info "Next steps:"
    echo "  1. Run: source ./activate-okta-cli.sh"
    echo "  2. Run: okta-config (to configure your Okta settings)"
    echo "  3. Run: okta-help (to see available helper functions)"
    echo ""
    print_warning "Remember to configure your Okta domain and API token before using the CLI"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
