"""ara uninstall <package> — remove a locally installed package."""

import click
from pathlib import Path

from ..core.config_manager import load_config
from ..core.installer import PackageInstaller
from ..core.registry_client import RegistryClient
from ..output.console import print_error, print_success


@click.command("uninstall")
@click.argument("package")
@click.pass_context
def uninstall_cmd(ctx, package: str):
    """Uninstall a package from the local project."""
    if "/" not in package:
        print_error("Package name must be in namespace/name format.")
        raise SystemExit(1)

    namespace, name = package.split("/", 1)
    config = load_config()
    registry = ctx.obj.get("registry") if ctx.obj else None
    client = RegistryClient(registry or config.registry_url, config.auth_token)
    installer = PackageInstaller(Path.cwd(), client)
    installer.uninstall_package(namespace, name)
    print_success(f"Uninstalled {package}")
