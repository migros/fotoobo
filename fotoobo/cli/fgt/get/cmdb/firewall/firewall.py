"""
The FortiGate commands
"""

import logging
from typing import Optional

import typer
from typing_extensions import Annotated

from fotoobo.exceptions import GeneralError
from fotoobo.helpers import cli_path
from fotoobo.tools.fgt.cmdb.firewall import *  # pylint: disable=wildcard-import

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


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
    host: Annotated[
        str,
        typer.Argument(
            help="The FortiGate hostname to access (must be defined in the inventory).",
            metavar="[host]",
        ),
    ],
    name: Annotated[
        str,
        typer.Argument(
            help="The firewall address object to get.",
            metavar="[name]",
        ),
    ] = "",
    vdom: Annotated[
        str,
        typer.Option(
            "--vdom",
            help="The vdom to query ('vdom1' or 'vdom1,vdom2').",
            metavar="[vdom]",
        ),
    ] = "*",
    output_file: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="Output file (format is specified by extension).",
            metavar="[file]",
            show_default=False,
        ),
    ] = None,
) -> None:
    """Get FortiGate cmdb firewall address."""
    if name and ("*" in vdom or "," in vdom):
        raise GeneralError("With name argument you have to specify one single VDOM (with --vdom)")

    result = get_cmdb_firewall_address(host, name, vdom, output_file)
    if not output_file:
        result.print_table_raw(result.results[host], auto_header=True, title=host)


@app.command()
def addrgrp(
    host: Annotated[
        str,
        typer.Argument(
            help="The FortiGate hostname to access (must be defined in the inventory).",
            metavar="[host]",
        ),
    ],
    name: Annotated[
        str,
        typer.Argument(
            help="The firewall address group object to get.",
            metavar="[name]",
        ),
    ] = "",
    vdom: Annotated[
        str,
        typer.Option(
            "--vdom",
            help="The vdom to query ('vdom1' or 'vdom1,vdom2').",
            metavar="[vdom]",
        ),
    ] = "*",
    output_file: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="Output file (format is specified by extension).",
            metavar="[file]",
            show_default=False,
        ),
    ] = None,
) -> None:
    """Get FortiGate cmdb firewall address group."""
    if name and ("*" in vdom or "," in vdom):
        raise GeneralError("With name argument you have to specify one single VDOM (with --vdom)")

    result = get_cmdb_firewall_addrgrp(host, name, vdom, output_file)
    if not output_file:
        result.print_table_raw(result.results[host], auto_header=True, title=host)


@app.command()
def service_custom(
    host: Annotated[
        str,
        typer.Argument(
            help="The FortiGate hostname to access (must be defined in the inventory).",
            metavar="[host]",
        ),
    ],
    name: Annotated[
        str,
        typer.Argument(
            help="The firewall service object to get.",
            metavar="[name]",
        ),
    ] = "",
    vdom: Annotated[
        str,
        typer.Option(
            "--vdom",
            help="The vdom to query ('vdom1' or 'vdom1,vdom2').",
            metavar="[vdom]",
        ),
    ] = "*",
    output_file: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="Output file (format is specified by extension).",
            metavar="[file]",
            show_default=False,
        ),
    ] = None,
) -> None:
    """Get FortiGate cmdb firewall service custom."""
    if name and ("*" in vdom or "," in vdom):
        raise GeneralError("With name argument you have to specify one single VDOM (with --vdom)")

    result = get_cmdb_firewall_service_custom(host, name, vdom, output_file)
    if not output_file:
        result.print_table_raw(result.results[host], auto_header=True, title=host)


@app.command()
def service_group(
    host: Annotated[
        str,
        typer.Argument(
            help="The FortiGate hostname to access (must be defined in the inventory).",
            metavar="[host]",
        ),
    ],
    name: Annotated[
        str,
        typer.Argument(
            help="The firewall service group to get.",
            metavar="[name]",
        ),
    ] = "",
    vdom: Annotated[
        str,
        typer.Option(
            "--vdom",
            help="The vdom to query ('vdom1' or 'vdom1,vdom2').",
            metavar="[vdom]",
        ),
    ] = "*",
    output_file: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="Output file (format is specified by extension).",
            metavar="[file]",
            show_default=False,
        ),
    ] = None,
) -> None:
    """Get FortiGate cmdb firewall service group."""
    if name and ("*" in vdom or "," in vdom):
        raise GeneralError("With name argument you have to specify one single VDOM (with --vdom)")

    result = get_cmdb_firewall_service_group(host, name, vdom, output_file)
    if not output_file:
        result.print_table_raw(result.results[host], auto_header=True, title=host)
