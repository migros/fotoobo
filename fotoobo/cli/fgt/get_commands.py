"""
The FortiGate get commands
"""
# pylint: disable=anomalous-backslash-in-string

import logging

import typer

from fotoobo.helpers import cli_path
from fotoobo.tools import fgt

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
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
        help="The FortiGate hostname to access (must be defined in the inventory). "
        "\[default: <all>]",
        show_default=False,
        metavar="[host]",
    )
) -> None:
    """
    Get the FortiGate(s) version(s).

    The optional argument [host] makes this command somewhat magic. If you omit \[host] it searches
    for all devices of type 'fortigate' in the inventory and tries to get their FortiOS version.
    """
    result = fgt.get.version(host)
    result.print_result_as_table(title="FortiGate Versions", headers=["FortiGate", "Version"])
