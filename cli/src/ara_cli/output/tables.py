"""Rich table formatters for CLI output."""

from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .console import console
from ..models.api_responses import PackageListResponse


def render_search_results(results: PackageListResponse) -> None:
    if not results.packages:
        console.print("[dim]No packages found.[/dim]")
        return

    table = Table(title="Search Results", show_lines=False)
    table.add_column("Package", style="package")
    table.add_column("Version", style="version")
    table.add_column("Type", style="dim")
    table.add_column("Description")
    table.add_column("Downloads", justify="right")

    for pkg in results.packages:
        table.add_row(
            f"{pkg.namespace}/{pkg.name}",
            pkg.latest_version,
            pkg.type,
            pkg.description[:60] + ("..." if len(pkg.description) > 60 else ""),
            str(pkg.total_downloads),
        )

    console.print(table)
    console.print(f"[dim]Page {results.page} — {results.total} total results[/dim]")


def render_installed_packages(packages: dict[str, str]) -> None:
    if not packages:
        console.print("[dim]No packages installed.[/dim]")
        return

    table = Table(title="Installed Packages")
    table.add_column("Package", style="package")
    table.add_column("Version", style="version")

    for name, version in sorted(packages.items()):
        table.add_row(name, version)

    console.print(table)


def render_package_info(data: dict) -> None:
    name = data.get("name", "unknown")
    version = data.get("version", "?")
    description = data.get("description", "")
    author = data.get("author", "")
    tags = ", ".join(data.get("tags", []))
    pkg_type = data.get("type", "kiro-agent")
    license_str = data.get("license", "")
    homepage = data.get("homepage", "")
    repository = data.get("repository", "")

    info_lines = [
        f"[bold]{name}[/bold] @ [version]{version}[/version]",
        "",
        description,
        "",
        f"[dim]Type:[/dim]       {pkg_type}",
        f"[dim]Author:[/dim]     {author}",
        f"[dim]Tags:[/dim]       {tags}",
    ]
    if license_str:
        info_lines.append(f"[dim]License:[/dim]    {license_str}")
    if homepage:
        info_lines.append(f"[dim]Homepage:[/dim]   {homepage}")
    if repository:
        info_lines.append(f"[dim]Repository:[/dim] {repository}")

    deps = data.get("dependencies")
    if deps:
        info_lines.append("")
        info_lines.append("[dim]Dependencies:[/dim]")
        for dep_name, constraint in deps.items():
            info_lines.append(f"  {dep_name}: {constraint}")

    panel = Panel("\n".join(info_lines), title="Package Info", border_style="cyan")
    console.print(panel)


def render_validation_results(errors: list[str], path: str) -> None:
    if not errors:
        console.print(f"[success]Valid[/success] {path}")
        return

    console.print(f"[error]Validation failed for {path}[/error]")
    for err in errors:
        console.print(f"  [error]•[/error] {err}")
