"""Tests for dependency resolver."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from ara_cli.core.resolver import DependencyResolver, ResolvedPackage
from ara_cli.core.registry_client import RegistryClient
from ara_cli.models.api_responses import VersionListResponse
from ara_cli.utils.errors import ARACyclicDependencyError, ARANotFoundError


def _make_client():
    return RegistryClient("http://localhost:3000")


class TestDependencyResolver:
    def test_resolved_package_dataclass(self):
        rp = ResolvedPackage(name="acme/test", version="1.0.0")
        assert rp.name == "acme/test"
        assert rp.dependencies == {}

    @patch("ara_cli.core.resolver.run_async")
    def test_simple_resolve(self, mock_run_async):
        mock_run_async.side_effect = [
            # list_versions call
            VersionListResponse(namespace="acme", name="utils", versions=["1.0.0", "1.1.0"], latest="1.1.0"),
            # get_manifest call
            {"name": "acme/utils", "version": "1.1.0", "type": "context"},
        ]

        resolver = DependencyResolver(_make_client())
        result = resolver.resolve({"acme/utils": "^1.0.0"})
        assert len(result) == 1
        assert result[0].name == "acme/utils"
        assert result[0].version == "1.1.0"

    @patch("ara_cli.core.resolver.run_async")
    def test_no_matching_version(self, mock_run_async):
        mock_run_async.return_value = VersionListResponse(
            namespace="acme", name="old", versions=["0.1.0"], latest="0.1.0"
        )

        resolver = DependencyResolver(_make_client())
        with pytest.raises(ARANotFoundError, match="No version"):
            resolver.resolve({"acme/old": "^2.0.0"})

    @patch("ara_cli.core.resolver.run_async")
    def test_transitive_deps(self, mock_run_async):
        mock_run_async.side_effect = [
            # First dep: acme/a
            VersionListResponse(namespace="acme", name="a", versions=["1.0.0"], latest="1.0.0"),
            {"name": "acme/a", "version": "1.0.0", "type": "skill", "dependencies": {"acme/b": "^1.0.0"}},
            # Transitive dep: acme/b
            VersionListResponse(namespace="acme", name="b", versions=["1.0.0"], latest="1.0.0"),
            {"name": "acme/b", "version": "1.0.0", "type": "context"},
        ]

        resolver = DependencyResolver(_make_client())
        result = resolver.resolve({"acme/a": "^1.0.0"})
        assert len(result) == 2
        # b should come before a (topological order)
        names = [r.name for r in result]
        assert names.index("acme/b") < names.index("acme/a")
