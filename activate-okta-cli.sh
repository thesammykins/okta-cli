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
