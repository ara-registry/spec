"""Shared Rich console and themed output helpers."""

from rich.console import Console
from rich.theme import Theme

ara_theme = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red bold",
    "package": "bold magenta",
    "version": "bold blue",
    "dim": "dim",
})

console = Console(theme=ara_theme)


def print_error(message: str) -> None:
    console.print(f"[error]Error:[/error] {message}")


def print_success(message: str) -> None:
    console.print(f"[success]{message}[/success]")


def print_info(message: str) -> None:
    console.print(f"[info]{message}[/info]")


def print_warning(message: str) -> None:
    console.print(f"[warning]Warning:[/warning] {message}")


def print_json_output(data: dict) -> None:
    """Print raw JSON for --json flag."""
    import json
    console.print_json(json.dumps(data))
