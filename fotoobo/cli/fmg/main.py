"""
The FortiManager commands
"""
import logging

import typer

from fotoobo.cli.fmg import get_commands as get
from fotoobo.helpers import cli_path
from fotoobo.utils import fmg

app = typer.Typer()
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fmg subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command()
def assign(
    host: str = typer.Argument(
        "fmg",
        help="The FortiManager hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
    adoms: str = typer.Argument(
        ...,
        help="The ADOMs to assign the global policy/objects. Use 'fmg get adoms' to get a list of "
        + "available ADOMs. Separate multiple ADOMs by comma (no spaces)",
        metavar="[adoms]",
        show_default=False,
    ),
    timeout: int = typer.Option(
        60,
        "--timeout",
        "-t",
        help="The timeout to wait for the FortiManager task to finish",
        metavar="[timeout]",
    ),
) -> None:
    """
    Assign a global policy to a specified ADOM or to a list of ADOMs
    """
    fmg.assign(host, adoms, timeout=timeout)


@app.command()
def set(  # pylint: disable=redefined-builtin
    host: str = typer.Argument(
        ...,
        help="The FortiManager hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
    file: str = typer.Argument(
        ..., help="json file with payload(s)", show_default=False, metavar="[file]"
    ),
    adom: str = typer.Argument(..., help="The ADOM to issue the set command(s)", metavar="[adom]"),
) -> None:
    """FortiManager set command"""
    fmg.set(host, file, adom)


app.add_typer(get.app, name="get", help="FortiManager get commands")
