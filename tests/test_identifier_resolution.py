"""
Comprehensive unit tests for identifier resolution functionality.

Tests cover user and group identifier resolution with various scenarios including:
- Direct ID lookups
- Email and login resolution
- Group names with spaces, mixed case, special characters
- Not-found scenarios
- Ambiguous results
- Logging behavior when disabled/enabled
- Error handling and exception scenarios

Target: 95%+ branch coverage for resolver module
"""

import pytest
import responses
import logging
import json
import os
from unittest.mock import patch, MagicMock
from okta_cli.utils import (
    resolve_user_id,
    resolve_group_id, 
    resolve_app_id,
    get_user_by_identifier,
    get_group_by_identifier,
    get_app_by_identifier,
    is_okta_id,
    normalize_string
)
from okta_cli.errors import AmbiguousIdentifierError, ResolutionError


class TestIsOktaId:
    """Test cases for is_okta_id function."""
    
    def test_valid_okta_id_20_chars(self):
        """Test valid 20-character Okta ID."""
        assert is_okta_id("00u1a2b3c4d5e6f7g8h9") == True
        
    def test_valid_simple_id(self):
        """Test simple alphanumeric ID for backward compatibility."""
        assert is_okta_id("user123") == True
        assert is_okta_id("group456") == True
        
    def test_invalid_empty_id(self):
        """Test empty identifier."""
        assert is_okta_id("") == False
        assert is_okta_id(None) == False
        
    def test_invalid_special_chars(self):
        """Test identifiers with special characters."""
        assert is_okta_id("user@example.com") == False
        assert is_okta_id("user-with-dash") == False
        assert is_okta_id("user_with_underscore") == False
        
    def test_invalid_too_long(self):
        """Test identifiers that are too long."""
        assert is_okta_id("a" * 21) == False
        assert is_okta_id("verylongidentifierthatexceeds20chars") == False


class TestNormalizeString:
    """Test cases for normalize_string function."""
    
    def test_normalize_basic(self):
        """Test basic normalization."""
        assert normalize_string("Test") == "test"
        assert normalize_string("  Test  ") == "test"
        
    def test_normalize_unicode(self):
        """Test Unicode normalization."""
        assert normalize_string("Café") == "café"
        assert normalize_string("naïve") == "naïve"
        
    def test_normalize_empty(self):
        """Test empty string normalization."""
        assert normalize_string("") == ""
        assert normalize_string("   ") == ""


