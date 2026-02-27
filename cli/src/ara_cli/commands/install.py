"""ara install [package[@version]] — install packages."""

import click
from pathlib import Path

from rich.progress import Progress

from ..core.config_manager import load_config
from ..core.installer import PackageInstaller
from ..core.registry_client import RegistryClient, run_async
from ..core.resolver import DependencyResolver
from ..core.validation import read_manifest
from ..output.console import console, print_error, print_success
from ..utils.constants import MANIFEST_NAME
from ..utils.errors import ARAError
from ..utils.semver import best_matching_version


@click.command("install")
@click.argument("package", required=False, default=None)
@click.pass_context
def install_cmd(ctx, package: str | None):
    """Install a package or all dependencies from ara.lock/ara.json."""
    config = load_config()
    registry = ctx.obj.get("registry") if ctx.obj else None
    client = RegistryClient(registry or config.registry_url, config.auth_token)
    project_dir = Path.cwd()
    installer = PackageInstaller(project_dir, client)

    try:
        if package is None:
            _install_all(project_dir, installer, client)
        else:
            _install_one(package, installer, client)
    except ARAError as e:
        print_error(e.message)
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Cannot connect to registry at {registry or config.registry_url}. Is the server running?")
        raise SystemExit(1)


def _install_all(project_dir: Path, installer: PackageInstaller, client: RegistryClient) -> None:
    """Install from lock file, or resolve from ara.json dependencies."""
    from ..core.lockfile_manager import read_lockfile
    lockfile = read_lockfile(project_dir)

    if lockfile and lockfile.packages:
        with Progress(console=console) as progress:
            task = progress.add_task("Installing from lock file...", total=len(lockfile.packages))
            for pkg_name, entry in lockfile.packages.items():
                namespace, name = pkg_name.split("/", 1)
                installer.install_package(namespace, name, entry.version)
                progress.advance(task)
        print_success(f"Installed {len(lockfile.packages)} package(s) from lock file.")
        return

    manifest_path = project_dir / MANIFEST_NAME
    if not manifest_path.exists():
        print_error(f"No {MANIFEST_NAME} or lock file found.")
        raise SystemExit(1)

    manifest = read_manifest(manifest_path)
    if not manifest.dependencies:
        print_success("No dependencies to install.")
        return

    resolver = DependencyResolver(client)
    resolved = resolver.resolve(manifest.dependencies)

    with Progress(console=console) as progress:
        task = progress.add_task("Installing dependencies...", total=len(resolved))
        for pkg in resolved:
            namespace, name = pkg.name.split("/", 1)
            installer.install_package(namespace, name, pkg.version)
            progress.advance(task)

    print_success(f"Installed {len(resolved)} package(s).")


def _install_one(package: str, installer: PackageInstaller, client: RegistryClient) -> None:
    """Install a single package, optionally at a specific version."""
    if "@" in package:
        full_name, version = package.rsplit("@", 1)
    else:
        full_name = package
        version = None

    if "/" not in full_name:
        print_error("Package name must be in namespace/name format.")
        raise SystemExit(1)

    namespace, name = full_name.split("/", 1)

    if version is None:
        versions_resp = run_async(client.list_versions(namespace, name))
        version = versions_resp.latest

    with Progress(console=console) as progress:
        task = progress.add_task(f"Installing {full_name}@{version}...", total=None)
        installer.install_package(namespace, name, version)

    # Also resolve transitive dependencies
    manifest_data = run_async(client.get_manifest(namespace, name, version))
    deps = manifest_data.get("dependencies")
    if deps:
        resolver = DependencyResolver(client)
        resolved = resolver.resolve(deps)
        for pkg in resolved:
            ns, n = pkg.name.split("/", 1)
            installer.install_package(ns, n, pkg.version)
        console.print(f"[dim]+ {len(resolved)} transitive dependency(ies)[/dim]")

    print_success(f"Installed {full_name}@{version}")
