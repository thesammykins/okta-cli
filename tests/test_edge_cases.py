#!/usr/bin/env python3
"""
Test script to systematically test edge cases for user and group identifier resolution.
This script will help identify concrete edge inputs for use as test vectors.
"""

import subprocess
import sys

def run_command(command, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_case(description, command, expected_success=True):
    """Test a specific case and report results."""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"CMD:  {command}")
    print(f"{'='*60}")
    
    returncode, stdout, stderr = run_command(command)
    
    if returncode == 0 and expected_success:
        status = "✅ PASS"
    elif returncode != 0 and not expected_success:
        status = "✅ PASS (Expected Failure)"
    else:
        status = "❌ FAIL"
    
    print(f"STATUS: {status}")
    print(f"OUTPUT:\n{stdout}")
    if stderr:
        print(f"STDERR:\n{stderr}")
    
    return returncode == 0

def main():
    """Run comprehensive edge case tests."""
    profile = "test"  # Using the test profile
    
    print("OKTA CLI IDENTIFIER RESOLUTION EDGE CASE TESTING")
    print("=" * 60)
    
    # Test cases for group resolution
    group_tests = [
        # Basic functionality
        ("Group with spaces", f'okta-cli groups list-members "QA Team" --profile {profile} --debug'),
        ("Group with spaces and mixed case", f'okta-cli groups list-members "qa team" --profile {profile} --debug'),
        ("Group with special characters", f'okta-cli groups list-members "Test & Special" --profile {profile} --debug'),
        ("Single word group", f'okta-cli groups list-members "Everyone" --profile {profile} --debug'),
        ("Group with numbers", f'okta-cli groups list-members "testing123" --profile {profile} --debug'),
        
        # Error cases
        ("Non-existent group", f'okta-cli groups list-members "NonExistentGroup" --profile {profile} --debug', False),
        ("Empty group name", f'okta-cli groups list-members "" --profile {profile} --debug', False),
    ]
    
    # Test cases for user resolution
    user_tests = [
        # Basic functionality
        ("User by email (lowercase)", f'okta-cli groups add-user "QA Team" "evelyn.tester@example.com" --profile {profile} --debug'),
        ("User by email (mixed case)", f'okta-cli groups add-user "QA Team" "EVELYN.TESTER@EXAMPLE.COM" --profile {profile} --debug'),
        ("User by email (different domain)", f'okta-cli groups add-user "QA Team" "samantha.myers@ferocia.com.au" --profile {profile} --debug'),
        
        # Error cases  
        ("Non-existent user email", f'okta-cli groups add-user "QA Team" "nonexistent@example.com" --profile {profile} --debug', False),
        ("Invalid email format", f'okta-cli groups add-user "QA Team" "not-an-email" --profile {profile} --debug', False),
        ("Empty user identifier", f'okta-cli groups add-user "QA Team" "" --profile {profile} --debug', False),
    ]
    
    # Combined edge cases
    combined_tests = [
        ("Remove user by email from group by name", f'okta-cli groups remove-user "QA Team" "evelyn.tester@example.com" --profile {profile} --debug'),
        ("Show group by name with spaces", f'okta-cli groups show "Temp Contractors" --profile {profile}'),
    ]
    
    # Run all tests
    results = {
        "group_tests": [],
        "user_tests": [], 
        "combined_tests": []
    }
    
    print("\n\n🔍 TESTING GROUP IDENTIFIER RESOLUTION")
    for desc, cmd, *expected in group_tests:
        expected_success = expected[0] if expected else True
        success = test_case(desc, cmd, expected_success)
        results["group_tests"].append((desc, success))
    
    print("\n\n👤 TESTING USER IDENTIFIER RESOLUTION") 
    for desc, cmd, *expected in user_tests:
        expected_success = expected[0] if expected else True
        success = test_case(desc, cmd, expected_success)
        results["user_tests"].append((desc, success))
    
    print("\n\n🔄 TESTING COMBINED SCENARIOS")
    for desc, cmd, *expected in combined_tests:
        expected_success = expected[0] if expected else True
        success = test_case(desc, cmd, expected_success)
        results["combined_tests"].append((desc, success))
    
    # Summary report
    print("\n\n📊 SUMMARY REPORT")
    print("=" * 60)
    
    total_tests = 0
    total_passed = 0
    
    for category, tests in results.items():
        category_name = category.replace("_", " ").title()
        passed = sum(1 for _, success in tests if success)
        total = len(tests)
        
        print(f"{category_name}: {passed}/{total} passed")
        total_tests += total
        total_passed += passed
        
        for desc, success in tests:
            status = "✅" if success else "❌"
            print(f"  {status} {desc}")
    
    print(f"\nOVERALL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
