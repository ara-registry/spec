"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from ara_cli.models.manifest import ARAManifest, PackageType, PackageSource, SourceType
from ara_cli.models.lockfile import ARALockfile, LockfileEntry
from ara_cli.models.config import CLIConfig


class TestARAManifest:
    def test_valid_manifest(self, valid_manifest_data):
        m = ARAManifest(**valid_manifest_data)
        assert m.name == "acme/test-agent"
        assert m.version == "1.0.0"
        assert m.type == PackageType.KIRO_AGENT

    def test_parse_name(self, valid_manifest_data):
        m = ARAManifest(**valid_manifest_data)
        ns, pkg = m.parse_name()
        assert ns == "acme"
        assert pkg == "test-agent"

    def test_invalid_name(self, valid_manifest_data):
        valid_manifest_data["name"] = "no-slash"
        with pytest.raises(ValidationError):
            ARAManifest(**valid_manifest_data)

    def test_invalid_version(self, valid_manifest_data):
        valid_manifest_data["version"] = "not-semver"
        with pytest.raises(ValidationError):
            ARAManifest(**valid_manifest_data)

    def test_invalid_tag_format(self, valid_manifest_data):
        valid_manifest_data["tags"] = ["valid", "has spaces"]
        with pytest.raises(ValidationError):
            ARAManifest(**valid_manifest_data)

    def test_empty_tags(self, valid_manifest_data):
        valid_manifest_data["tags"] = []
        with pytest.raises(ValidationError):
            ARAManifest(**valid_manifest_data)

    def test_sources_only_mcp_server(self, valid_manifest_data):
        valid_manifest_data["sources"] = [{"type": "npm", "package": "foo"}]
        with pytest.raises(ValidationError, match="sources field is only allowed for mcp-server"):
            ARAManifest(**valid_manifest_data)

    def test_sources_allowed_mcp_server(self, valid_manifest_data):
        valid_manifest_data["type"] = "mcp-server"
        valid_manifest_data["sources"] = [{"type": "npm", "package": "foo"}]
        m = ARAManifest(**valid_manifest_data)
        assert len(m.sources) == 1

    def test_schema_field(self, valid_manifest_data):
        valid_manifest_data["$schema"] = "https://example.com/schema.json"
        m = ARAManifest(**valid_manifest_data)
        assert m.schema_url == "https://example.com/schema.json"

    def test_files_no_traversal(self, valid_manifest_data):
        valid_manifest_data["files"] = ["../etc/passwd"]
        with pytest.raises(ValidationError, match="no absolute paths"):
            ARAManifest(**valid_manifest_data)

    def test_to_file(self, tmp_path, valid_manifest_data):
        m = ARAManifest(**valid_manifest_data)
        path = tmp_path / "ara.json"
        m.to_file(path)
        assert path.exists()
        import json
        with open(path) as f:
            data = json.load(f)
        assert data["name"] == "acme/test-agent"

    def test_prerelease_version(self, valid_manifest_data):
        valid_manifest_data["version"] = "1.0.0-alpha.1"
        m = ARAManifest(**valid_manifest_data)
        assert m.version == "1.0.0-alpha.1"

    def test_dependencies(self, valid_manifest_data):
        valid_manifest_data["dependencies"] = {"acme/utils": "^1.0.0"}
        m = ARAManifest(**valid_manifest_data)
        assert m.dependencies == {"acme/utils": "^1.0.0"}


class TestPackageSource:
    def test_npm_requires_package(self):
        with pytest.raises(ValidationError, match="'package' is required"):
            PackageSource(type=SourceType.NPM)

    def test_git_requires_repository(self):
        with pytest.raises(ValidationError, match="'repository' is required"):
            PackageSource(type=SourceType.GIT)

    def test_valid_npm_source(self):
        s = PackageSource(type=SourceType.NPM, package="@acme/server")
        assert s.package == "@acme/server"

    def test_valid_git_source(self):
        s = PackageSource(type=SourceType.GIT, repository="https://github.com/acme/repo")
        assert s.repository is not None


class TestLockfile:
    def test_lockfile_round_trip(self):
        lf = ARALockfile(
            lockfileVersion=1,
            generatedAt="2025-01-01T00:00:00Z",
            packages={
                "acme/test": LockfileEntry(
                    version="1.0.0",
                    type="kiro-agent",
                    integrity="sha256:abc123",
                    resolved="https://example.com/pkg.tgz",
                )
            },
        )
        data = lf.model_dump(by_alias=True)
        assert data["lockfileVersion"] == 1
        assert "acme/test" in data["packages"]

    def test_lockfile_defaults(self):
        lf = ARALockfile(lockfileVersion=1, generatedAt="2025-01-01T00:00:00Z")
        assert lf.packages == {}


class TestCLIConfig:
    def test_defaults(self):
        c = CLIConfig()
        assert c.registry_url == "http://localhost:3000"
        assert c.auth_token is None

    def test_custom_values(self):
        c = CLIConfig(registry_url="https://ara.dev", auth_token="tok_123")
        assert c.registry_url == "https://ara.dev"
        assert c.auth_token == "tok_123"