class TestResolveUserId:
    """Test cases for resolve_user_id function."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.domain = "test.okta.com"
        self.token = "test-token-123"
        self.base_url = f"https://{self.domain}/api/v1"
        
    def test_resolve_user_already_okta_id(self):
        """Test resolving user when identifier is already an Okta ID."""
        user_id = "00u1a2b3c4d5e6f7g8h9"
        result = resolve_user_id(user_id, self.domain, self.token)
        assert result == user_id
        
    def test_resolve_user_empty_identifier(self):
        """Test resolving user with empty identifier."""
        assert resolve_user_id("", self.domain, self.token) is None
        assert resolve_user_id("   ", self.domain, self.token) is None
        assert resolve_user_id(None, self.domain, self.token) is None
        
    @responses.activate
    def test_resolve_user_direct_lookup_success(self):
        """Test successful direct user lookup by ID."""
        user_id = "test-user-123"
        responses.add(
            responses.GET,
            f"{self.base_url}/users/{user_id}",
            json={"id": user_id, "profile": {"email": "test@example.com"}},
            status=200
        )
        
        result = resolve_user_id(user_id, self.domain, self.token)
        assert result == user_id
        
    def test_resolve_user_direct_lookup_by_email(self):
        """Test successful direct user lookup by URL-encoded email."""
        email = "test@example.com"
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        # First attempt (direct ID lookup) fails
        responses.add(
            responses.GET,
            f"{self.base_url}/users/{email}",
            status=404
        )
        
        # Second attempt (URL-encoded email) succeeds
        responses.add(
            responses.GET,
            f"{self.base_url}/users/test%40example.com",
            json={"id": user_id, "profile": {"email": email}},
            status=200
        )
        
        result = resolve_user_id(email, self.domain, self.token)
        assert result == user_id
        
    def test_resolve_user_search_exact_match(self):
        """Test user resolution via search query with exact match."""
        email = "test@example.com"
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        # Direct lookups fail
        responses.add(responses.GET, f"{self.base_url}/users/{email}", status=404)
        responses.add(responses.GET, f"{self.base_url}/users/test%40example.com", status=404)
        
        # Search query succeeds
        responses.add(
            responses.GET,
            f"{self.base_url}/users",
            json=[{"id": user_id, "profile": {"email": email, "login": email}}],
            status=200
        )
        
        result = resolve_user_id(email, self.domain, self.token)
        assert result == user_id
        
    def test_resolve_user_search_multiple_exact_matches_ambiguous(self):
        """Test user resolution with multiple exact matches raises AmbiguousIdentifierError."""
        email = "test@example.com"
        user1_id = "00u1a2b3c4d5e6f7g8h9"
        user2_id = "00u2b3c4d5e6f7g8h9i0"
        
        # Direct lookups fail
        responses.add(responses.GET, f"{self.base_url}/users/{email}", status=404)
        responses.add(responses.GET, f"{self.base_url}/users/test%40example.com", status=404)
        
        # Search query returns multiple matches
        responses.add(
            responses.GET,
            f"{self.base_url}/users",
            json=[
                {"id": user1_id, "profile": {"email": email, "login": email}},
                {"id": user2_id, "profile": {"email": email, "login": email}}
            ],
            status=200
        )
        
        with pytest.raises(AmbiguousIdentifierError) as excinfo:
            resolve_user_id(email, self.domain, self.token)
        
        assert "Ambiguous user identifier" in str(excinfo.value)
        assert "found 2 exact matches" in str(excinfo.value)
        
    def test_resolve_user_search_fallback_first_result(self):
        """Test user resolution falls back to first result when no exact matches."""
        identifier = "testuser"
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        # Direct lookups fail
        responses.add(responses.GET, f"{self.base_url}/users/{identifier}", status=404)
        responses.add(responses.GET, f"{self.base_url}/users/{identifier}", status=404)
        
        # Search query returns results but no exact matches
        responses.add(
            responses.GET,
            f"{self.base_url}/users",
            json=[{
                "id": user_id, 
                "profile": {"email": "different@example.com", "login": "different"}
            }],
            status=200
        )
        
        result = resolve_user_id(identifier, self.domain, self.token)
        assert result == user_id
        
    def test_resolve_user_case_insensitive_query_success(self):
        """Test user resolution via case-insensitive query."""
        email = "Test@Example.COM"
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        # Direct lookups fail
        responses.add(responses.GET, f"{self.base_url}/users/{email}", status=404)
        responses.add(responses.GET, f"{self.base_url}/users/Test%40Example.COM", status=404)
        
        # Search query fails
        responses.add(responses.GET, f"{self.base_url}/users", status=200, json=[])
        
        # Case-insensitive query succeeds
        responses.add(
            responses.GET,
            f"{self.base_url}/users",
            json=[{"id": user_id, "profile": {"email": "test@example.com", "login": "test@example.com"}}],
            status=200
        )
        
        result = resolve_user_id(email, self.domain, self.token)
        assert result == user_id
        
    def test_resolve_user_case_insensitive_ambiguous(self):
        """Test case-insensitive query with ambiguous results."""
        email = "Test@Example.COM"
        user1_id = "00u1a2b3c4d5e6f7g8h9"
        user2_id = "00u2b3c4d5e6f7g8h9i0"
        
        # Direct lookups fail
        responses.add(responses.GET, f"{self.base_url}/users/{email}", status=404)
        responses.add(responses.GET, f"{self.base_url}/users/Test%40Example.COM", status=404)
        
        # Search query fails
        responses.add(responses.GET, f"{self.base_url}/users", status=200, json=[])
        
        # Case-insensitive query returns multiple normalized matches
        responses.add(
            responses.GET,
            f"{self.base_url}/users",
            json=[
                {"id": user1_id, "profile": {"email": "test@example.com", "login": "test@example.com"}},
                {"id": user2_id, "profile": {"email": "test@example.com", "login": "test@example.com"}}
            ],
            status=200
        )
        
        with pytest.raises(AmbiguousIdentifierError):
            resolve_user_id(email, self.domain, self.token)
            
    def test_resolve_user_all_methods_fail(self):
        """Test user resolution when all methods fail."""
        email = "nonexistent@example.com"
        
        # All lookups fail
        responses.add(responses.GET, f"{self.base_url}/users/{email}", status=404)
        responses.add(responses.GET, f"{self.base_url}/users/nonexistent%40example.com", status=404)
        responses.add(responses.GET, f"{self.base_url}/users", status=200, json=[])
        responses.add(responses.GET, f"{self.base_url}/users", status=200, json=[])
        
        result = resolve_user_id(email, self.domain, self.token)
        assert result is None
        
    def test_resolve_user_network_exception(self):
        """Test user resolution with network exceptions."""
        email = "test@example.com"
        
        # Simulate network errors
        responses.add(responses.GET, f"{self.base_url}/users/{email}", 
                     body=Exception("Connection error"))
        responses.add(responses.GET, f"{self.base_url}/users/test%40example.com",
                     body=Exception("Connection error"))
        responses.add(responses.GET, f"{self.base_url}/users",
                     body=Exception("Connection error"))
        responses.add(responses.GET, f"{self.base_url}/users",
                     body=Exception("Connection error"))
        
        result = resolve_user_id(email, self.domain, self.token)
        assert result is None
        
    def test_resolve_user_with_logger(self):
        """Test user resolution with logging enabled."""
        logger = logging.getLogger('test_logger')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        with patch.object(logger, 'debug') as mock_debug:
            result = resolve_user_id(user_id, self.domain, self.token, logger=logger)
            assert result == user_id
            assert mock_debug.called
            
    def test_resolve_user_with_debug_print(self):
        """Test user resolution with debug print statements."""
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        with patch('builtins.print') as mock_print:
            result = resolve_user_id(user_id, self.domain, self.token, debug=True)
            assert result == user_id
            assert mock_print.called
            
    def test_resolve_user_logger_from_environment(self):
        """Test logger initialization from environment variable."""
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        with patch.dict(os.environ, {'OKTA_CLI_DEBUG': '1'}):
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                mock_logger.handlers = []
                
                result = resolve_user_id(user_id, self.domain, self.token)
                assert result == user_id
                mock_get_logger.assert_called_with('okta_cli.resolver')


@responses.activate
class TestResolveGroupId:
    """Test cases for resolve_group_id function."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.domain = "test.okta.com"
        self.token = "test-token-123"
        self.base_url = f"https://{self.domain}/api/v1"
        
    def test_resolve_group_already_okta_id(self):
        """Test resolving group when identifier is already an Okta ID."""
        group_id = "00g1a2b3c4d5e6f7g8h9"
        result = resolve_group_id(group_id, self.domain, self.token)
        assert result == group_id
        
    def test_resolve_group_by_name_exact_match(self):
        """Test successful group resolution by exact name match."""
        group_name = "Administrators"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        responses.add(
            responses.GET,
            f"{self.base_url}/groups",
            json=[{"id": group_id, "profile": {"name": group_name}}],
            status=200
        )
        
        result = resolve_group_id(group_name, self.domain, self.token)
        assert result == group_id
        
    def test_resolve_group_by_name_with_spaces(self):
        """Test group resolution with spaces in name."""
        group_name = "My Test Group"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        responses.add(
            responses.GET,
            f"{self.base_url}/groups",
            json=[{"id": group_id, "profile": {"name": group_name}}],
            status=200
        )
        
        result = resolve_group_id(group_name, self.domain, self.token)
        assert result == group_id
        
    def test_resolve_group_mixed_case(self):
        """Test group resolution with mixed case names."""
        search_name = "AdminISTRators"
        actual_name = "Administrators"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        responses.add(
            responses.GET,
            f"{self.base_url}/groups",
            json=[{"id": group_id, "profile": {"name": actual_name}}],
            status=200
        )
        
        result = resolve_group_id(search_name, self.domain, self.token)
        assert result == group_id
        
    def test_resolve_group_special_characters(self):
        """Test group resolution with special characters in name."""
        group_name = "Test-Group_2023 (Active)"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        responses.add(
            responses.GET,
            f"{self.base_url}/groups",
            json=[{"id": group_id, "profile": {"name": group_name}}],
            status=200
        )
        
        result = resolve_group_id(group_name, self.domain, self.token)
        assert result == group_id
        
    def test_resolve_group_fallback_search_success(self):
        """Test group resolution via fallback search."""
        group_name = "TestGroup"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        # Exact search fails
        responses.add(responses.GET, f"{self.base_url}/groups", status=200, json=[])
        
        # Fallback search succeeds
        responses.add(
            responses.GET,
            f"{self.base_url}/groups",
            json=[{"id": group_id, "profile": {"name": group_name}}],
            status=200
        )
        
        result = resolve_group_id(group_name, self.domain, self.token)
        assert result == group_id
        
    def test_resolve_group_fallback_ambiguous_results(self):
        """Test fallback search with ambiguous results."""
        group_name = "TestGroup"
        group1_id = "00g1a2b3c4d5e6f7g8h9"
        group2_id = "00g2b3c4d5e6f7g8h9i0"
        
        # Exact search fails
        responses.add(responses.GET, f"{self.base_url}/groups", status=200, json=[])
        
        # Fallback search returns multiple matches
        responses.add(
            responses.GET,
            f"{self.base_url}/groups",
            json=[
                {"id": group1_id, "profile": {"name": group_name}},
                {"id": group2_id, "profile": {"name": group_name}}
            ],
            status=200
        )
        
        with pytest.raises(AmbiguousIdentifierError) as excinfo:
            resolve_group_id(group_name, self.domain, self.token)
            
        assert "Ambiguous group identifier" in str(excinfo.value)
        assert "found 2 exact matches" in str(excinfo.value)
        
    def test_resolve_group_not_found(self):
        """Test group resolution when group is not found."""
        group_name = "NonexistentGroup"
        
        # Both searches fail
        responses.add(responses.GET, f"{self.base_url}/groups", status=200, json=[])
        responses.add(responses.GET, f"{self.base_url}/groups", status=200, json=[])
        
        result = resolve_group_id(group_name, self.domain, self.token)
        assert result is None
        
    def test_resolve_group_with_raise_on_failure(self):
        """Test group resolution with raise_on_failure=True."""
        group_name = "NonexistentGroup"
        
        # Both searches fail
        responses.add(responses.GET, f"{self.base_url}/groups", status=200, json=[])
        responses.add(responses.GET, f"{self.base_url}/groups", status=200, json=[])
        
        with pytest.raises(ResolutionError) as excinfo:
            resolve_group_id(group_name, self.domain, self.token, raise_on_failure=True)
            
        assert "Unable to resolve group" in str(excinfo.value)
        assert group_name in str(excinfo.value)
        
    def test_resolve_group_network_exception(self):
        """Test group resolution with network exceptions."""
        group_name = "TestGroup"
        
        # Simulate network errors
        responses.add(responses.GET, f"{self.base_url}/groups", 
                     body=Exception("Connection error"))
        responses.add(responses.GET, f"{self.base_url}/groups",
                     body=Exception("Connection error"))
        
        result = resolve_group_id(group_name, self.domain, self.token)
        assert result is None
        
    def test_resolve_group_api_error(self):
        """Test group resolution with API errors."""
        group_name = "TestGroup"
        
        # Simulate API errors
        responses.add(responses.GET, f"{self.base_url}/groups", status=500)
        responses.add(responses.GET, f"{self.base_url}/groups", status=500)
        
        result = resolve_group_id(group_name, self.domain, self.token)
        assert result is None
        
    def test_resolve_group_with_logger(self):
        """Test group resolution with logging enabled."""
        logger = logging.getLogger('test_logger')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        with patch.object(logger, 'debug') as mock_debug:
            result = resolve_group_id(group_id, self.domain, self.token, logger=logger)
            assert result == group_id
            assert mock_debug.called
            
    def test_resolve_group_fallback_no_normalized_match(self):
        """Test fallback search with results but no normalized matches."""
        group_name = "TestGroup"
        
        # Exact search fails
        responses.add(responses.GET, f"{self.base_url}/groups", status=200, json=[])
        
        # Fallback search returns results but no normalized matches
        responses.add(
            responses.GET,
            f"{self.base_url}/groups",
            json=[{"id": "00g123", "profile": {"name": "DifferentGroup"}}],
            status=200
        )
        
        result = resolve_group_id(group_name, self.domain, self.token)
        assert result is None


