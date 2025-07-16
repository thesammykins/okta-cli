"""
Tests for Phase 5 features: Applications, Sessions, Policies, Authorization, Logs, and Factors.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from okta_cli.applications import applications
from okta_cli.sessions import sessions
from okta_cli.policies import policies
from okta_cli.authorization import authorization
from okta_cli.logs import logs
from okta_cli.factors import factors


class TestApplicationsCommands:
    """Test application management commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = []

    @patch("okta_cli.applications.requests.get")
    @patch("okta_cli.applications.get_effective_config")
    def test_list_applications_success(self, mock_config, mock_get):
        """Test successful application listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(applications, ["list"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.applications.requests.get")
    @patch("okta_cli.applications.get_effective_config")
    def test_show_application_success(self, mock_config, mock_get):
        """Test successful application show."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(applications, ["show", "app123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.applications.requests.post")
    @patch("okta_cli.applications.get_effective_config")
    def test_create_application_success(self, mock_config, mock_post):
        """Test successful application creation."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_post.return_value = self.mock_response

        result = self.runner.invoke(
            applications,
            [
                "create",
                "--name",
                "TestApp",
                "--label",
                "Test Application",
                "--sign-on-mode",
                "BOOKMARK",
            ],
        )

        assert result.exit_code == 0
        mock_post.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.applications.requests.put")
    @patch("okta_cli.applications.get_effective_config")
    def test_update_application_success(self, mock_config, mock_put):
        """Test successful application update."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_put.return_value = self.mock_response

        result = self.runner.invoke(
            applications, ["update", "app123", "--name", "UpdatedApp"]
        )

        assert result.exit_code == 0
        mock_put.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.applications.requests.delete")
    @patch("okta_cli.applications.get_effective_config")
    def test_delete_application_success(self, mock_config, mock_delete):
        """Test successful application deletion."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_delete.return_value = Mock(status_code=204)

        result = self.runner.invoke(applications, ["delete", "app123", "--force"])

        assert result.exit_code == 0
        mock_delete.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.applications.requests.post")
    @patch("okta_cli.applications.get_effective_config")
    def test_activate_application_success(self, mock_config, mock_post):
        """Test successful application activation."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_post.return_value = self.mock_response

        result = self.runner.invoke(applications, ["activate", "app123"])

        assert result.exit_code == 0
        mock_post.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.applications.requests.get")
    @patch("okta_cli.applications.get_effective_config")
    def test_list_app_users_success(self, mock_config, mock_get):
        """Test successful application users listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(applications, ["list-users", "app123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()


class TestSessionsCommands:
    """Test session management commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = []

    @patch("okta_cli.sessions.requests.get")
    @patch("okta_cli.sessions.get_effective_config")
    def test_list_sessions_success(self, mock_config, mock_get):
        """Test successful session listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(sessions, ["list", "user123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.sessions.requests.get")
    @patch("okta_cli.sessions.get_effective_config")
    def test_show_session_success(self, mock_config, mock_get):
        """Test successful session show."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(sessions, ["show", "user123", "session456"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.sessions.requests.delete")
    @patch("okta_cli.sessions.get_effective_config")
    def test_clear_sessions_success(self, mock_config, mock_delete):
        """Test successful session clearing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_delete.return_value = Mock(status_code=204)

        result = self.runner.invoke(sessions, ["clear", "user123", "--force"])

        assert result.exit_code == 0
        mock_delete.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.sessions.requests.put")
    @patch("okta_cli.sessions.get_effective_config")
    def test_extend_session_success(self, mock_config, mock_put):
        """Test successful session extension."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_put.return_value = self.mock_response

        result = self.runner.invoke(sessions, ["extend", "user123", "session456"])

        assert result.exit_code == 0
        mock_put.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.sessions.requests.get")
    @patch("okta_cli.sessions.get_effective_config")
    def test_session_stats_success(self, mock_config, mock_get):
        """Test successful session statistics."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(sessions, ["stats"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()


class TestPoliciesCommands:
    """Test policies and group rules management commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = []

    @patch("okta_cli.policies.requests.get")
    @patch("okta_cli.policies.get_effective_config")
    def test_list_policies_success(self, mock_config, mock_get):
        """Test successful policy listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(policies, ["list"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.policies.requests.get")
    @patch("okta_cli.policies.get_effective_config")
    def test_show_policy_success(self, mock_config, mock_get):
        """Test successful policy show."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(policies, ["show", "policy123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.policies.requests.post")
    @patch("okta_cli.policies.get_effective_config")
    def test_activate_policy_success(self, mock_config, mock_post):
        """Test successful policy activation."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_post.return_value = self.mock_response

        result = self.runner.invoke(policies, ["activate", "policy123"])

        assert result.exit_code == 0
        mock_post.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.policies.requests.get")
    @patch("okta_cli.policies.get_effective_config")
    def test_list_group_rules_success(self, mock_config, mock_get):
        """Test successful group rules listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(policies, ["rules", "list"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.policies.requests.get")
    @patch("okta_cli.policies.get_effective_config")
    def test_show_group_rule_success(self, mock_config, mock_get):
        """Test successful group rule show."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(policies, ["rules", "show", "rule123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.policies.requests.post")
    @patch("okta_cli.policies.get_effective_config")
    def test_create_group_rule_success(self, mock_config, mock_post):
        """Test successful group rule creation."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_post.return_value = self.mock_response

        result = self.runner.invoke(
            policies,
            [
                "rules",
                "create",
                "--name",
                "TestRule",
                "--expression",
                'user.department=="Engineering"',
                "--group-id",
                "group123",
            ],
        )

        assert result.exit_code == 0
        mock_post.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.policies.requests.delete")
    @patch("okta_cli.policies.get_effective_config")
    def test_delete_group_rule_success(self, mock_config, mock_delete):
        """Test successful group rule deletion."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_delete.return_value = Mock(status_code=202)

        result = self.runner.invoke(policies, ["rules", "delete", "rule123", "--force"])

        assert result.exit_code == 0
        mock_delete.assert_called_once()
        mock_config.assert_called_once()


class TestAuthorizationCommands:
    """Test authorization server management commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = []

    @patch("okta_cli.authorization.requests.get")
    @patch("okta_cli.authorization.get_effective_config")
    def test_list_authorization_servers_success(self, mock_config, mock_get):
        """Test successful authorization server listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(authorization, ["list"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.authorization.requests.get")
    @patch("okta_cli.authorization.get_effective_config")
    def test_show_authorization_server_success(self, mock_config, mock_get):
        """Test successful authorization server show."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(authorization, ["show", "server123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.authorization.requests.post")
    @patch("okta_cli.authorization.get_effective_config")
    def test_create_authorization_server_success(self, mock_config, mock_post):
        """Test successful authorization server creation."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_post.return_value = Mock(status_code=201, json=lambda: {})

        result = self.runner.invoke(
            authorization,
            ["create", "--name", "TestServer", "--audience", "api://test"],
        )

        assert result.exit_code == 0
        mock_post.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.authorization.requests.delete")
    @patch("okta_cli.authorization.get_effective_config")
    def test_delete_authorization_server_success(self, mock_config, mock_delete):
        """Test successful authorization server deletion."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_delete.return_value = Mock(status_code=204)

        result = self.runner.invoke(authorization, ["delete", "server123", "--force"])

        assert result.exit_code == 0
        mock_delete.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.authorization.requests.get")
    @patch("okta_cli.authorization.get_effective_config")
    def test_list_scopes_success(self, mock_config, mock_get):
        """Test successful scope listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(authorization, ["scopes", "list", "server123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.authorization.requests.post")
    @patch("okta_cli.authorization.get_effective_config")
    def test_create_scope_success(self, mock_config, mock_post):
        """Test successful scope creation."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_post.return_value = Mock(status_code=201, json=lambda: {})

        result = self.runner.invoke(
            authorization,
            [
                "scopes",
                "create",
                "server123",
                "--name",
                "read:users",
                "--description",
                "Read user data",
            ],
        )

        assert result.exit_code == 0
        mock_post.assert_called_once()
        mock_config.assert_called_once()


class TestLogsCommands:
    """Test event log querying commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = []

    @patch("okta_cli.logs.requests.get")
    @patch("okta_cli.logs.get_effective_config")
    def test_list_logs_success(self, mock_config, mock_get):
        """Test successful log listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(logs, ["list"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.logs.requests.get")
    @patch("okta_cli.logs.get_effective_config")
    def test_show_log_success(self, mock_config, mock_get):
        """Test successful log show."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(logs, ["show", "log123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.logs.requests.get")
    @patch("okta_cli.logs.get_effective_config")
    def test_search_logs_success(self, mock_config, mock_get):
        """Test successful log search."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(
            logs, ["search", "--event-type", "user.session.start"]
        )

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.logs.requests.get")
    @patch("okta_cli.logs.get_effective_config")
    def test_log_stats_success(self, mock_config, mock_get):
        """Test successful log statistics."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(logs, ["stats"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.logs.requests.get")
    @patch("okta_cli.logs.get_effective_config")
    def test_failed_logins_success(self, mock_config, mock_get):
        """Test successful failed login retrieval."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(logs, ["failed-logins"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.logs.requests.get")
    @patch("okta_cli.logs.get_effective_config")
    def test_suspicious_activities_success(self, mock_config, mock_get):
        """Test successful suspicious activities retrieval."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(logs, ["suspicious"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()


class TestFactorsCommands:
    """Test MFA factor management commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = []

    @patch("okta_cli.factors.requests.get")
    @patch("okta_cli.factors.get_effective_config")
    def test_list_factors_success(self, mock_config, mock_get):
        """Test successful factor listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(factors, ["list", "user123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.factors.requests.get")
    @patch("okta_cli.factors.get_effective_config")
    def test_show_factor_success(self, mock_config, mock_get):
        """Test successful factor show."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(factors, ["show", "user123", "factor456"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.factors.requests.post")
    @patch("okta_cli.factors.get_effective_config")
    def test_enroll_factor_success(self, mock_config, mock_post):
        """Test successful factor enrollment."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_post.return_value = self.mock_response

        result = self.runner.invoke(
            factors,
            [
                "enroll",
                "user123",
                "--factor-type",
                "sms",
                "--phone-number",
                "+1234567890",
            ],
        )

        assert result.exit_code == 0
        mock_post.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.factors.requests.post")
    @patch("okta_cli.factors.get_effective_config")
    def test_activate_factor_success(self, mock_config, mock_post):
        """Test successful factor activation."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_post.return_value = self.mock_response

        result = self.runner.invoke(
            factors, ["activate", "user123", "factor456", "--passcode", "123456"]
        )

        assert result.exit_code == 0
        mock_post.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.factors.requests.delete")
    @patch("okta_cli.factors.get_effective_config")
    def test_reset_factor_success(self, mock_config, mock_delete):
        """Test successful factor reset."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_delete.return_value = Mock(status_code=204)

        result = self.runner.invoke(
            factors, ["reset", "user123", "factor456", "--force"]
        )

        assert result.exit_code == 0
        mock_delete.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.factors.requests.post")
    @patch("okta_cli.factors.get_effective_config")
    def test_verify_factor_success(self, mock_config, mock_post):
        """Test successful factor verification."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_post.return_value.json.return_value = {"factorResult": "SUCCESS"}

        result = self.runner.invoke(
            factors, ["verify", "user123", "factor456", "--passcode", "123456"]
        )

        assert result.exit_code == 0
        mock_post.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.factors.requests.get")
    @patch("okta_cli.factors.get_effective_config")
    def test_list_catalog_success(self, mock_config, mock_get):
        """Test successful factor catalog listing."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = self.mock_response

        result = self.runner.invoke(factors, ["catalog", "list", "user123"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.factors.requests.get")
    @patch("okta_cli.factors.get_effective_config")
    def test_factor_stats_success(self, mock_config, mock_get):
        """Test successful factor statistics."""
        mock_config.return_value = ("test.okta.com", "test-token")
        # Mock multiple responses for users and factors
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: [{"id": "user1"}, {"id": "user2"}]),
            Mock(status_code=200, json=lambda: [{"factorType": "sms"}]),
            Mock(status_code=200, json=lambda: []),
        ]

        result = self.runner.invoke(factors, ["stats"])

        assert result.exit_code == 0
        assert mock_get.call_count >= 1
        mock_config.assert_called()


class TestIntegrationScenarios:
    """Test integration scenarios across Phase 5 features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("okta_cli.applications.requests.get")
    @patch("okta_cli.applications.get_effective_config")
    def test_application_and_user_assignment_workflow(self, mock_config, mock_get):
        """Test workflow of listing applications and their users."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = Mock(status_code=200, json=lambda: [])

        # List applications
        result1 = self.runner.invoke(applications, ["list"])
        assert result1.exit_code == 0

        # List users for an app
        result2 = self.runner.invoke(applications, ["list-users", "app123"])
        assert result2.exit_code == 0

        assert mock_get.call_count == 2
        mock_config.assert_called()

    @patch("okta_cli.sessions.requests.get")
    @patch("okta_cli.sessions.get_effective_config")
    def test_session_management_workflow(self, mock_config, mock_get):
        """Test workflow of session management operations."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = Mock(status_code=200, json=lambda: [])

        # List sessions
        result1 = self.runner.invoke(sessions, ["list", "user123"])
        assert result1.exit_code == 0

        # Show session
        result2 = self.runner.invoke(sessions, ["show", "user123", "session456"])
        assert result2.exit_code == 0

        assert mock_get.call_count == 2
        mock_config.assert_called()

    @patch("okta_cli.logs.requests.get")
    @patch("okta_cli.logs.get_effective_config")
    def test_security_monitoring_workflow(self, mock_config, mock_get):
        """Test workflow of security monitoring operations."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = Mock(status_code=200, json=lambda: [])

        # Get failed logins
        result1 = self.runner.invoke(logs, ["failed-logins"])
        assert result1.exit_code == 0

        # Get suspicious activities
        result2 = self.runner.invoke(logs, ["suspicious"])
        assert result2.exit_code == 0

        # Get log stats
        result3 = self.runner.invoke(logs, ["stats"])
        assert result3.exit_code == 0

        assert mock_get.call_count == 3
        mock_config.assert_called()

    @patch("okta_cli.factors.requests.get")
    @patch("okta_cli.factors.get_effective_config")
    def test_mfa_management_workflow(self, mock_config, mock_get):
        """Test workflow of MFA management operations."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = Mock(status_code=200, json=lambda: [])

        # List factors
        result1 = self.runner.invoke(factors, ["list", "user123"])
        assert result1.exit_code == 0

        # List catalog
        result2 = self.runner.invoke(factors, ["catalog", "list", "user123"])
        assert result2.exit_code == 0

        assert mock_get.call_count == 2
        mock_config.assert_called()


class TestErrorHandling:
    """Test error handling in Phase 5 features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("okta_cli.applications.requests.get")
    @patch("okta_cli.applications.get_effective_config")
    def test_application_api_error_handling(self, mock_config, mock_get):
        """Test API error handling in applications."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = Mock(status_code=404, text="Not Found")

        with patch("okta_cli.applications.handle_api_error") as mock_handle:
            result = self.runner.invoke(applications, ["show", "nonexistent"])
            mock_handle.assert_called_once()

    @patch("okta_cli.sessions.requests.get")
    @patch("okta_cli.sessions.get_effective_config")
    def test_session_network_error_handling(self, mock_config, mock_get):
        """Test network error handling in sessions."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.side_effect = Exception("Network error")

        with patch("okta_cli.sessions.handle_network_error") as mock_handle:
            result = self.runner.invoke(sessions, ["list", "user123"])
            mock_handle.assert_called_once()

    @patch("okta_cli.factors.get_effective_config")
    def test_factor_config_error_handling(self, mock_config):
        """Test configuration error handling in factors."""
        mock_config.side_effect = Exception("Config error")

        with patch("okta_cli.factors.config.get_config") as mock_get_config:
            mock_get_config.side_effect = Exception("Config error")
            with patch("okta_cli.factors.handle_corrupted_config") as mock_handle:
                result = self.runner.invoke(factors, ["list", "user123"])
                mock_handle.assert_called_once()


class TestOutputFormatting:
    """Test output formatting in Phase 5 features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("okta_cli.applications.requests.get")
    @patch("okta_cli.applications.get_effective_config")
    def test_application_json_output(self, mock_config, mock_get):
        """Test JSON output format for applications."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = Mock(
            status_code=200, json=lambda: [{"id": "app1", "name": "TestApp"}]
        )

        result = self.runner.invoke(applications, ["list", "--output", "json"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.logs.requests.get")
    @patch("okta_cli.logs.get_effective_config")
    def test_logs_table_output(self, mock_config, mock_get):
        """Test table output format for logs."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = Mock(status_code=200, json=lambda: [])

        result = self.runner.invoke(logs, ["list", "--output", "table"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()

    @patch("okta_cli.factors.requests.get")
    @patch("okta_cli.factors.get_effective_config")
    def test_factors_csv_output(self, mock_config, mock_get):
        """Test CSV output format for factors."""
        mock_config.return_value = ("test.okta.com", "test-token")
        mock_get.return_value = Mock(status_code=200, json=lambda: [])

        result = self.runner.invoke(factors, ["list", "user123", "--output", "csv"])

        assert result.exit_code == 0
        mock_get.assert_called_once()
        mock_config.assert_called_once()
