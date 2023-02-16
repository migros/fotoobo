"""
The FortiGate check commands
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
    The fgt check subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command()
def hamaster(
    host: str = typer.Argument(
        "fmg",
        help="The FortiManager hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
    smtp_server: str = typer.Option(
        None, "--smtp", help="the smtp configuration from the inventory", metavar="server"
    ),
) -> None:
    """
    Check the FortiGate HA master

    Although this command checks the HA master status of FortiGates you have to specify a
    FortiManager to access. The command searches for all FortiGate clusters in the FortiManager
    and checks if the designated primary node really is the HA master node.

    The optional argument [host] makes this command somewhat magic. If you omit [host] it searches
    for all devices in the default FortiManager (fmg) in the inventory.
    """
    data = fgt.check.hamaster(host, smtp_server)
    print_datatable(
        data, title="FortiGate HA master status", headers=["FortiGate Cluster", "Status"]
    )
