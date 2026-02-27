"""ara logout — remove stored auth token."""

import click

from ..core.config_manager import clear_token
from ..output.console import print_success


@click.command("logout")
def logout_cmd():
    """Remove stored authentication token."""
    clear_token()
    print_success("Logged out. Token removed.")
