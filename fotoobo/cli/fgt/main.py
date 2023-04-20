"""
The FortiGate commands
"""
import logging

import typer

from fotoobo import tools
from fotoobo.cli.fgt import monitor_commands as monitor
from fotoobo.cli.fgt import config_commands as config
from fotoobo.cli.fgt import get_commands as get
from fotoobo.helpers import cli_path

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
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


app.add_typer(get.app, name="get", help="FortiGate get commands.")
app.add_typer(monitor.app, name="monitor", help="FortiGate monitor commands.")
app.add_typer(config.app, name="config", help="FortiGate config file commands.")


@app.command()
def backup(
    host: str = typer.Argument(
        "",
        help="The FortiGate to backup (must be defined in the inventory). "
        "Backups all if left empty.",
        show_default=False,
        metavar="[host]",
    ),
    backup_dir: str = typer.Option(
        None,
        "--backup-dir",
        "-b",
        help="The directory to save the backup(s) to. Default is the current working directory.",
        show_default=False,
        metavar="backup_dir",
    ),
    ftp_server: str = typer.Option(
        None,
        "--ftp",
        "-f",
        help="The ftp configuration from the inventory to send the backup to.",
        metavar="server",
    ),
    smtp_server: str = typer.Option(
        None,
        "--smtp",
        "-s",
        help="The smtp configuration from the inventory to send potential errors to.",
        metavar="server",
    ),
) -> None:
    """
    Backup one or more FortiGate(s).
    """
    tools.fgt.backup(host, backup_dir, ftp_server, smtp_server)
