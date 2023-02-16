"""
The FortiGate commands
"""
import logging

import typer

from fotoobo import utils
from fotoobo.cli.fgt import check_commands as check
from fotoobo.cli.fgt import get_commands as get
from fotoobo.helpers import cli_path

app = typer.Typer()
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fgt subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


app.add_typer(get.app, name="get", help="FortiGate get commands")
app.add_typer(check.app, name="check", help="FortiGate check commands")


@app.command()
def backup(
    host: str = typer.Argument(
        "",
        help="The FortiGate hostname to access (must be defined in inventory)",
        show_default=False,
        metavar="[host]",
    ),
    ftp_server: str = typer.Option(
        None, "--ftp", help="the ftp configuration from the inventory", metavar="server"
    ),
    smtp_server: str = typer.Option(
        None, "--smtp", help="the smtp configuration from the inventory", metavar="server"
    ),
) -> None:
    """
    Backup one or more FortiGate(s)
    """
    utils.fgt.backup(host, ftp_server, smtp_server)


@app.command()
def confcheck(
    configuration: str = typer.Argument(
        ..., help="The FortiGate configuration file or directory", metavar="[config]"
    ),
    bundles: str = typer.Argument(
        ..., help="Filename of the file containing the check bundles", metavar="[bundles]"
    ),
) -> None:
    """
    Check one or more FortiGate configuration files
    """
    utils.fgt_confcheck(configuration, bundles)
