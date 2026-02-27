"""Tests for ara init command."""

import json
import pytest
from click.testing import CliRunner

from ara_cli.main import main


@pytest.fixture
def runner():
    return CliRunner()


class TestInitCommand:
    def test_init_creates_file(self, runner, tmp_path):
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ["init"], input="acme/my-agent\n1.0.0\nA test agent\ntest@x.com\nai,test\nkiro-agent\nMIT\n")
            assert result.exit_code == 0
            assert "Created ara.json" in result.output
            with open("ara.json") as f:
                data = json.load(f)
            assert data["name"] == "acme/my-agent"
            assert data["version"] == "1.0.0"
            assert data["tags"] == ["ai", "test"]
