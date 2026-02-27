"""Create .tgz archives for publishing packages."""

import io
import tarfile
from pathlib import Path

from ..utils.constants import DEFAULT_EXCLUDES, MANIFEST_NAME


class PackageArchiver:
    """Creates a .tgz archive of a package directory."""

    def __init__(self, base_dir: Path, files: list[str] | None = None):
        self.base_dir = base_dir
        self.files = files

    def _should_exclude(self, path: Path) -> bool:
        for part in path.parts:
            if part in DEFAULT_EXCLUDES:
                return True
        return False

    def _collect_files(self) -> list[Path]:
        """Collect files to include in the archive."""
        if self.files is not None:
            collected: list[Path] = []
            for f in self.files:
                target = self.base_dir / f
                if target.is_dir():
                    for child in target.rglob("*"):
                        if child.is_file() and not self._should_exclude(child.relative_to(self.base_dir)):
                            collected.append(child)
                elif target.is_file():
                    collected.append(target)
            # Always include ara.json
            manifest = self.base_dir / MANIFEST_NAME
            if manifest.exists() and manifest not in collected:
                collected.append(manifest)
            return collected

        # No files field: include everything except excludes
        collected = []
        for child in self.base_dir.rglob("*"):
            if child.is_file() and not self._should_exclude(child.relative_to(self.base_dir)):
                collected.append(child)
        return collected

    def create_archive(self, output_path: Path | None = None) -> Path:
        """Create a .tgz archive. Returns path to the archive."""
        files = self._collect_files()

        if output_path is None:
            output_path = self.base_dir / "package.tgz"

        with tarfile.open(output_path, "w:gz") as tar:
            for file_path in files:
                arcname = str(file_path.relative_to(self.base_dir))
                tar.add(file_path, arcname=arcname)

        return output_path

    def create_archive_bytes(self) -> bytes:
        """Create a .tgz archive in memory, returning bytes."""
        files = self._collect_files()
        buf = io.BytesIO()

        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            for file_path in files:
                arcname = str(file_path.relative_to(self.base_dir))
                tar.add(file_path, arcname=arcname)

        return buf.getvalue()
