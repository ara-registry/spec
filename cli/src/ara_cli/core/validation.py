"""Manifest validation and reading."""

import json
from pathlib import Path

from pydantic import ValidationError

from ..models.manifest import ARAManifest
from ..utils.errors import ARAValidationError


def read_manifest(path: Path) -> ARAManifest:
    """Read and parse an ara.json file into an ARAManifest."""
    with open(path) as f:
        data = json.load(f)
    return ARAManifest(**data)


def validate(path: Path) -> list[str]:
    """Validate an ara.json file. Returns list of error messages (empty = valid)."""
    try:
        read_manifest(path)
        return []
    except FileNotFoundError:
        return [f"File not found: {path}"]
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except ValidationError as e:
        return [err["msg"] for err in e.errors()]


def validate_files_field(files: list[str], base_dir: Path) -> list[str]:
    """Validate that files listed in the manifest exist. Returns error messages."""
    errors: list[str] = []
    for f in files:
        target = base_dir / f
        if not target.exists():
            errors.append(f"File not found: {f}")
    return errors


def validate_dependencies(dependencies: dict[str, str]) -> list[str]:
    """Validate dependency name and constraint format. Returns error messages."""
    import re
    from ..utils.semver import parse_version

    errors: list[str] = []
    name_pattern = re.compile(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$")

    for name, constraint in dependencies.items():
        if not name_pattern.match(name):
            errors.append(f"Invalid dependency name: '{name}'")

        constraint = constraint.strip()
        if constraint == "*":
            continue

        version_str = constraint.lstrip("^~>=<!")
        if version_str:
            try:
                parse_version(version_str)
            except ValueError:
                errors.append(f"Invalid version constraint for '{name}': {constraint}")

    return errors
