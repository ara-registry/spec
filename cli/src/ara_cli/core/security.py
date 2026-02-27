"""Security utilities: checksums and URL validation."""

import hashlib
from pathlib import Path
from urllib.parse import urlparse

from ..utils.errors import ARAChecksumError


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file. Returns 'sha256:<hex>' string."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def compute_sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of bytes. Returns 'sha256:<hex>' string."""
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def verify_checksum(file_path: Path, expected: str) -> None:
    """Verify a file's SHA-256 checksum. Raises ARAChecksumError on mismatch."""
    actual = compute_sha256(file_path)
    if actual != expected:
        raise ARAChecksumError(
            f"Checksum mismatch for {file_path.name}",
            expected=expected,
            actual=actual,
        )


def validate_git_url(url: str, trusted_domains: list[str] | None = None) -> list[str]:
    """Validate a git URL against security rules. Returns list of errors."""
    errors: list[str] = []
    parsed = urlparse(url)

    if parsed.scheme != "https":
        errors.append(f"Git URL must use HTTPS, got: {parsed.scheme}")

    if parsed.username or parsed.password:
        errors.append("Git URL must not contain embedded credentials")

    if ".." in parsed.path:
        errors.append("Git URL must not contain path traversal")

    if trusted_domains and parsed.hostname not in trusted_domains:
        errors.append(f"Git host '{parsed.hostname}' is not in the trusted domains list")

    return errors
