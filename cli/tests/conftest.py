"""Shared test fixtures."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def valid_manifest_data():
    return {
        "name": "acme/test-agent",
        "version": "1.0.0",
        "description": "A test agent",
        "author": "test@example.com",
        "tags": ["test", "agent"],
        "type": "kiro-agent",
    }


@pytest.fixture
def valid_manifest_file(tmp_path, valid_manifest_data):
    path = tmp_path / "ara.json"
    with open(path, "w") as f:
        json.dump(valid_manifest_data, f)
    return path


@pytest.fixture
def project_dir(tmp_path, valid_manifest_data):
    """A temporary project directory with ara.json."""
    manifest_path = tmp_path / "ara.json"
    with open(manifest_path, "w") as f:
        json.dump(valid_manifest_data, f)
    return tmp_path
