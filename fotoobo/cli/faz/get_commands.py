"""
The FortiAnalyzer get commands
"""
import logging

import typer

from fotoobo.helpers import cli_path
from fotoobo.helpers.output import print_datatable
from fotoobo.utils import faz

app = typer.Typer()
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The faz get subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command()
def version(
    host: str = typer.Argument(
        "faz",
        help="The FortiAnalyzer hostname to access (must be defined in inventory)",
        metavar="[host]",
    )
) -> None:
    """
    Get the FortiAnalyzer version
    """
    data = faz.get.version(host)
    print_datatable(data, title="FortiAnalyzer Version", headers=["FortiAnalyzer", "Version"])
