"""
The FortiGate commands
"""

import logging
from typing import Optional

import typer
from typing_extensions import Annotated

from fotoobo.helpers import cli_path
from fotoobo.tools import fgt

from .cmdb import cmdb

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


app.add_typer(cmdb.app, name="cmdb", help="FortiGate get cmdb commands.")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fgt get subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)


@app.command()
def version(
    host: Annotated[
        Optional[str],
        typer.Argument(
            help="The FortiGate hostname to access (must be defined in the inventory). ",
            metavar="[host]",
        ),
    ] = None,
) -> None:
    """
    Get the FortiGate(s) version(s).

    The optional argument \\[host] makes this command somewhat magic. If you omit \\[host] it
    searches for all devices of type 'fortigate' in the inventory and tries to get their FortiOS
    version.
    """
    result = fgt.get.version(host)
    result.print_result_as_table(title="FortiGate Versions", headers=["FortiGate", "Version"])
