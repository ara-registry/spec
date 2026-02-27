"""Manage ~/.ara/config.json for CLI settings and auth tokens."""

import json
from pathlib import Path

from ..models.config import CLIConfig
from ..utils.constants import CONFIG_DIR, CONFIG_FILE


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> CLIConfig:
    """Load config from ~/.ara/config.json, returning defaults if missing."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        return CLIConfig(**data)
    return CLIConfig()


def save_config(config: CLIConfig) -> None:
    """Write config to ~/.ara/config.json."""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.model_dump(), f, indent=2)
        f.write("\n")


def get_token() -> str | None:
    """Return the stored auth token, or None."""
    return load_config().auth_token


def set_token(token: str) -> None:
    """Store an auth token in config."""
    config = load_config()
    config.auth_token = token
    save_config(config)


def clear_token() -> None:
    """Remove the auth token from config."""
    config = load_config()
    config.auth_token = None
    save_config(config)
