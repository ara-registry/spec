"""Tests for semver utilities."""

import pytest
from ara_cli.utils.semver import parse_version, satisfies_constraint, best_matching_version


class TestParseVersion:
    def test_valid(self):
        v = parse_version("1.2.3")
        assert str(v) == "1.2.3"

    def test_invalid(self):
        with pytest.raises(ValueError):
            parse_version("not-a-version")


class TestSatisfiesConstraint:
    def test_exact(self):
        assert satisfies_constraint("1.0.0", "1.0.0")
        assert not satisfies_constraint("1.0.1", "1.0.0")

    def test_caret(self):
        assert satisfies_constraint("1.2.3", "^1.0.0")
        assert satisfies_constraint("1.9.9", "^1.0.0")
        assert not satisfies_constraint("2.0.0", "^1.0.0")

    def test_caret_zero_major(self):
        assert satisfies_constraint("0.2.0", "^0.2.0")
        assert satisfies_constraint("0.2.5", "^0.2.0")
        assert not satisfies_constraint("0.3.0", "^0.2.0")

    def test_tilde(self):
        assert satisfies_constraint("1.0.5", "~1.0.0")
        assert not satisfies_constraint("1.1.0", "~1.0.0")

    def test_gte(self):
        assert satisfies_constraint("2.0.0", ">=1.0.0")
        assert satisfies_constraint("1.0.0", ">=1.0.0")
        assert not satisfies_constraint("0.9.0", ">=1.0.0")

    def test_wildcard(self):
        assert satisfies_constraint("0.0.1", "*")
        assert satisfies_constraint("99.99.99", "*")


class TestBestMatchingVersion:
    def test_finds_highest(self):
        versions = ["1.0.0", "1.1.0", "1.2.0", "2.0.0"]
        assert best_matching_version(versions, "^1.0.0") == "1.2.0"

    def test_no_match(self):
        versions = ["2.0.0", "3.0.0"]
        assert best_matching_version(versions, "^1.0.0") is None

    def test_wildcard_latest(self):
        versions = ["1.0.0", "2.0.0"]
        assert best_matching_version(versions, "*") == "2.0.0"

    def test_exact_match(self):
        versions = ["1.0.0", "1.1.0"]
        assert best_matching_version(versions, "1.0.0") == "1.0.0"
