import os
from click.testing import CliRunner
from okta_cli.main import configure
from okta_cli import config

def test_configure():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Override the config file path for testing
        config.CONFIG_FILE = os.path.join(os.getcwd(), "config")

        result = runner.invoke(configure, input="test.okta.com\nmy-api-token-that-is-longer-than-20-chars\n")
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
        assert result.exit_code == 0
        assert "Configuration saved" in result.output

        cfg = config.get_config()
        assert cfg.has_section("default")
        assert cfg.get("default", "domain") == "test.okta.com"
        assert cfg.get("default", "token") == "my-api-token-that-is-longer-than-20-chars"