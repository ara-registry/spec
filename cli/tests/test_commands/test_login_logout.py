"""Tests for ara login/logout commands."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from ara_cli.main import main


@pytest.fixture
def runner():
    return CliRunner()


class TestLoginCommand:
    @patch("ara_cli.commands.login.set_token")
    def test_login_with_token_flag(self, mock_set, runner):
        result = runner.invoke(main, ["login", "--token", "my-token"])
        assert result.exit_code == 0
        assert "Login successful" in result.output
        mock_set.assert_called_once_with("my-token")

    @patch("ara_cli.commands.login.set_token")
    def test_login_prompt(self, mock_set, runner):
        result = runner.invoke(main, ["login"], input="secret-token\n")
        assert result.exit_code == 0
        mock_set.assert_called_once_with("secret-token")


class TestLogoutCommand:
    @patch("ara_cli.commands.logout.clear_token")
    def test_logout(self, mock_clear, runner):
        result = runner.invoke(main, ["logout"])
        assert result.exit_code == 0
        assert "Logged out" in result.output
        mock_clear.assert_called_once()
