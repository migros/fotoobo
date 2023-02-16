"""
The FortiGate get commands
"""
import logging

import typer

from fotoobo.helpers import cli_path
from fotoobo.helpers.output import print_datatable
from fotoobo.utils import fgt

app = typer.Typer()
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fgt get subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command()
def version(
    host: str = typer.Argument(
        "",
        help="The FortiGate hostname to access (must be defined in inventory)",
        show_default=False,
        metavar="[host]",
    )
) -> None:
    """
    Get the FortiGate version

    The optional argument [host] makes this command somewhat magic. If you omit [host] it searches
    for all devices of type 'fortigate' in the inventory and tries to get their FortiOS version.
    """
    data = fgt.get.version(host)
    print_datatable(data, title="FortiGate Versions", headers=["FortiGate", "Version"])
