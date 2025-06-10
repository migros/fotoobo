"""
The FortiManager commands
"""

import logging
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from fotoobo.helpers import cli_path
from fotoobo.helpers.config import config as fotoobo_config
from fotoobo.inventory import Inventory
from fotoobo.tools import fmg

from . import get

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fmg subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)


@app.command(no_args_is_help=True)
def assign(
    adoms: Annotated[
        str,
        typer.Argument(
            help="The ADOMs to assign the global policy/objects to. Use 'fotoobo fmg get adoms' to "
            "get a list of available ADOMs. Separate multiple ADOMs by comma (no spaces).",
            metavar="[adoms]",
            show_default=False,
        ),
    ],
    policy: Annotated[
        str,
        typer.Argument(
            help="The global policy to assign",
            metavar="[policy]",
            show_default=False,
        ),
    ],
    host: Annotated[
        str,
        typer.Argument(
            help="The FortiManager to access (must be defined in the inventory).",
            metavar="[host]",
        ),
    ] = "fmg",
    smtp_server: Annotated[
        Optional[str],
        typer.Option(
            "--smtp",
            "-s",
            help="The smtp configuration from the inventory to send potential errors to.",
            metavar="[server]",
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout",
            "-t",
            help="The timeout to wait for the FortiManager task to finish.",
            metavar="[timeout]",
        ),
    ] = 60,
) -> None:
    """
    Assign a global policy to a specified ADOM or to a list of ADOMs.
    """
    inventory = Inventory(fotoobo_config.inventory_file)
    result = fmg.assign(adoms=adoms, policy=policy, host=host, timeout=timeout)

    if smtp_server:
        if smtp_server in inventory.assets:
            result.send_messages_as_mail(inventory.assets[smtp_server], "error")

        else:
            log.warning("SMTP server '%s' not in found in inventory.", smtp_server)


@app.command(no_args_is_help=True)
def post(
    file: Annotated[
        Path,
        typer.Argument(help="JSON file with payload(s).", show_default=False, metavar="[file]"),
    ],
    adom: Annotated[
        str,
        typer.Argument(
            help="The ADOM to issue the set command(s).", metavar="[adom]", show_default=False
        ),
    ],
    host: Annotated[
        str,
        typer.Argument(
            help="The FortiManager to access (must be defined in the inventory).",
            metavar="[host]",
        ),
    ] = "fmg",
    smtp_server: Annotated[
        Optional[str],
        typer.Option(
            "--smtp",
            "-s",
            help="The smtp configuration from the inventory to send potential errors to.",
            metavar="[server]",
        ),
    ] = None,
) -> None:
    """
    Post any valid JSON request to the FortiManager.

    Configure the FortiManager with any valid API call(s) given within the JSON file.
    """
    inventory = Inventory(fotoobo_config.inventory_file)
    result = fmg.post(file=file, adom=adom, host=host)

    if smtp_server:
        if smtp_server in inventory.assets:
            result.send_messages_as_mail(inventory.assets[smtp_server], "error", command=True)

        else:
            log.warning("SMTP server '%s' not in found in inventory.", smtp_server)


app.add_typer(get.app, name="get", help="FortiManager get commands.")
