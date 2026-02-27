"""Tests for ara list command."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from ara_cli.main import main


@pytest.fixture
def runner():
    return CliRunner()


class TestListCommand:
    @patch("ara_cli.commands.list_cmd.PackageInstaller")
    @patch("ara_cli.commands.list_cmd.load_config")
    def test_list_empty(self, mock_config, mock_installer_cls, runner):
        from ara_cli.models.config import CLIConfig
        mock_config.return_value = CLIConfig()
        mock_installer = MagicMock()
        mock_installer.get_installed_packages.return_value = {}
        mock_installer_cls.return_value = mock_installer
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "No packages installed" in result.output

    @patch("ara_cli.commands.list_cmd.PackageInstaller")
    @patch("ara_cli.commands.list_cmd.load_config")
    def test_list_with_packages(self, mock_config, mock_installer_cls, runner):
        from ara_cli.models.config import CLIConfig
        mock_config.return_value = CLIConfig()
        mock_installer = MagicMock()
        mock_installer.get_installed_packages.return_value = {"acme/agent": "1.0.0"}
        mock_installer_cls.return_value = mock_installer
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "acme/agent" in result.output
