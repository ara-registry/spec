"""Constants used across the ARA CLI."""

from pathlib import Path

DEFAULT_REGISTRY_URL = "http://localhost:3000"
MANIFEST_NAME = "ara.json"
LOCKFILE_NAME = "ara.lock"
PACKAGES_DIR = ".ara/packages"
CONFIG_DIR = Path.home() / ".ara"
CONFIG_FILE = CONFIG_DIR / "config.json"

SCHEMA_URL = "https://raw.githubusercontent.com/aws/ara/refs/heads/main/ara.schema.json"

DEFAULT_EXCLUDES = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".env",
    ".DS_Store",
    "Thumbs.db",
    ".ara",
    "ara.lock",
    ".gitignore",
    ".npmignore",
}

TRUSTED_GIT_DOMAINS = [
    "github.com",
    "gitlab.com",
    "bitbucket.org",
]
