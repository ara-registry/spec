"""Tests for validation module."""

import json
import pytest
from pathlib import Path

from ara_cli.core.validation import validate, read_manifest, validate_files_field, validate_dependencies


class TestValidate:
    def test_valid_file(self, valid_manifest_file):
        errors = validate(valid_manifest_file)
        assert errors == []

    def test_missing_file(self, tmp_path):
        errors = validate(tmp_path / "nonexistent.json")
        assert len(errors) == 1
        assert "File not found" in errors[0]

    def test_invalid_json(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{bad json")
        errors = validate(path)
        assert len(errors) == 1
        assert "Invalid JSON" in errors[0]

    def test_missing_required_fields(self, tmp_path):
        path = tmp_path / "ara.json"
        with open(path, "w") as f:
            json.dump({"name": "a/b"}, f)
        errors = validate(path)
        assert len(errors) > 0


class TestReadManifest:
    def test_read_valid(self, valid_manifest_file):
        m = read_manifest(valid_manifest_file)
        assert m.name == "acme/test-agent"

    def test_read_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_manifest(tmp_path / "nope.json")


class TestValidateFilesField:
    def test_all_exist(self, tmp_path):
        (tmp_path / "a.txt").touch()
        (tmp_path / "b.txt").touch()
        errors = validate_files_field(["a.txt", "b.txt"], tmp_path)
        assert errors == []

    def test_missing_file(self, tmp_path):
        errors = validate_files_field(["missing.txt"], tmp_path)
        assert len(errors) == 1


class TestValidateDependencies:
    def test_valid_deps(self):
        errors = validate_dependencies({"acme/utils": "^1.0.0", "acme/tools": ">=2.0.0"})
        assert errors == []

    def test_invalid_dep_name(self):
        errors = validate_dependencies({"bad_name": "^1.0.0"})
        assert len(errors) == 1
        assert "Invalid dependency name" in errors[0]

    def test_wildcard(self):
        errors = validate_dependencies({"acme/thing": "*"})
        assert errors == []
