"""ara config set/get — manage CLI configuration."""

import click

from ..core.config_manager import load_config, save_config
from ..output.console import print_error, print_success, print_info


@click.group("config")
def config_cmd():
    """Manage CLI configuration."""
    pass


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration value."""
    config = load_config()
    valid_keys = {"registry_url", "default_author"}

    if key not in valid_keys:
        print_error(f"Unknown config key: '{key}'. Valid keys: {', '.join(sorted(valid_keys))}")
        raise SystemExit(1)

    setattr(config, key, value)
    save_config(config)
    print_success(f"Set {key} = {value}")


@config_cmd.command("get")
@click.argument("key")
def config_get(key: str):
    """Get a configuration value."""
    config = load_config()
    valid_keys = {"registry_url", "default_author", "auth_token"}

    if key not in valid_keys:
        print_error(f"Unknown config key: '{key}'. Valid keys: {', '.join(sorted(valid_keys))}")
        raise SystemExit(1)

    value = getattr(config, key, None)
    if key == "auth_token" and value:
        # Mask the token
        print_info(f"{key} = {value[:8]}...{value[-4:]}" if len(value) > 12 else f"{key} = ****")
    elif value is not None:
        print_info(f"{key} = {value}")
    else:
        print_info(f"{key} = (not set)")
