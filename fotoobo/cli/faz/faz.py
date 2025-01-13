"""
The FortiAnalyzer commands
"""

import logging

import typer

from fotoobo.helpers import cli_path

from . import get

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The faz subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)


app.add_typer(get.app, name="get", help="FortiAnalyzer get commands.")
