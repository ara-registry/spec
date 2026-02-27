"""Tests for security module."""

import pytest
from pathlib import Path

from ara_cli.core.security import compute_sha256, verify_checksum, validate_git_url
from ara_cli.utils.errors import ARAChecksumError


class TestComputeSha256:
    def test_compute(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        result = compute_sha256(f)
        assert result.startswith("sha256:")
        assert len(result) > 10

    def test_deterministic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("same content")
        h1 = compute_sha256(f)
        h2 = compute_sha256(f)
        assert h1 == h2


class TestVerifyChecksum:
    def test_valid(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("verify me")
        expected = compute_sha256(f)
        verify_checksum(f, expected)  # Should not raise

    def test_mismatch(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        with pytest.raises(ARAChecksumError):
            verify_checksum(f, "sha256:wrong")


class TestValidateGitUrl:
    def test_valid_https(self):
        errors = validate_git_url("https://github.com/acme/repo")
        assert errors == []

    def test_not_https(self):
        errors = validate_git_url("http://github.com/acme/repo")
        assert any("HTTPS" in e for e in errors)

    def test_embedded_credentials(self):
        errors = validate_git_url("https://user:pass@github.com/acme/repo")
        assert any("credentials" in e for e in errors)

    def test_path_traversal(self):
        errors = validate_git_url("https://github.com/acme/../evil/repo")
        assert any("traversal" in e for e in errors)

    def test_untrusted_domain(self):
        errors = validate_git_url("https://evil.com/repo", trusted_domains=["github.com"])
        assert any("trusted" in e for e in errors)

    def test_trusted_domain(self):
        errors = validate_git_url("https://github.com/repo", trusted_domains=["github.com"])
        assert errors == []
