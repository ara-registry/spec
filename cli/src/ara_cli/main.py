"""ARA CLI — Click group root with global options."""

import click

from . import __version__
from .commands.config import config_cmd
from .commands.init import init_cmd
from .commands.info import info_cmd
from .commands.install import install_cmd
from .commands.list_cmd import list_cmd
from .commands.login import login_cmd
from .commands.logout import logout_cmd
from .commands.publish import publish_cmd
from .commands.search import search_cmd
from .commands.uninstall import uninstall_cmd
from .commands.unpublish import unpublish_cmd
from .commands.update import update_cmd
from .commands.validate import validate_cmd


@click.group()
@click.version_option(__version__, prog_name="ara")
@click.option("--registry", default=None, envvar="ARA_REGISTRY", help="Registry URL override.")
@click.pass_context
def main(ctx, registry: str | None):
    """ARA — AI Registry for Agents."""
    ctx.ensure_object(dict)
    if registry:
        ctx.obj["registry"] = registry


main.add_command(init_cmd)
main.add_command(validate_cmd)
main.add_command(search_cmd)
main.add_command(info_cmd)
main.add_command(install_cmd)
main.add_command(uninstall_cmd)
main.add_command(update_cmd)
main.add_command(list_cmd)
main.add_command(publish_cmd)
main.add_command(unpublish_cmd)
main.add_command(login_cmd)
main.add_command(logout_cmd)
main.add_command(config_cmd)


if __name__ == "__main__":
    main()