@responses.activate 
class TestResolveAppId:
    """Test cases for resolve_app_id function."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.domain = "test.okta.com"
        self.token = "test-token-123"
        self.base_url = f"https://{self.domain}/api/v1"
        
    def test_resolve_app_already_okta_id(self):
        """Test resolving app when identifier is already an Okta ID."""
        app_id = "0oa1a2b3c4d5e6f7g8h9"
        result = resolve_app_id(app_id, self.domain, self.token)
        assert result == app_id
        
    def test_resolve_app_by_name(self):
        """Test successful app resolution by name."""
        app_name = "My Application"
        app_id = "0oa1a2b3c4d5e6f7g8h9"
        
        responses.add(
            responses.GET,
            f"{self.base_url}/apps",
            json=[{
                "id": app_id, 
                "name": app_name,
                "label": "My App Label"
            }],
            status=200
        )
        
        result = resolve_app_id(app_name, self.domain, self.token)
        assert result == app_id
        
    def test_resolve_app_by_label(self):
        """Test successful app resolution by label."""
        app_label = "My App Label"
        app_id = "0oa1a2b3c4d5e6f7g8h9"
        
        responses.add(
            responses.GET,
            f"{self.base_url}/apps",
            json=[{
                "id": app_id, 
                "name": "Different Name",
                "label": app_label
            }],
            status=200
        )
        
        result = resolve_app_id(app_label, self.domain, self.token)
        assert result == app_id
        
    def test_resolve_app_not_found(self):
        """Test app resolution when app is not found."""
        app_name = "NonexistentApp"
        
        responses.add(
            responses.GET,
            f"{self.base_url}/apps",
            json=[{"id": "different_id", "name": "Different App"}],
            status=200
        )
        
        result = resolve_app_id(app_name, self.domain, self.token)
        assert result is None
        
    def test_resolve_app_network_exception(self):
        """Test app resolution with network exception."""
        app_name = "TestApp"
        
        responses.add(responses.GET, f"{self.base_url}/apps",
                     body=Exception("Connection error"))
        
        result = resolve_app_id(app_name, self.domain, self.token)
        assert result is None


@responses.activate
class TestGetUserByIdentifier:
    """Test cases for get_user_by_identifier function."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.domain = "test.okta.com"
        self.token = "test-token-123"
        self.base_url = f"https://{self.domain}/api/v1"
        
    def test_get_user_direct_lookup_success(self):
        """Test successful direct user object lookup."""
        user_id = "00u1a2b3c4d5e6f7g8h9"
        user_data = {
            "id": user_id,
            "profile": {"email": "test@example.com", "login": "test@example.com"}
        }
        
        responses.add(
            responses.GET,
            f"{self.base_url}/users/{user_id}",
            json=user_data,
            status=200
        )
        
        result = get_user_by_identifier(user_id, self.domain, self.token)
        assert result == user_data
        
    def test_get_user_search_fallback_success(self):
        """Test user object resolution via search fallback."""
        email = "test@example.com"
        user_id = "00u1a2b3c4d5e6f7g8h9"
        user_data = {
            "id": user_id,
            "profile": {"email": email, "login": email}
        }
        
        # Direct lookup fails
        responses.add(responses.GET, f"{self.base_url}/users/{email}", status=404)
        
        # Search succeeds
        responses.add(
            responses.GET,
            f"{self.base_url}/users",
            json=[user_data],
            status=200
        )
        
        result = get_user_by_identifier(email, self.domain, self.token)
        assert result == user_data
        
    def test_get_user_not_found(self):
        """Test user object resolution when user not found."""
        email = "nonexistent@example.com"
        
        # Direct lookup fails
        responses.add(responses.GET, f"{self.base_url}/users/{email}", status=404)
        
        # Search returns empty
        responses.add(responses.GET, f"{self.base_url}/users", json=[], status=200)
        
        result = get_user_by_identifier(email, self.domain, self.token)
        assert result is None
        
    def test_get_user_with_logger_from_environment(self):
        """Test logger initialization from environment variable."""
        user_id = "00u1a2b3c4d5e6f7g8h9"
        user_data = {"id": user_id, "profile": {"email": "test@example.com"}}
        
        responses.add(
            responses.GET,
            f"{self.base_url}/users/{user_id}",
            json=user_data,
            status=200
        )
        
        with patch.dict(os.environ, {'OKTA_CLI_DEBUG': '1'}):
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                mock_logger.handlers = []
                
                result = get_user_by_identifier(user_id, self.domain, self.token)
                assert result == user_data
                mock_get_logger.assert_called_with('okta_cli.resolver')


