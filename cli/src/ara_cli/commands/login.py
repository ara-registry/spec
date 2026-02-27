"""ara login — authenticate with a registry."""

import click

from ..core.config_manager import set_token
from ..output.console import print_success, print_info


@click.command("login")
@click.option("--token", default=None, help="Auth token (prompted if not provided).")
def login_cmd(token: str | None):
    """Authenticate with the ARA registry."""
    if token is None:
        token = click.prompt("Enter your auth token", hide_input=True)

    set_token(token)
    print_success("Login successful. Token saved.")
