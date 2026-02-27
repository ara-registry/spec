"""ara init — create a new ara.json via interactive wizard."""

import json
import click
from pathlib import Path

from ..output.console import print_error, print_success, console
from ..output.prompts import init_wizard
from ..utils.constants import MANIFEST_NAME, SCHEMA_URL


@click.command("init")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def init_cmd(yes: bool):
    """Create a new ara.json in the current directory."""
    manifest_path = Path.cwd() / MANIFEST_NAME

    if manifest_path.exists() and not yes:
        if not click.confirm(f"{MANIFEST_NAME} already exists. Overwrite?", default=False):
            raise SystemExit(0)

    data = init_wizard()
    data["$schema"] = SCHEMA_URL

    with open(manifest_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print_success(f"Created {MANIFEST_NAME}")
