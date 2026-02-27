"""ara unpublish <package@version> — remove a version from the registry."""

import click

from ..core.config_manager import load_config
from ..core.registry_client import RegistryClient, run_async
from ..output.console import print_error, print_success
from ..utils.errors import ARAError


@click.command("unpublish")
@click.argument("package_version")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
@click.pass_context
def unpublish_cmd(ctx, package_version: str, yes: bool):
    """Unpublish a package version from the registry."""
    if "@" not in package_version:
        print_error("Format must be namespace/name@version (e.g., acme/my-agent@1.0.0)")
        raise SystemExit(1)

    full_name, version = package_version.rsplit("@", 1)
    if "/" not in full_name:
        print_error("Package name must be in namespace/name format.")
        raise SystemExit(1)

    namespace, name = full_name.split("/", 1)

    if not yes:
        if not click.confirm(f"Unpublish {full_name}@{version}? This cannot be undone."):
            raise SystemExit(0)

    config = load_config()
    registry = ctx.obj.get("registry") if ctx.obj else None
    client = RegistryClient(registry or config.registry_url, config.auth_token)

    if not config.auth_token:
        print_error("Not authenticated. Run 'ara login' first.")
        raise SystemExit(1)

    try:
        run_async(client.unpublish(namespace, name, version))
        print_success(f"Unpublished {full_name}@{version}")
    except ARAError as e:
        print_error(e.message)
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Cannot connect to registry at {registry or config.registry_url}. Is the server running?")
        raise SystemExit(1)