@responses.activate
class TestGetGroupByIdentifier:
    """Test cases for get_group_by_identifier function."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.domain = "test.okta.com"
        self.token = "test-token-123"
        self.base_url = f"https://{self.domain}/api/v1"
        
    def test_get_group_direct_lookup_success(self):
        """Test successful direct group object lookup."""
        group_id = "00g1a2b3c4d5e6f7g8h9"
        group_data = {
            "id": group_id,
            "profile": {"name": "Administrators"}
        }
        
        responses.add(
            responses.GET,
            f"{self.base_url}/groups/{group_id}",
            json=group_data,
            status=200
        )
        
        result = get_group_by_identifier(group_id, self.domain, self.token)
        assert result == group_data
        
    def test_get_group_search_by_name_success(self):
        """Test group object resolution via name search."""
        group_name = "Administrators"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        group_data = {
            "id": group_id,
            "profile": {"name": group_name}
        }
        
        responses.add(
            responses.GET,
            f"{self.base_url}/groups",
            json=[group_data],
            status=200
        )
        
        result = get_group_by_identifier(group_name, self.domain, self.token)
        assert result == group_data
        
    def test_get_group_not_found(self):
        """Test group object resolution when group not found."""
        group_name = "NonexistentGroup"
        
        responses.add(responses.GET, f"{self.base_url}/groups", json=[], status=200)
        
        result = get_group_by_identifier(group_name, self.domain, self.token)
        assert result is None


@responses.activate
class TestGetAppByIdentifier:
    """Test cases for get_app_by_identifier function."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.domain = "test.okta.com"
        self.token = "test-token-123"
        self.base_url = f"https://{self.domain}/api/v1"
        
    def test_get_app_direct_lookup_success(self):
        """Test successful direct app object lookup."""
        app_id = "0oa1a2b3c4d5e6f7g8h9"
        app_data = {
            "id": app_id,
            "name": "My Application",
            "label": "My App"
        }
        
        responses.add(
            responses.GET,
            f"{self.base_url}/apps/{app_id}",
            json=app_data,
            status=200
        )
        
        result = get_app_by_identifier(app_id, self.domain, self.token)
        assert result == app_data
        
    def test_get_app_search_by_name_success(self):
        """Test app object resolution via name search."""
        app_name = "My Application"
        app_id = "0oa1a2b3c4d5e6f7g8h9"
        app_data = {
            "id": app_id,
            "name": app_name,
            "label": "My App"
        }
        
        responses.add(
            responses.GET,
            f"{self.base_url}/apps",
            json=[app_data],
            status=200
        )
        
        result = get_app_by_identifier(app_name, self.domain, self.token)
        assert result == app_data
        
    def test_get_app_not_found(self):
        """Test app object resolution when app not found."""
        app_name = "NonexistentApp"
        
        responses.add(responses.GET, f"{self.base_url}/apps", json=[], status=200)
        
        result = get_app_by_identifier(app_name, self.domain, self.token)
        assert result is None


