"""Tests for ara config command."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from ara_cli.main import main
from ara_cli.models.config import CLIConfig


@pytest.fixture
def runner():
    return CliRunner()


class TestConfigCommand:
    @patch("ara_cli.commands.config.load_config")
    @patch("ara_cli.commands.config.save_config")
    def test_set_registry_url(self, mock_save, mock_load, runner):
        mock_load.return_value = CLIConfig()
        result = runner.invoke(main, ["config", "set", "registry_url", "https://ara.dev"])
        assert result.exit_code == 0
        assert "Set registry_url" in result.output

    @patch("ara_cli.commands.config.load_config")
    def test_get_registry_url(self, mock_load, runner):
        mock_load.return_value = CLIConfig(registry_url="https://ara.dev")
        result = runner.invoke(main, ["config", "get", "registry_url"])
        assert result.exit_code == 0
        assert "https://ara.dev" in result.output

    def test_set_unknown_key(self, runner):
        result = runner.invoke(main, ["config", "set", "unknown_key", "value"])
        assert result.exit_code == 1
