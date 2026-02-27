"""ara update [package] — update packages to latest compatible versions."""

import click
from pathlib import Path

from ..core.config_manager import load_config
from ..core.installer import PackageInstaller
from ..core.lockfile_manager import read_lockfile
from ..core.registry_client import RegistryClient, run_async
from ..core.validation import read_manifest
from ..output.console import console, print_error, print_success
from ..utils.constants import MANIFEST_NAME
from ..utils.errors import ARAError
from ..utils.semver import best_matching_version


@click.command("update")
@click.argument("package", required=False, default=None)
@click.pass_context
def update_cmd(ctx, package: str | None):
    """Update packages to latest compatible versions."""
    config = load_config()
    registry = ctx.obj.get("registry") if ctx.obj else None
    client = RegistryClient(registry or config.registry_url, config.auth_token)
    project_dir = Path.cwd()
    installer = PackageInstaller(project_dir, client)

    manifest_path = project_dir / MANIFEST_NAME
    if not manifest_path.exists():
        print_error(f"No {MANIFEST_NAME} found in current directory.")
        raise SystemExit(1)

    manifest = read_manifest(manifest_path)
    deps = manifest.dependencies or {}

    if package:
        if package not in deps:
            print_error(f"'{package}' is not in dependencies.")
            raise SystemExit(1)
        deps = {package: deps[package]}

    try:
        updated = 0
        for name, constraint in deps.items():
            namespace, pkg_name = name.split("/", 1)
            versions_resp = run_async(client.list_versions(namespace, pkg_name))
            best = best_matching_version(versions_resp.versions, constraint)

            if best is None:
                console.print(f"[warning]No compatible version for {name}[/warning]")
                continue

            installed = installer.get_installed_packages()
            current = installed.get(name)

            if current == best:
                console.print(f"[dim]{name} already at {best}[/dim]")
                continue

            # Uninstall old, install new
            if current:
                installer.uninstall_package(namespace, pkg_name)
            installer.install_package(namespace, pkg_name, best)
            console.print(f"  [success]Updated {name}: {current or '(new)'} → {best}[/success]")
            updated += 1

        if updated:
            print_success(f"Updated {updated} package(s).")
        else:
            print_success("All packages are up to date.")
    except ARAError as e:
        print_error(e.message)
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Cannot connect to registry at {registry or config.registry_url}. Is the server running?")
        raise SystemExit(1)
