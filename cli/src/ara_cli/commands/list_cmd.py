"""ara list — show locally installed packages."""

import click
from pathlib import Path

from ..core.installer import PackageInstaller
from ..core.config_manager import load_config
from ..core.registry_client import RegistryClient
from ..output.console import console
from ..output.tables import render_installed_packages


@click.command("list")
@click.option("--json-output", "use_json", is_flag=True, help="Output raw JSON.")
@click.pass_context
def list_cmd(ctx, use_json: bool):
    """List locally installed packages."""
    config = load_config()
    registry = ctx.obj.get("registry") if ctx.obj else None
    client = RegistryClient(registry or config.registry_url, config.auth_token)
    installer = PackageInstaller(Path.cwd(), client)
    packages = installer.get_installed_packages()

    if use_json:
        import json
        console.print_json(json.dumps(packages))
    else:
        render_installed_packages(packages)
