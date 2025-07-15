import os
from click.testing import CliRunner
from okta_cli.main import configure
from okta_cli import config

def test_configure():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Override the config file path for testing
        config.CONFIG_FILE = os.path.join(os.getcwd(), "config")

        result = runner.invoke(configure, input="test.okta.com\nmy-api-token\n")
        assert result.exit_code == 0
        assert "Configuration saved" in result.output

        cfg = config.get_config()
        assert cfg.has_section("default")
        assert cfg.get("default", "domain") == "test.okta.com"
        assert cfg.get("default", "token") == "my-api-token"