"""
The FortiGate commands
"""
import logging
import os
from datetime import datetime
from pathlib import Path

import typer

from fotoobo import tools
from fotoobo.cli.fgt import monitor_commands as monitor
from fotoobo.cli.fgt import config_commands as config
from fotoobo.cli.fgt import get_commands as get
from fotoobo.exceptions import GeneralWarning
from fotoobo.helpers import cli_path
from fotoobo.helpers.files import create_dir, file_to_ftp, file_to_zip
from fotoobo.inventory import Inventory
from fotoobo.helpers.config import config as fotoobo_config

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
    backup_dir: Path = typer.Option(
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
                log.debug("compressing configuration '%s'", name)
                time: str = datetime.now().strftime("%Y%m%d-%H%M")
                zip_file = backup_dir / Path(name + "-" + time + ".conf.zip")
                file_to_zip(config_file, zip_file)
                file_to_ftp(zip_file, server)
                os.remove(zip_file)

                result.push_message(name, f"Uploaded config file for '{name}' to '{ftp_server}'")

            else:
                raise GeneralWarning(f"ftp server '{ftp_server}' not found in inventory")

    if smtp_server and smtp_server in inventory.assets:
        result.send_messages_as_mail(inventory.assets[smtp_server], "error")
