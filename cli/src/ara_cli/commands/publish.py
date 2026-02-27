"""ara publish — validate, archive, and upload a package."""

import json
import click
from pathlib import Path

from rich.progress import Progress

from ..core.config_manager import load_config
from ..core.packager import PackageArchiver
from ..core.registry_client import RegistryClient, run_async
from ..core.security import compute_sha256
from ..core.validation import validate, read_manifest
from ..output.console import console, print_error, print_success
from ..utils.constants import MANIFEST_NAME
from ..utils.errors import ARAError


@click.command("publish")
@click.option("--dry-run", is_flag=True, help="Validate and archive but don't upload.")
@click.pass_context
def publish_cmd(ctx, dry_run: bool):
    """Publish a package to the registry."""
    project_dir = Path.cwd()
    manifest_path = project_dir / MANIFEST_NAME

    # Step 1: Validate
    errors = validate(manifest_path)
    if errors:
        print_error("Manifest validation failed:")
        for err in errors:
            console.print(f"  [error]•[/error] {err}")
        raise SystemExit(1)

    manifest = read_manifest(manifest_path)
    namespace, name = manifest.parse_name()
    console.print(f"Publishing [package]{manifest.name}[/package]@[version]{manifest.version}[/version]")

    # Step 2: Create archive
    archiver = PackageArchiver(project_dir, manifest.files)
    archive_path = archiver.create_archive()
    archive_size = archive_path.stat().st_size
    checksum = compute_sha256(archive_path)
    console.print(f"[dim]Archive: {archive_size} bytes, {checksum}[/dim]")

    if dry_run:
        archive_path.unlink(missing_ok=True)
        print_success("Dry run complete. Package is valid and archive was created.")
        return

    # Step 3: Upload
    config = load_config()
    registry = ctx.obj.get("registry") if ctx.obj else None
    client = RegistryClient(registry or config.registry_url, config.auth_token)

    if not config.auth_token:
        print_error("Not authenticated. Run 'ara login' first.")
        archive_path.unlink(missing_ok=True)
        raise SystemExit(1)

    try:
        manifest_data = manifest.model_dump(by_alias=True, exclude_none=True)

        with Progress(console=console) as progress:
            task = progress.add_task("Uploading...", total=3)

            # 3a: Initiate upload
            upload_resp = run_async(client.initiate_upload(
                namespace, name, manifest.version, manifest_data, archive_size,
            ))
            progress.advance(task)

            # 3b: Upload archive to signed URL
            run_async(client.upload_file(upload_resp.package_upload_url, archive_path))

            # 3b2: Upload manifest to signed URL
            manifest_bytes = json.dumps(manifest_data, indent=2).encode()
            run_async(client.upload_manifest(upload_resp.manifest_upload_url, manifest_bytes))
            progress.advance(task)

            # 3c: Complete upload
            result = run_async(client.complete_upload(
                namespace, name, manifest.version, upload_resp.upload_id,
            ))
            progress.advance(task)

        print_success(f"Published {manifest.name}@{manifest.version}")
    except ARAError as e:
        print_error(e.message)
        raise SystemExit(1)
    except Exception as e:
        msg = str(e)
        if "Connect" in msg or "connection" in msg.lower():
            print_error(f"Cannot connect to registry at {registry or config.registry_url}. Is the server running?")
        else:
            print_error(f"Publish failed: {msg}")
        raise SystemExit(1)
    finally:
        archive_path.unlink(missing_ok=True)
