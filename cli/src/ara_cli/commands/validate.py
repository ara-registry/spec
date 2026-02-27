"""ara validate [path] — validate an ara.json manifest."""

import click
from pathlib import Path

from ..core.validation import validate
from ..output.tables import render_validation_results
from ..utils.constants import MANIFEST_NAME


@click.command("validate")
@click.argument("path", default=MANIFEST_NAME, type=click.Path(path_type=Path))
def validate_cmd(path: Path):
    """Validate an ara.json file."""
    errors = validate(path)
    render_validation_results(errors, str(path))
    if errors:
        raise SystemExit(1)
