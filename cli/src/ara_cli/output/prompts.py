"""Interactive Rich prompts for ara init wizard."""

from rich.prompt import Prompt, Confirm

from .console import console


def prompt_text(label: str, default: str = "") -> str:
    return Prompt.ask(f"[info]{label}[/info]", default=default, console=console)


def prompt_confirm(label: str, default: bool = False) -> bool:
    return Confirm.ask(f"[info]{label}[/info]", default=default, console=console)


def init_wizard() -> dict:
    """Interactive wizard for creating a new ara.json. Returns field dict."""
    console.print("[bold]Create a new ara.json[/bold]\n")

    name = prompt_text("Package name (namespace/package-name)")
    version = prompt_text("Version", default="1.0.0")
    description = prompt_text("Description")
    author = prompt_text("Author email")
    tags_str = prompt_text("Tags (comma-separated)")
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]

    type_choices = [
        "kiro-agent", "mcp-server", "context", "skill",
        "kiro-powers", "kiro-steering", "agents-md",
    ]
    console.print(f"[dim]Types: {', '.join(type_choices)}[/dim]")
    pkg_type = prompt_text("Type", default="kiro-agent")

    license_str = prompt_text("License (SPDX, optional)", default="")

    result: dict = {
        "name": name,
        "version": version,
        "description": description,
        "author": author,
        "tags": tags,
    }

    if pkg_type and pkg_type != "kiro-agent":
        result["type"] = pkg_type
    if license_str:
        result["license"] = license_str

    return result
