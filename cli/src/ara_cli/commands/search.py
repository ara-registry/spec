"""ara search <query> — search the registry."""

import json
import click

from ..core.config_manager import load_config
from ..core.registry_client import RegistryClient, run_async
from ..output.console import print_error, console
from ..output.tables import render_search_results
from ..utils.errors import ARAError


@click.command("search")
@click.argument("query")
@click.option("--tags", default="", help="Filter by tags (comma-separated).")
@click.option("--type", "package_type", default="", help="Filter by package type.")
@click.option("--sort", default="", help="Sort by: name, downloads, updated.")
@click.option("--page", default=1, type=int, help="Page number.")
@click.option("--json-output", "use_json", is_flag=True, help="Output raw JSON.")
@click.pass_context
def search_cmd(ctx, query: str, tags: str, package_type: str, sort: str, page: int, use_json: bool):
    """Search for packages in the registry."""
    config = load_config()
    registry = ctx.obj.get("registry") if ctx.obj else None
    client = RegistryClient(registry or config.registry_url, config.auth_token)

    try:
        results = run_async(client.search_packages(
            query=query, tags=tags, package_type=package_type, sort=sort, page=page,
        ))
    except ARAError as e:
        print_error(e.message)
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Cannot connect to registry at {registry or config.registry_url}. Is the server running?")
        raise SystemExit(1)

    if use_json:
        console.print_json(results.model_dump_json())
    else:
        render_search_results(results)