class TestLoggingBehavior:
    """Test cases for logging behavior when disabled/enabled."""
    
    def test_logging_disabled_does_not_break_behavior(self):
        """Test that disabling logging does not break normal behavior."""
        # Test with no logger and no environment variable
        with patch.dict(os.environ, {}, clear=True):
            user_id = "00u1a2b3c4d5e6f7g8h9"
            domain = "test.okta.com"
            token = "test-token"
            
            # Should work without logging
            result = resolve_user_id(user_id, domain, token)
            assert result == user_id
            
    def test_logging_enabled_via_environment_variable(self):
        """Test logging initialization via OKTA_CLI_DEBUG environment variable."""
        with patch.dict(os.environ, {'OKTA_CLI_DEBUG': '1'}):
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_logger.handlers = []
                mock_get_logger.return_value = mock_logger
                
                user_id = "00u1a2b3c4d5e6f7g8h9"
                domain = "test.okta.com"
                token = "test-token"
                
                result = resolve_user_id(user_id, domain, token)
                assert result == user_id
                
                # Verify logger was configured
                mock_get_logger.assert_called_with('okta_cli.resolver')
                mock_logger.addHandler.assert_called_once()
                mock_logger.setLevel.assert_called_with(logging.DEBUG)
                
    def test_logging_with_explicit_logger(self):
        """Test behavior with explicitly provided logger."""
        logger = MagicMock()
        user_id = "00u1a2b3c4d5e6f7g8h9"
        domain = "test.okta.com"
        token = "test-token"
        
        result = resolve_user_id(user_id, domain, token, logger=logger)
        assert result == user_id
        
        # Verify logger was used
        logger.debug.assert_called()
        
    def test_debug_print_behavior(self):
        """Test debug print behavior."""
        user_id = "00u1a2b3c4d5e6f7g8h9"
        domain = "test.okta.com"
        token = "test-token"
        
        with patch('builtins.print') as mock_print:
            result = resolve_user_id(user_id, domain, token, debug=True)
            assert result == user_id
            
            # Verify debug prints were called
            mock_print.assert_called()
            debug_calls = [call for call in mock_print.call_args_list 
                          if '[DEBUG]' in str(call)]
            assert len(debug_calls) > 0


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    @responses.activate
    def test_malformed_json_response(self):
        """Test handling of malformed JSON responses."""
        domain = "test.okta.com"
        token = "test-token"
        user_id = "test-user"
        
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users/{user_id}",
            body="malformed json{",
            status=200
        )
        
        result = resolve_user_id(user_id, domain, token)
        assert result is None
        
    def test_timeout_handling(self):
        """Test timeout handling in requests."""
        domain = "test.okta.com"
        token = "test-token"
        user_id = "test@user.com"  # Use email to avoid Okta ID bypass
        
        # Mock requests.get to raise timeout exceptions
        with patch('requests.get') as mock_get:
            import requests
            mock_get.side_effect = requests.exceptions.ConnectTimeout("Connection timeout")
            
            result = resolve_user_id(user_id, domain, token)
            assert result is None
            
            # Verify that requests.get was called (meaning the code attempted HTTP calls)
            assert mock_get.called
        
    def test_special_characters_in_identifiers(self):
        """Test handling of special characters in identifiers."""
        # Test email with special characters
        assert is_okta_id("user+test@example.com") == False
        
        # Test normalization of special characters  
        assert normalize_string("Test@Example.com") == "test@example.com"
        assert normalize_string("Group (Active)") == "group (active)"
        
    def test_unicode_handling(self):
        """Test Unicode character handling."""
        # Test normalization preserves Unicode correctly
        assert normalize_string("Café") == "café"
        assert normalize_string("naïve résumé") == "naïve résumé"
        
    @responses.activate
    def test_empty_response_arrays(self):
        """Test handling of empty response arrays."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Group"  # Use name with space so it's not considered an Okta ID
        
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[],
            status=200
        )
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups", 
            json=[],
            status=200
        )
        
        result = resolve_group_id(group_name, domain, token)
        assert result is None
        
    @responses.activate
    def test_http_error_codes(self):
        """Test various HTTP error code handling."""
        domain = "test.okta.com" 
        token = "test-token"
        user_id = "test-user"
        
        for status_code in [400, 401, 403, 500, 502, 503]:
            responses.reset()
            responses.add(
                responses.GET,
                f"https://{domain}/api/v1/users/{user_id}",
                status=status_code
            )
            responses.add(
                responses.GET,
                f"https://{domain}/api/v1/users/test-user",
                status=status_code
            )
            responses.add(
                responses.GET,
                f"https://{domain}/api/v1/users",
                status=status_code
            )
            responses.add(
                responses.GET,
                f"https://{domain}/api/v1/users",
                status=status_code
            )
            
            result = resolve_user_id(user_id, domain, token)
            assert result is None


# Additional comprehensive test scenarios for 95%+ coverage

class TestComprehensiveCoverage:
    """Additional test cases to achieve comprehensive coverage."""
    
    def test_resolve_user_id_with_none_handling(self):
        """Test resolve_user_id with None user identifier edge case."""
        domain = "test.okta.com"
        token = "test-token"
        
        # Test with None
        result = resolve_user_id(None, domain, token)
        assert result is None
        
        # Test with empty string
        result = resolve_user_id("", domain, token)
        assert result is None
    
    @responses.activate
    def test_resolve_user_direct_lookup_json_decode_error(self):
        """Test JSON decode error handling in direct lookup."""
        domain = "test.okta.com"
        token = "test-token"
        user_id = "test@example.com"
        
        # Mock malformed JSON response
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users/{user_id}",
            body="{invalid json",
            status=200
        )
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users/test%40example.com",
            body="{invalid json",
            status=200
        )
        
        # Should handle JSON decode error gracefully
        result = resolve_user_id(user_id, domain, token)
        assert result is None
    
    @responses.activate
    def test_resolve_user_search_json_decode_error(self):
        """Test JSON decode error handling in search query."""
        domain = "test.okta.com"
        token = "test-token"
        user_id = "test@example.com"
        
        # Direct lookups fail
        responses.add(responses.GET, f"https://{domain}/api/v1/users/{user_id}", status=404)
        responses.add(responses.GET, f"https://{domain}/api/v1/users/test%40example.com", status=404)
        
        # Search query returns malformed JSON
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users",
            body="{malformed}",
            status=200
        )
        
        result = resolve_user_id(user_id, domain, token)
        assert result is None
    
    @responses.activate
    def test_resolve_group_name_exact_match_multiple_groups(self):
        """Test group resolution when multiple groups found but only one exact match."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Admins"  # Use name with space so it's not considered an Okta ID
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[
                {"id": "other_id", "profile": {"name": "Administrators"}},  # Partial match
                {"id": group_id, "profile": {"name": group_name}},  # Exact match
                {"id": "other_id2", "profile": {"name": "Super Admins"}}  # Partial match
            ],
            status=200
        )
        
        result = resolve_group_id(group_name, domain, token)
        assert result == group_id
    
    @responses.activate
    def test_resolve_group_json_decode_error_exact_search(self):
        """Test JSON decode error in group exact search."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Group"
        
        # Exact search returns malformed JSON
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            body="{invalid",
            status=200
        )
        
        result = resolve_group_id(group_name, domain, token)
        assert result is None
    
    @responses.activate
    def test_resolve_group_json_decode_error_fallback_search(self):
        """Test JSON decode error in group fallback search."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Group"
        
        # Exact search fails
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[],
            status=200
        )
        
        # Fallback search returns malformed JSON
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            body="{malformed",
            status=200
        )
        
        result = resolve_group_id(group_name, domain, token)
        assert result is None
    
    @responses.activate
    def test_get_group_by_identifier_not_okta_id(self):
        """Test get_group_by_identifier with non-Okta ID."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Group"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        group_data = {"id": group_id, "profile": {"name": group_name}}
        
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[group_data],
            status=200
        )
        
        result = get_group_by_identifier(group_name, domain, token)
        assert result == group_data
    
    @responses.activate 
    def test_get_group_by_identifier_exact_name_match(self):
        """Test get_group_by_identifier with exact name matching."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Administrators"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[
                {"id": "other_id", "profile": {"name": "Super Admins"}},
                {"id": group_id, "profile": {"name": group_name}},
                {"id": "other_id2", "profile": {"name": "Temp Administrators"}}
            ],
            status=200
        )
        
        result = get_group_by_identifier(group_name, domain, token)
        assert result["id"] == group_id
    
    def test_resolve_group_id_logger_environment_initialization(self):
        """Test logger initialization from environment in resolve_group_id."""
        group_id = "00g1a2b3c4d5e6f7g8h9"
        domain = "test.okta.com"
        token = "test-token"
        
        with patch.dict(os.environ, {'OKTA_CLI_DEBUG': '1'}):
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_logger.handlers = []
                mock_get_logger.return_value = mock_logger
                
                result = resolve_group_id(group_id, domain, token)
                assert result == group_id
                mock_get_logger.assert_called_with('okta_cli.resolver')
    
    @responses.activate
    def test_resolve_app_json_decode_error(self):
        """Test JSON decode error handling in app resolution."""
        domain = "test.okta.com"
        token = "test-token"
        app_name = "Test App"
        
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/apps",
            body="{malformed json",
            status=200
        )
        
        result = resolve_app_id(app_name, domain, token)
        assert result is None
    
    @responses.activate
    def test_get_app_by_identifier_json_decode_error(self):
        """Test JSON decode error in get_app_by_identifier."""
        domain = "test.okta.com"
        token = "test-token"
        app_name = "Test App"
        
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/apps",
            body="{invalid",
            status=200
        )
        
        result = get_app_by_identifier(app_name, domain, token)
        assert result is None
    
    @responses.activate
    def test_get_user_by_identifier_json_decode_error_search(self):
        """Test JSON decode error in user search fallback."""
        domain = "test.okta.com"
        token = "test-token"
        email = "test@example.com"
        
        # Direct lookup fails
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users/{email}",
            status=404
        )
        
        # Search returns malformed JSON
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users",
            body="{malformed",
            status=200
        )
        
        result = get_user_by_identifier(email, domain, token)
        assert result is None
    
    def test_resolve_user_id_debug_print_detailed(self):
        """Test debug print statements with different scenarios."""
        domain = "test.okta.com"
        token = "test-token"
        
        # Test with empty identifier debug print
        with patch('builtins.print') as mock_print:
            result = resolve_user_id("", domain, token, debug=True)
            assert result is None
            
            # Check that debug print was called with empty identifier message
            debug_calls = [call for call in mock_print.call_args_list 
                          if 'Empty or invalid user identifier' in str(call)]
            assert len(debug_calls) > 0
    
    def test_resolve_group_id_debug_print_detailed(self):
        """Test debug print statements in group resolution."""
        domain = "test.okta.com"
        token = "test-token"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        with patch('builtins.print') as mock_print:
            result = resolve_group_id(group_id, domain, token, debug=True)
            assert result == group_id
            
            # Check that debug print was called
            debug_calls = [call for call in mock_print.call_args_list 
                          if '[DEBUG]' in str(call)]
            assert len(debug_calls) > 0
    
    @responses.activate
    def test_case_insensitive_query_no_results(self):
        """Test case-insensitive query with no results."""
        domain = "test.okta.com"
        token = "test-token"
        email = "NonExistent@Example.COM"
        
        # All lookups fail
        responses.add(responses.GET, f"https://{domain}/api/v1/users/{email}", status=404)
        responses.add(responses.GET, f"https://{domain}/api/v1/users/NonExistent%40Example.COM", status=404)
        responses.add(responses.GET, f"https://{domain}/api/v1/users", json=[], status=200)
        responses.add(responses.GET, f"https://{domain}/api/v1/users", json=[], status=200)
        
        result = resolve_user_id(email, domain, token)
        assert result is None
    
    @responses.activate 
    def test_resolve_user_with_profile_missing_fields(self):
        """Test user resolution with missing profile fields."""
        domain = "test.okta.com"
        token = "test-token"
        email = "test@example.com"
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        # Direct lookups fail
        responses.add(responses.GET, f"https://{domain}/api/v1/users/{email}", status=404)
        responses.add(responses.GET, f"https://{domain}/api/v1/users/test%40example.com", status=404)
        
        # Search returns user with missing profile fields
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users",
            json=[{"id": user_id, "profile": {}}],  # Empty profile
            status=200
        )
        
        result = resolve_user_id(email, domain, token)
        assert result == user_id
    
    def test_resolve_group_with_exception_handling(self):
        """Test that functions properly handle various exceptions."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Group"
        
        # Test with mocked function that simulates KeyError during processing
        with patch('okta_cli.utils.normalize_string') as mock_normalize:
            mock_normalize.side_effect = KeyError("name")
            
            # Should handle KeyError gracefully and return None
            result = resolve_group_id(group_name, domain, token)
            assert result is None
    
    def test_normalize_string_edge_cases(self):
        """Test normalize_string with various edge cases."""
        # Test with only whitespace
        assert normalize_string("\t\n\r ") == ""
        
        # Test with mixed whitespace and content
        assert normalize_string("\t Hello World \n") == "hello world"
        
        # Test with special Unicode characters
        assert normalize_string("ÀÁÂÃÄÅ") == "àáâãäå"
        
        # Test with numbers and symbols
        assert normalize_string("Test123!@#") == "test123!@#"


class TestAdditionalCoverage:
    """Additional test cases for missing coverage areas."""
    
    @responses.activate
    def test_resolve_user_search_success_with_debug_print(self):
        """Test user search with debug prints for first result."""
        domain = "test.okta.com"
        token = "test-token"
        email = "test@example.com"
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        # Direct lookups fail
        responses.add(responses.GET, f"https://{domain}/api/v1/users/{email}", status=404)
        responses.add(responses.GET, f"https://{domain}/api/v1/users/test%40example.com", status=404)
        
        # Search succeeds with multiple results
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users",
            json=[
                {"id": user_id, "profile": {"email": "different@example.com", "login": "different@example.com"}},
                {"id": "user2", "profile": {"email": "another@example.com", "login": "another@example.com"}}
            ],
            status=200
        )
        
        with patch('builtins.print') as mock_print:
            result = resolve_user_id(email, domain, token, debug=True)
            assert result == user_id
            
            # Verify debug prints were made
            assert any("User search found 2 users" in str(call) for call in mock_print.call_args_list)
            assert any(f"First user: different@example.com (ID: {user_id})" in str(call) for call in mock_print.call_args_list)
    
    @responses.activate
    def test_resolve_user_search_failure_with_debug_print(self):
        """Test user search failure with debug print."""
        domain = "test.okta.com"
        token = "test-token"
        email = "test@example.com"
        
        # Direct lookups fail
        responses.add(responses.GET, f"https://{domain}/api/v1/users/{email}", status=404)
        responses.add(responses.GET, f"https://{domain}/api/v1/users/test%40example.com", status=404)
        
        # Search fails with error
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users",
            body="Server Error: Internal error occurred",
            status=500
        )
        
        with patch('builtins.print') as mock_print:
            result = resolve_user_id(email, domain, token, debug=True)
            assert result is None
            
            # Verify debug print for failure
            assert any("User search failed:" in str(call) for call in mock_print.call_args_list)
    
    @responses.activate
    def test_resolve_user_case_insensitive_with_debug(self):
        """Test case-insensitive query with debug prints."""
        domain = "test.okta.com"
        token = "test-token"
        email = "Test@Example.COM"
        user_id = "00u1a2b3c4d5e6f7g8h9"
        
        # Direct lookups fail
        responses.add(responses.GET, f"https://{domain}/api/v1/users/{email}", status=404)
        responses.add(responses.GET, f"https://{domain}/api/v1/users/Test%40Example.COM", status=404)
        
        # Search query fails
        responses.add(responses.GET, f"https://{domain}/api/v1/users", json=[], status=200)
        
        # Case-insensitive query succeeds
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/users",
            json=[{"id": user_id, "profile": {"email": "test@example.com", "login": "test@example.com"}}],
            status=200
        )
        
        with patch('builtins.print') as mock_print:
            result = resolve_user_id(email, domain, token, debug=True)
            assert result == user_id
            
            # Verify debug prints
            assert any(f"User case-insensitive query: GET https://{domain}/api/v1/users with q={email}" in str(call) for call in mock_print.call_args_list)
            assert any("Case-insensitive query found 1 users" in str(call) for call in mock_print.call_args_list)
    
    @responses.activate
    def test_resolve_group_debug_prints_exact_search(self):
        """Test group search with debug prints for exact search."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Admins"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[
                {"id": group_id, "profile": {"name": group_name}}
            ],
            status=200
        )
        
        with patch('builtins.print') as mock_print:
            result = resolve_group_id(group_name, domain, token, debug=True)
            assert result == group_id
            
            # Verify debug prints for group search
            assert any(f"Group search: GET https://{domain}/api/v1/groups" in str(call) for call in mock_print.call_args_list)
            assert any("Group search found 1 groups" in str(call) for call in mock_print.call_args_list)
            assert any(f"Group 0: '{group_name}' (ID: {group_id})" in str(call) for call in mock_print.call_args_list)
            assert any(f"Normalized match found: {group_id}" in str(call) for call in mock_print.call_args_list)
    
    @responses.activate
    def test_resolve_group_debug_prints_fallback_search(self):
        """Test group fallback search with debug prints."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Admins"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        # Exact search fails
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[],
            status=200
        )
        
        # Fallback search succeeds
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[
                {"id": group_id, "profile": {"name": group_name}}
            ],
            status=200
        )
        
        with patch('builtins.print') as mock_print:
            result = resolve_group_id(group_name, domain, token, debug=True)
            assert result == group_id
            
            # Verify debug prints for fallback search
            assert any(f"Group fallback search: GET https://{domain}/api/v1/groups with q={group_name}" in str(call) for call in mock_print.call_args_list)
            assert any("Group fallback search found 1 groups" in str(call) for call in mock_print.call_args_list)
            assert any(f"Fallback normalized match found: {group_id}" in str(call) for call in mock_print.call_args_list)
    
    @responses.activate
    def test_resolve_group_fallback_no_match_debug(self):
        """Test group fallback search with no normalized match and debug."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Admins"
        
        # Exact search fails
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[],
            status=200
        )
        
        # Fallback search returns results but no normalized matches
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[
                {"id": "other_id", "profile": {"name": "Different Group"}}
            ],
            status=200
        )
        
        with patch('builtins.print') as mock_print:
            result = resolve_group_id(group_name, domain, token, debug=True)
            assert result is None
            
            # Verify debug print for no match
            assert any(f"No normalized match found for '{group_name}' in fallback search" in str(call) for call in mock_print.call_args_list)
    
    @responses.activate
    def test_resolve_group_fallback_search_failure_debug(self):
        """Test group fallback search failure with debug print."""
        domain = "test.okta.com"
        token = "test-token"
        group_name = "Test Admins"
        
        # Exact search fails
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            json=[],
            status=200
        )
        
        # Fallback search fails
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups",
            body="Server Error: Internal error occurred",
            status=500
        )
        
        with patch('builtins.print') as mock_print:
            result = resolve_group_id(group_name, domain, token, debug=True)
            assert result is None
            
            # Verify debug print for failure
            assert any("Group fallback search failed:" in str(call) for call in mock_print.call_args_list)
    
    @responses.activate
    def test_get_app_by_identifier_direct_lookup_success(self):
        """Test get_app_by_identifier direct lookup for Okta ID."""
        domain = "test.okta.com"
        token = "test-token"
        app_id = "0oa1a2b3c4d5e6f7g8h9"
        app_data = {
            "id": app_id,
            "name": "My Application",
            "label": "My App"
        }
        
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/apps/{app_id}",
            json=app_data,
            status=200
        )
        
        result = get_app_by_identifier(app_id, domain, token)
        assert result == app_data
    
    @responses.activate
    def test_get_app_by_identifier_direct_lookup_failure(self):
        """Test get_app_by_identifier direct lookup failure for Okta ID."""
        domain = "test.okta.com"
        token = "test-token"
        app_id = "0oa1a2b3c4d5e6f7g8h9"
        
        # Direct lookup fails
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/apps/{app_id}",
            status=404
        )
        
        # Search returns no matching apps
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/apps",
            json=[{"id": "different_id", "name": "Different App", "label": "Different Label"}],
            status=200
        )
        
        result = get_app_by_identifier(app_id, domain, token)
        assert result is None
    
    def test_get_app_by_identifier_exception_handling(self):
        """Test get_app_by_identifier with request exceptions."""
        domain = "test.okta.com"
        token = "test-token"
        app_id = "0oa1a2b3c4d5e6f7g8h9"
        
        # Mock requests.get to raise exceptions
        with patch('requests.get') as mock_get:
            import requests
            mock_get.side_effect = requests.exceptions.RequestException("Network error")
            
            result = get_app_by_identifier(app_id, domain, token)
            assert result is None
    
    def test_get_group_by_identifier_direct_lookup_exception(self):
        """Test get_group_by_identifier with direct lookup exception."""
        domain = "test.okta.com"
        token = "test-token"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        
        # Mock requests.get to raise exceptions
        with patch('requests.get') as mock_get:
            import requests
            mock_get.side_effect = requests.exceptions.RequestException("Network error")
            
            result = get_group_by_identifier(group_id, domain, token)
            assert result is None
    
    @responses.activate
    def test_get_group_by_identifier_search_exception(self):
        """Test get_group_by_identifier with search exception but successful direct lookup."""
        domain = "test.okta.com"
        token = "test-token"
        group_id = "00g1a2b3c4d5e6f7g8h9"
        group_data = {"id": group_id, "profile": {"name": "Administrators"}}
        
        # Direct lookup succeeds
        responses.add(
            responses.GET,
            f"https://{domain}/api/v1/groups/{group_id}",
            json=group_data,
            status=200
        )
        
        result = get_group_by_identifier(group_id, domain, token)
        assert result == group_data
        
    def test_get_user_by_identifier_logger_environment_initialization(self):
        """Test get_user_by_identifier logger initialization from environment."""
        user_id = "00u1a2b3c4d5e6f7g8h9"
        domain = "test.okta.com"
        token = "test-token"
        
        with patch.dict(os.environ, {'OKTA_CLI_DEBUG': '1'}):
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_logger.handlers = []
                mock_get_logger.return_value = mock_logger
                
                # Need to mock requests to avoid actual HTTP calls
                with patch('requests.get') as mock_get:
                    mock_response = MagicMock()
                    mock_response.status_code = 404
                    mock_get.return_value = mock_response
                    
                    result = get_user_by_identifier(user_id, domain, token)
                    assert result is None
                    mock_get_logger.assert_called_with('okta_cli.resolver')


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
