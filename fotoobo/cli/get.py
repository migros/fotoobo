"""
The fotoobo get commands
"""
import logging

import typer

from fotoobo.helpers import cli_path
from fotoobo.utils import get

app = typer.Typer()
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fotoobo get command callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command()
def inventory() -> None:
    """
    Get the fotoobo inventory
    """
    get.inventory()


@app.command()
def version(
    verbose: bool = typer.Option(
        False, "-v", help="Verbose output (also show most important modules)"
    ),
) -> None:
    """
    Get the fotoobo version
    """
    get.version(verbose)


@app.command()
def commands() -> None:
    """
    Get the fotoobo commands
    """
    get.commands()
