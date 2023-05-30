"""
The FortiGate get commands
"""
import logging
from pathlib import Path

import typer

from fotoobo.helpers.output import print_datatable, print_dicttable
from fotoobo.tools import fgt

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


@app.command(no_args_is_help=True)
def check(
    configuration: Path = typer.Argument(
        ...,
        help="The FortiGate configuration file or directory.",
        metavar="[config]",
        show_default=False,
    ),
    bundles: Path = typer.Argument(
        ...,
        help="Filename of the file containing the check bundles.",
        metavar="[bundles]",
        show_default=False,
    ),
) -> None:
    """
    Check one or more FortiGate configuration files.
    """
    fgt.config.check(configuration, bundles)


@app.command(no_args_is_help=True)
def info(
    configuration: Path = typer.Argument(
        ...,
        help="The FortiGate configuration file or directory.",
        metavar="[config]",
        show_default=False,
    ),
    as_list: bool = typer.Option(
        False, "--list", "-l", help="Print the result as a list instead of separate blocks."
    ),
) -> None:
    """
    Get the information from one or more FortiGate configuration files.
    """
    infos = fgt.config.info(configuration)
    info_dicts = [data.__dict__ for data in infos]

    if as_list:
        print_datatable(info_dicts, auto_header=True)

    else:
        for data in info_dicts:
            print_dicttable(data, title=data.get("hostname", "unknown"))
