"""
The FortiGate get commands
"""

import logging
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from fotoobo.helpers.config import config
from fotoobo.inventory.inventory import Inventory
from fotoobo.tools import fgt

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


@app.command(no_args_is_help=True)
def check(
    configuration: Annotated[
        Path,
        typer.Argument(
            help="The FortiGate configuration file or directory.",
            metavar="[config]",
            show_default=False,
        ),
    ],
    bundles: Annotated[
        Path,
        typer.Argument(
            help="Filename of the file containing the check bundles.",
            metavar="[bundles]",
            show_default=False,
        ),
    ],
    smtp_server: Annotated[
        Optional[str],
        typer.Option(
            "--smtp",
            help="The smtp configuration from the inventory.",
            metavar="[server]",
            show_default=False,
        ),
    ] = None,
) -> None:
    """
    Check one or more FortiGate configuration files.
    """
    inventory = Inventory(config.inventory_file)
    result = fgt.config.check(configuration, bundles)

    if smtp_server:
        if smtp_server in inventory.assets:
            result.send_messages_as_mail(
                inventory.assets[smtp_server],
                count=True,
                command=True,
            )

        else:
            log.warning("SMTP server '%s' not in found in inventory.", smtp_server)

    result.print_messages()


@app.command(no_args_is_help=True)
def get(
    configuration: Annotated[
        Path,
        typer.Argument(
            help="The FortiGate configuration file or directory.",
            metavar="[config]",
            show_default=False,
        ),
    ],
    scope: Annotated[
        str,
        typer.Argument(help="Scope of the configuration ('global' or 'vdom')", metavar="[scope]"),
    ],
    path: Annotated[str, typer.Argument(help="Configuration path", metavar="[path]")] = "/",
) -> None:
    """Get configuration or parts of it from one or more FortiGate configuration files."""
    result = fgt.config.get(configuration, scope, path)
    result.print_raw()


@app.command(no_args_is_help=True)
def info(
    configuration: Annotated[
        Path,
        typer.Argument(
            help="The FortiGate configuration file or directory.",
            metavar="[config]",
            show_default=False,
        ),
    ],
    as_list: Annotated[
        bool,
        typer.Option("--list", "-l", help="Print the result as a list instead of separate blocks."),
    ] = False,
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
