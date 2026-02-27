"""Tests for lockfile manager."""

import json
import pytest
from pathlib import Path

from ara_cli.core.lockfile_manager import read_lockfile, write_lockfile, add_package, remove_package
from ara_cli.models.lockfile import ARALockfile, LockfileEntry


class TestReadWriteLockfile:
    def test_read_missing(self, tmp_path):
        result = read_lockfile(tmp_path)
        assert result is None

    def test_write_and_read(self, tmp_path):
        lf = ARALockfile(
            lockfileVersion=1,
            generatedAt="2025-01-01T00:00:00Z",
            packages={
                "acme/test": LockfileEntry(
                    version="1.0.0",
                    type="kiro-agent",
                    integrity="sha256:abc",
                    resolved="https://example.com/p.tgz",
                )
            },
        )
        write_lockfile(tmp_path, lf)
        result = read_lockfile(tmp_path)
        assert result is not None
        assert "acme/test" in result.packages
        assert result.packages["acme/test"].version == "1.0.0"


class TestAddRemovePackage:
    def test_add_to_empty(self, tmp_path):
        entry = LockfileEntry(
            version="2.0.0",
            type="context",
            integrity="sha256:def",
            resolved="https://example.com/pkg.tgz",
        )
        lf = add_package(tmp_path, "acme/new", entry)
        assert "acme/new" in lf.packages

    def test_remove_existing(self, tmp_path):
        entry = LockfileEntry(
            version="1.0.0",
            type="skill",
            integrity="sha256:xyz",
            resolved="https://example.com/pkg.tgz",
        )
        add_package(tmp_path, "acme/removeme", entry)
        lf = remove_package(tmp_path, "acme/removeme")
        assert lf is not None
        assert "acme/removeme" not in lf.packages

    def test_remove_nonexistent(self, tmp_path):
        result = remove_package(tmp_path, "acme/nope")
        assert result is None
