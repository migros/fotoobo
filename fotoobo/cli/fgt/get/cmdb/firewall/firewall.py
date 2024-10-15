"""
The FortiGate commands
"""

# pylint: disable=anomalous-backslash-in-string
import logging

import typer

from fotoobo.helpers import cli_path

from .service import service

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


app.add_typer(service.app, name="service", help="FortiGate get cmdb firewall service commands.")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fgt get cmdb get firewall subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)


@app.command()
def address(
    name: str = typer.Argument(
        "",
        help="The firewall address object to get \[default: <all>]",
        show_default=False,
        metavar="[name]",
    ),
    output_file: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (format is specified by extension)",
        metavar="[file]",
        show_default=False,
    ),
) -> None:
    """
    Get FortiGate cmdb firewall address.

    The FortiGate api endpoint is: /cmdb/firewall/address
    """
    # TODO: Here to add the address cli code
    print("ADDRESS")


@app.command()
def addrgrp(
    name: str = typer.Argument(
        "",
        help="The firewall address group object to get \[default: <all>]",
        show_default=False,
        metavar="[name]",
    ),
    output_file: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (format is specified by extension)",
        metavar="[file]",
        show_default=False,
    ),
) -> None:
    """
    Get FortiGate cmdb firewall address group.

    The FortiGate api endpoint is: /cmdb/firewall/addrgrp
    """
    # TODO: Here to add the address group cli code
    print("ADDRGRP")
