"""Dependency resolution with cycle detection."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..utils.errors import ARACyclicDependencyError, ARANotFoundError
from ..utils.semver import best_matching_version
from .registry_client import RegistryClient, run_async


@dataclass
class ResolvedPackage:
    name: str
    version: str
    dependencies: dict[str, str] = field(default_factory=dict)
    package_type: str = "kiro-agent"


class DependencyResolver:
    """Resolves a dependency tree from the registry, detecting cycles."""

    def __init__(self, client: RegistryClient):
        self.client = client
        self._resolved: dict[str, ResolvedPackage] = {}
        self._in_progress: set[str] = set()

    def resolve(self, dependencies: dict[str, str]) -> list[ResolvedPackage]:
        """Resolve all dependencies recursively. Returns topologically sorted list."""
        for name, constraint in dependencies.items():
            self._resolve_one(name, constraint, [])
        return self._topological_sort()

    def _resolve_one(self, name: str, constraint: str, path: list[str]) -> None:
        if name in self._resolved:
            return

        if name in self._in_progress:
            cycle = path[path.index(name):] + [name]
            raise ARACyclicDependencyError(
                f"Cyclic dependency detected: {' -> '.join(cycle)}",
                cycle=cycle,
            )

        self._in_progress.add(name)
        current_path = path + [name]

        namespace, pkg_name = name.split("/", 1)

        # Fetch available versions
        versions_resp = run_async(self.client.list_versions(namespace, pkg_name))
        version = best_matching_version(versions_resp.versions, constraint)
        if version is None:
            raise ARANotFoundError(
                f"No version of '{name}' satisfies constraint '{constraint}'"
            )

        # Fetch manifest for resolved version
        manifest_data = run_async(self.client.get_manifest(namespace, pkg_name, version))
        deps = manifest_data.get("dependencies") or {}
        pkg_type = manifest_data.get("type", "kiro-agent")

        resolved = ResolvedPackage(
            name=name,
            version=version,
            dependencies=deps,
            package_type=pkg_type,
        )
        self._resolved[name] = resolved
        self._in_progress.discard(name)

        # Recurse into transitive deps
        for dep_name, dep_constraint in deps.items():
            self._resolve_one(dep_name, dep_constraint, current_path)

    def _topological_sort(self) -> list[ResolvedPackage]:
        """Topological sort so dependencies come before dependents."""
        visited: set[str] = set()
        order: list[ResolvedPackage] = []

        def visit(name: str) -> None:
            if name in visited or name not in self._resolved:
                return
            visited.add(name)
            for dep_name in self._resolved[name].dependencies:
                visit(dep_name)
            order.append(self._resolved[name])

        for name in self._resolved:
            visit(name)

        return order
