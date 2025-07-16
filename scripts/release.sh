#!/bin/bash

# Okta CLI Release Script
# This script helps create releases manually

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Okta CLI Release Script${NC}"
echo "================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "okta_cli" ]; then
    echo -e "${RED}❌ Error: Must be run from the project root directory${NC}"
    exit 1
fi

# Check if git is clean
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ Error: Working directory is not clean. Please commit or stash changes.${NC}"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep -E "^version = " pyproject.toml | cut -d'"' -f2)
echo -e "${YELLOW}📋 Current version: ${CURRENT_VERSION}${NC}"

# Ask for version type
echo ""
echo "Select version bump type:"
echo "1) Patch (bug fixes)"
echo "2) Minor (new features)"
echo "3) Major (breaking changes)"
read -p "Enter choice (1-3): " choice

case $choice in
    1) VERSION_TYPE="patch" ;;
    2) VERSION_TYPE="minor" ;;
    3) VERSION_TYPE="major" ;;
    *) echo -e "${RED}❌ Invalid choice${NC}"; exit 1 ;;
esac

# Confirm
echo -e "${YELLOW}🔄 Will perform ${VERSION_TYPE} version bump${NC}"
read -p "Continue? (y/N): " confirm

if [[ $confirm != [yY] ]]; then
    echo -e "${YELLOW}⏹️  Release cancelled${NC}"
    exit 0
fi

# Run tests first
echo -e "${GREEN}🧪 Running tests...${NC}"
if command -v pytest &> /dev/null; then
    pytest tests/ -v || {
        echo -e "${RED}❌ Tests failed${NC}"
        exit 1
    }
else
    echo -e "${YELLOW}⚠️  pytest not found, skipping tests${NC}"
fi

# Install bump2version if not present
if ! command -v bump2version &> /dev/null; then
    echo -e "${GREEN}📦 Installing bump2version...${NC}"
    pip install bump2version
fi

# Bump version
echo -e "${GREEN}📈 Bumping version...${NC}"
bump2version $VERSION_TYPE --verbose

# Get new version
NEW_VERSION=$(grep -E "^version = " pyproject.toml | cut -d'"' -f2)
echo -e "${GREEN}✅ Version bumped from ${CURRENT_VERSION} to ${NEW_VERSION}${NC}"

# Build package
echo -e "${GREEN}🏗️  Building package...${NC}"
python -m build

# Ask about pushing
echo ""
echo -e "${YELLOW}🏷️  Created tag: v${NEW_VERSION}${NC}"
read -p "Push to remote? (y/N): " push_confirm

if [[ $push_confirm == [yY] ]]; then
    echo -e "${GREEN}⬆️  Pushing to remote...${NC}"
    git push
    git push --tags
    echo -e "${GREEN}✅ Release ${NEW_VERSION} pushed to remote${NC}"
    echo ""
    echo -e "${GREEN}📝 Next steps:${NC}"
    echo "1. Go to GitHub releases page"
    echo "2. Create release from tag v${NEW_VERSION}"
    echo "3. The GitHub Action will handle building and publishing"
else
    echo -e "${YELLOW}⏹️  Not pushed to remote${NC}"
    echo -e "${YELLOW}📝 To push later, run:${NC}"
    echo "   git push"
    echo "   git push --tags"
fi

echo ""
echo -e "${GREEN}🎉 Release ${NEW_VERSION} ready!${NC}"