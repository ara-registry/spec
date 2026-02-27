"""ara info <package> — show package details."""

import click

from ..core.config_manager import load_config
from ..core.registry_client import RegistryClient, run_async
from ..output.console import print_error, console
from ..output.tables import render_package_info
from ..utils.errors import ARAError


@click.command("info")
@click.argument("package")
@click.option("--version", "-v", "pkg_version", default=None, help="Specific version.")
@click.option("--json-output", "use_json", is_flag=True, help="Output raw JSON.")
@click.pass_context
def info_cmd(ctx, package: str, pkg_version: str | None, use_json: bool):
    """Show detailed information about a package."""
    if "/" not in package:
        print_error("Package name must be in namespace/name format.")
        raise SystemExit(1)

    namespace, name = package.split("/", 1)
    config = load_config()
    registry = ctx.obj.get("registry") if ctx.obj else None
    client = RegistryClient(registry or config.registry_url, config.auth_token)

    try:
        if pkg_version is None:
            versions_resp = run_async(client.list_versions(namespace, name))
            pkg_version = versions_resp.latest

        data = run_async(client.get_manifest(namespace, name, pkg_version))
    except ARAError as e:
        print_error(e.message)
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Cannot connect to registry at {registry or config.registry_url}. Is the server running?")
        raise SystemExit(1)

    if use_json:
        import json
        console.print_json(json.dumps(data))
    else:
        render_package_info(data)
