"""Semantic versioning utilities wrapping the packaging library."""

import re
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet, InvalidSpecifier


def parse_version(version_str: str) -> Version:
    """Parse a semantic version string into a Version object.

    Raises ValueError if the version string is invalid.
    """
    try:
        return Version(version_str)
    except InvalidVersion:
        raise ValueError(f"Invalid version: {version_str}")


def _translate_constraint(constraint: str) -> str:
    """Translate ARA version constraints to PEP 440 specifiers.

    Supports: ^1.0.0, ~1.0.0, >=1.0.0, *, exact versions.
    """
    constraint = constraint.strip()

    if constraint == "*":
        return ">=0.0.0"

    if constraint.startswith("^"):
        # Caret: compatible with major version (^1.2.3 → >=1.2.3,<2.0.0)
        ver = constraint[1:]
        v = parse_version(ver)
        if v.major > 0:
            upper = f"{v.major + 1}.0.0"
        elif v.minor > 0:
            upper = f"0.{v.minor + 1}.0"
        else:
            upper = f"0.0.{v.micro + 1}"
        return f">={ver},<{upper}"

    if constraint.startswith("~"):
        # Tilde: compatible with minor version (~1.2.3 → >=1.2.3,<1.3.0)
        ver = constraint[1:]
        v = parse_version(ver)
        upper = f"{v.major}.{v.minor + 1}.0"
        return f">={ver},<{upper}"

    if re.match(r"^[><=!]", constraint):
        return constraint

    # Exact version
    return f"=={constraint}"


def satisfies_constraint(version_str: str, constraint: str) -> bool:
    """Check if a version satisfies a constraint.

    Args:
        version_str: The version to check (e.g., "1.2.3").
        constraint: The constraint to check against (e.g., "^1.0.0").

    Returns:
        True if the version satisfies the constraint.
    """
    try:
        pep440_spec = _translate_constraint(constraint)
        specifier = SpecifierSet(pep440_spec)
        version = parse_version(version_str)
        return version in specifier
    except (ValueError, InvalidSpecifier):
        return False


def best_matching_version(versions: list[str], constraint: str) -> str | None:
    """Find the best (highest) version matching a constraint.

    Args:
        versions: List of available version strings.
        constraint: Version constraint (e.g., "^1.0.0").

    Returns:
        The highest version matching the constraint, or None.
    """
    matching = []
    for v in versions:
        if satisfies_constraint(v, constraint):
            try:
                matching.append(parse_version(v))
            except ValueError:
                continue

    if not matching:
        return None

    best = max(matching)
    return str(best)
