"""
The FortiGate commands
"""

import logging

import typer

from fotoobo.helpers import cli_path

from .firewall import firewall

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


app.add_typer(firewall.app, name="firewall", help="FortiGate get cmdb firewall commands.")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fgt get cmdb subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)
