"""Download, verify, extract, and manage installed packages."""

from __future__ import annotations

import shutil
import tarfile
import tempfile
from pathlib import Path

from ..models.lockfile import LockfileEntry
from ..utils.constants import PACKAGES_DIR
from ..utils.errors import ARAChecksumError
from .lockfile_manager import add_package, read_lockfile, remove_package
from .registry_client import RegistryClient, run_async
from .security import compute_sha256, verify_checksum


class PackageInstaller:
    """Handles downloading, verifying, and extracting packages."""

    def __init__(self, project_dir: Path, client: RegistryClient):
        self.project_dir = project_dir
        self.client = client
        self.packages_dir = project_dir / PACKAGES_DIR

    def _package_dir(self, namespace: str, name: str, version: str) -> Path:
        return self.packages_dir / namespace / name / version

    def install_package(
        self,
        namespace: str,
        name: str,
        version: str,
    ) -> Path:
        """Download, verify, and extract a single package. Returns install dir."""
        dest_dir = self._package_dir(namespace, name, version)
        if dest_dir.exists():
            return dest_dir

        # Get download URL and checksum
        download_info = run_async(self.client.get_download_url(namespace, name, version))

        # Download to temp file
        with tempfile.NamedTemporaryFile(suffix=".tgz", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            run_async(self.client.download_file(download_info.download_url, tmp_path))

            # Verify checksum
            verify_checksum(tmp_path, download_info.checksum)

            # Extract
            dest_dir.mkdir(parents=True, exist_ok=True)
            with tarfile.open(tmp_path, "r:gz") as tar:
                tar.extractall(dest_dir, filter="data")
        finally:
            tmp_path.unlink(missing_ok=True)

        # Update lock file
        add_package(
            self.project_dir,
            f"{namespace}/{name}",
            LockfileEntry(
                version=version,
                type=self._get_installed_type(dest_dir),
                integrity=download_info.checksum,
                resolved=download_info.download_url,
                dependencies={},
            ),
        )

        return dest_dir

    def install_from_lockfile(self) -> list[str]:
        """Install all packages from ara.lock. Returns list of installed package names."""
        lockfile = read_lockfile(self.project_dir)
        if lockfile is None:
            return []

        installed: list[str] = []
        for pkg_name, entry in lockfile.packages.items():
            namespace, name = pkg_name.split("/", 1)
            dest_dir = self._package_dir(namespace, name, entry.version)
            if not dest_dir.exists():
                self.install_package(namespace, name, entry.version)
            installed.append(pkg_name)
        return installed

    def uninstall_package(self, namespace: str, name: str) -> bool:
        """Remove a package from disk and lock file. Returns True if found."""
        pkg_dir = self.packages_dir / namespace / name
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)

        # Clean up empty namespace dir
        ns_dir = self.packages_dir / namespace
        if ns_dir.exists() and not any(ns_dir.iterdir()):
            ns_dir.rmdir()

        remove_package(self.project_dir, f"{namespace}/{name}")
        return True

    def get_installed_packages(self) -> dict[str, str]:
        """Scan .ara/packages/ and return {name: version} map."""
        installed: dict[str, str] = {}
        if not self.packages_dir.exists():
            return installed

        for ns_dir in self.packages_dir.iterdir():
            if not ns_dir.is_dir():
                continue
            for pkg_dir in ns_dir.iterdir():
                if not pkg_dir.is_dir():
                    continue
                for ver_dir in pkg_dir.iterdir():
                    if ver_dir.is_dir():
                        installed[f"{ns_dir.name}/{pkg_dir.name}"] = ver_dir.name
        return installed

    def _get_installed_type(self, dest_dir: Path) -> str:
        """Read package type from extracted ara.json."""
        import json
        manifest_path = dest_dir / "ara.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                data = json.load(f)
            return data.get("type", "kiro-agent")
        return "kiro-agent"
