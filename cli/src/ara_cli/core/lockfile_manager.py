"""Read/write/update ara.lock with atomic writes."""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from ..models.lockfile import ARALockfile, LockfileEntry
from ..utils.constants import LOCKFILE_NAME


def read_lockfile(project_dir: Path) -> ARALockfile | None:
    """Read ara.lock from a project directory. Returns None if missing."""
    lock_path = project_dir / LOCKFILE_NAME
    if not lock_path.exists():
        return None
    with open(lock_path) as f:
        data = json.load(f)
    return ARALockfile(**data)


def write_lockfile(project_dir: Path, lockfile: ARALockfile) -> None:
    """Write ara.lock atomically (write to temp, then rename)."""
    lock_path = project_dir / LOCKFILE_NAME
    data = lockfile.model_dump(by_alias=True)

    fd, tmp_path = tempfile.mkstemp(dir=project_dir, suffix=".lock.tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        # On Windows, need to remove target first if it exists
        if lock_path.exists():
            lock_path.unlink()
        os.rename(tmp_path, str(lock_path))
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def add_package(
    project_dir: Path,
    package_name: str,
    entry: LockfileEntry,
) -> ARALockfile:
    """Add or update a package in the lock file."""
    lockfile = read_lockfile(project_dir) or ARALockfile(
        lockfileVersion=1,
        generatedAt=datetime.now(timezone.utc).isoformat(),
    )
    lockfile.packages[package_name] = entry
    lockfile.generated_at = datetime.now(timezone.utc).isoformat()
    write_lockfile(project_dir, lockfile)
    return lockfile


def remove_package(project_dir: Path, package_name: str) -> ARALockfile | None:
    """Remove a package from the lock file. Returns updated lockfile or None."""
    lockfile = read_lockfile(project_dir)
    if lockfile is None or package_name not in lockfile.packages:
        return lockfile
    del lockfile.packages[package_name]
    lockfile.generated_at = datetime.now(timezone.utc).isoformat()
    write_lockfile(project_dir, lockfile)
    return lockfile
