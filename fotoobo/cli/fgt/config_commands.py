"""
The FortiGate get commands
"""
import logging
from pathlib import Path

import typer

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
    result = fgt.config.check(configuration, bundles)

    result.print_messages()


@app.command(no_args_is_help=True)
def get(
    configuration: Path = typer.Argument(
        ...,
        help="The FortiGate configuration file or directory.",
        metavar="[config]",
        show_default=False,
    ),
    scope: str = typer.Argument(
        ..., help="Scope of the configuration ('global' or 'vdom')", metavar="[scope]"
    ),
    path: str = typer.Argument("/", help="Configuration path", metavar="[path]"),
) -> None:
    """Get configuration or parts of it from one or more FortiGate configuration files"""
    result = fgt.config.get(configuration, scope, path)
    result.print_raw()


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
    result = fgt.config.info(configuration)

    if as_list:
        info_dicts = []

        for _, _info in result.all_results().items():
            info_dicts.append(_info.__dict__)

        result.print_table_raw(info_dicts, [], auto_header=True)

    else:
        result.print_result_as_table()
