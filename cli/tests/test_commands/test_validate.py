"""Tests for ara validate command."""

import json
import pytest
from click.testing import CliRunner

from ara_cli.main import main


@pytest.fixture
def runner():
    return CliRunner()


class TestValidateCommand:
    def test_valid_manifest(self, runner, valid_manifest_file):
        result = runner.invoke(main, ["validate", str(valid_manifest_file)])
        assert result.exit_code == 0
        assert "Valid" in result.output

    def test_missing_file(self, runner, tmp_path):
        result = runner.invoke(main, ["validate", str(tmp_path / "nope.json")])
        assert result.exit_code == 1

    def test_invalid_manifest(self, runner, tmp_path):
        bad = tmp_path / "ara.json"
        with open(bad, "w") as f:
            json.dump({"name": "bad"}, f)
        result = runner.invoke(main, ["validate", str(bad)])
        assert result.exit_code == 1
