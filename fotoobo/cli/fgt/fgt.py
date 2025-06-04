"""
The FortiGate commands
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from fotoobo import tools
from fotoobo.exceptions import GeneralWarning
from fotoobo.helpers import cli_path
from fotoobo.helpers.config import config as fotoobo_config
from fotoobo.helpers.files import create_dir, file_to_ftp, file_to_zip
from fotoobo.inventory import Inventory

from . import config, monitor
from .get import get

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


app.add_typer(config.app, name="config", help="FortiGate config file commands.")
app.add_typer(get.app, name="get", help="FortiGate get commands.")
app.add_typer(monitor.app, name="monitor", help="FortiGate monitor commands.")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fgt subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)


@app.command()
def backup(
    host: Annotated[
        str,
        typer.Argument(
            help="The FortiGate to backup (must be defined in the inventory). "
            "Backups all if left empty.",
            show_default=False,
            metavar="[host]",
        ),
    ] = "",
    backup_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--backup-dir",
            "-b",
            help="Directory to save the backup(s) to. Default is the current working directory.",
            show_default=False,
            metavar="backup_dir",
        ),
    ] = None,
    ftp_server: Annotated[
        Optional[str],
        typer.Option(
            "--ftp",
            "-f",
            help="The ftp configuration from the inventory to send the backup to.",
            metavar="server",
        ),
    ] = None,
    smtp_server: Annotated[
        Optional[str],
        typer.Option(
            "--smtp",
            "-s",
            help="The smtp configuration from the inventory to send potential errors to.",
            metavar="server",
        ),
    ] = None,
) -> None:
    """
    Backup one or more FortiGate(s).
    """
    inventory = Inventory(fotoobo_config.inventory_file)

    if not backup_dir:
        backup_dir = Path.cwd()

    create_dir(backup_dir)
    result = tools.fgt.backup(host)

    for name, data in result.all_results().items():
        config_file = backup_dir / Path(name).with_suffix(".conf")

        if config_file.is_file():
            os.remove(config_file)

        config_file.write_text(data, encoding="UTF-8")

        if not config_file.is_file():
            result.push_message(name, f"backup file for '{name}' does not exist")
            continue

        if ftp_server:
            if ftp_server in inventory.assets:
                server = inventory.assets[ftp_server]
                log.debug("Compressing configuration '%s'", name)
                time: str = datetime.now().strftime("%Y%m%d-%H%M")
                zip_file = backup_dir / Path(name + "-" + time + ".conf.zip")
                file_to_zip(config_file, zip_file)
                file_to_ftp(zip_file, server)
                os.remove(zip_file)
                result.push_message(name, f"Uploaded config file for '{name}' to '{ftp_server}'")

            else:
                raise GeneralWarning(f"FTP server '{ftp_server}' not found in inventory")

    if smtp_server and smtp_server in inventory.assets:
        result.send_messages_as_mail(inventory.assets[smtp_server], "error")
