"""
The FortiGate check commands
"""
# pylint: disable=anomalous-backslash-in-string

import logging

import typer

from fotoobo.helpers import cli_path
from fotoobo.helpers.config import config
from fotoobo.inventory.inventory import Inventory
from fotoobo.tools import fgt

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
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
        help="The FortiManager hostname to access (must be defined in the inventory).",
        metavar="[host]",
    ),
    smtp_server: str = typer.Option(
        None,
        "--smtp",
        help="The smtp configuration from the inventory.",
        metavar="server",
        show_default=False,
    ),
) -> None:
    """
    Check the FortiGate HA master.

    Although this command checks the HA master status of FortiGates you have to specify a
    FortiManager to access. The command searches for all FortiGate clusters in the FortiManager
    and checks if the designated primary node really is the HA master node.

    The optional argument \[host] makes this command somewhat magic. If you omit \[host] it searches
    for all devices in the default FortiManager (fmg) in the inventory.
    """
    inventory = Inventory(config.inventory_file)
    result = fgt.monitor.hamaster(host)

    if smtp_server:
        if smtp_server in inventory.assets:
            result.send_mail(
                inventory.assets[smtp_server],
                ["warning", "error"],
                count=True,
                command=True,
            )

        else:
            log.warning("SMTP server %s not in found in inventory.", smtp_server)

    result.print_result_as_table(
        headers=["FortiGate Cluster", "Status"],
        title="FortiGate HA master status",
        host_is_first_column=True,
    )
