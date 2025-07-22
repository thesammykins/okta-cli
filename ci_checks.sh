#!/bin/bash

# Static Analysis & Automated CI Checks Script
# Usage: ./ci_checks.sh

set -e  # Exit on any error

OKTA_CLI_PATH="okta_cli"
EXIT_CODE=0

echo "🔍 Starting Static Analysis & Automated CI Checks..."
echo "=================================================="

# 1. Ruff Linting (F,E,W,I rules)
echo "1️⃣  Running ruff linting (F,E,W,I rules)..."
if ruff check --select F,E,W,I "$OKTA_CLI_PATH"; then
    echo "✅ Ruff linting passed"
else
    echo "❌ Ruff linting failed"
    EXIT_CODE=1
fi

echo ""

# 2. MyPy Type Checking
echo "2️⃣  Running mypy type checking..."
if mypy "$OKTA_CLI_PATH"; then
    echo "✅ MyPy type checking passed"
else
    echo "❌ MyPy type checking failed"
    EXIT_CODE=1
fi

echo ""

# 3. Bandit Security Analysis
echo "3️⃣  Running bandit security analysis..."
if bandit -r "$OKTA_CLI_PATH"; then
    echo "✅ Bandit security analysis passed"
else
    echo "❌ Bandit security analysis failed"
    EXIT_CODE=1
fi

echo ""

# 4. Legacy config.get_config Pattern Check
echo "4️⃣  Checking for legacy config.get_config patterns..."
CONFIG_PATTERN_COUNT=$(grep -r "config\.get_config(" "$OKTA_CLI_PATH" --exclude-dir="__pycache__" | grep -v "Replace config.get_config()" | wc -l || true)

if [ "$CONFIG_PATTERN_COUNT" -eq 0 ]; then
    echo "✅ No legacy config.get_config patterns found"
else
    echo "❌ Found $CONFIG_PATTERN_COUNT instances of legacy config.get_config pattern"
    echo "   These patterns should be migrated to use enhanced_config.get_effective_config()"
    grep -r "config\.get_config(" "$OKTA_CLI_PATH" --exclude-dir="__pycache__" | grep -v "Replace config.get_config()" || true
    EXIT_CODE=1
fi

echo ""
echo "=================================================="

# Final Results
if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 All static analysis checks passed!"
else
    echo "💥 Static analysis checks failed - build should fail"
    echo "   Please fix the issues above before proceeding"
fi

echo ""
echo "Summary:"
echo "- Ruff linting: $([ $EXIT_CODE -eq 0 ] && echo "PASS" || echo "FAIL")"
echo "- MyPy type checking: $([ $EXIT_CODE -eq 0 ] && echo "PASS" || echo "FAIL")" 
echo "- Bandit security: $([ $EXIT_CODE -eq 0 ] && echo "PASS" || echo "FAIL")"
echo "- Legacy pattern check: PASS"

exit $EXIT_CODE
