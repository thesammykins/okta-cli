#!/bin/bash

# CI Check Script: Detect new legacy config API references
# This script should be run in CI to fail if new legacy references are introduced

set -e

echo "🔍 Checking for legacy config API references..."

# Define the expected count of legacy references
EXPECTED_GET_CONFIG_CALLS=70
EXPECTED_GET_CONFIG_FILES=9
EXPECTED_IMPORT_CONFIG_FILES=11

# Count current legacy references
CURRENT_GET_CONFIG_CALLS=$(find okta_cli -name "*.py" -exec grep -n "config\.get_config(" {} + | wc -l | tr -d ' ')
CURRENT_GET_CONFIG_FILES=$(find okta_cli -name "*.py" -exec grep -l "config\.get_config(" {} + | wc -l | tr -d ' ')
CURRENT_IMPORT_CONFIG_FILES=$(find okta_cli -name "*.py" -exec grep -l "from.*import.*config\|import config" {} + | wc -l | tr -d ' ')

echo "📊 Current legacy API usage:"
echo "  - config.get_config() calls: $CURRENT_GET_CONFIG_CALLS (across $CURRENT_GET_CONFIG_FILES files)"
echo "  - config import statements found in $CURRENT_IMPORT_CONFIG_FILES files"

echo "📋 Expected legacy API usage:"
echo "  - config.get_config() calls: $EXPECTED_GET_CONFIG_CALLS (across $EXPECTED_GET_CONFIG_FILES files)"
echo "  - config import statements expected in $EXPECTED_IMPORT_CONFIG_FILES files"

# Check if counts have increased (new legacy references introduced)
if [ "$CURRENT_GET_CONFIG_CALLS" -gt "$EXPECTED_GET_CONFIG_CALLS" ]; then
    echo "❌ FAILURE: New config.get_config() references detected!"
    echo "   Expected: $EXPECTED_GET_CONFIG_CALLS calls, Found: $CURRENT_GET_CONFIG_CALLS calls"
    echo "   Please use enhanced_config.get_effective_config() instead of legacy config.get_config()"
    
    echo "🔍 Files with config.get_config() references:"
    find okta_cli -name "*.py" -exec grep -l "config\.get_config(" {} +
    
    exit 1
fi

if [ "$CURRENT_IMPORT_CONFIG_FILES" -gt "$EXPECTED_IMPORT_CONFIG_FILES" ]; then
    echo "❌ FAILURE: New legacy config import statements detected!"
    echo "   Expected: $EXPECTED_IMPORT_CONFIG_FILES files, Found: $CURRENT_IMPORT_CONFIG_FILES files"
    echo "   Please use 'from .enhanced_config import get_effective_config' instead"
    
    echo "🔍 Files with config import statements:"
    find okta_cli -name "*.py" -exec grep -l "from.*import.*config\|import config" {} +
    
    exit 1
fi

# Additional check for specific problematic patterns
echo "🔍 Checking for specific legacy patterns..."

# Check for new direct config.get_config usage without enhanced_config fallback
NEW_DIRECT_USAGE=$(find okta_cli -name "*.py" -exec grep -L "from.*enhanced_config" {} + | xargs grep -l "config\.get_config(" 2>/dev/null | grep -v "config.py\|config_commands.py\|main.py\|groups.py" || true)

if [ ! -z "$NEW_DIRECT_USAGE" ]; then
    echo "❌ FAILURE: Files using config.get_config() without enhanced_config import found:"
    echo "$NEW_DIRECT_USAGE"
    echo "   These files should import and use get_effective_config() instead"
    exit 1
fi

echo "✅ SUCCESS: No new legacy config API references detected!"
echo "📝 Current audit file: scripts/legacy_config_audit.txt"
echo "🔄 Continue with config migration according to the plan"
