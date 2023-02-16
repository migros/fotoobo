"""
FortiGate backup utility
"""
import datetime
import json
import logging
import os
from typing import Optional

from fotoobo.exceptions import APIError, GeneralError, GeneralWarning
from fotoobo.helpers.config import config
from fotoobo.helpers.files import create_dir, file_to_ftp, file_to_zip
from fotoobo.helpers.output import Output
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def backup(  # pylint: disable=too-many-locals, too-many-branches
    host: str, ftp_server: Optional[str] = None, smtp_server: Optional[str] = None
) -> None:
    """
    Create a FortiGate configuration backup into a file and optionally upload it to an FTP server.

    Args:
        host (str):  the host from the inventory to get the backup. If no host is given all
                     FortiGate devices in the inventory are backed up.
        ftp_server:  the FTP server from the inventory to upload the backup to. You may omit this
                     argument to only safe the backup to a file. This argument also compresses
                     the configuration file into a zip file.
        smtp_server: the SMTP server from the inventory to send mail messages if errors occur
    """
    for option in ["backup_dir"]:
        if not getattr(config, option, None):
            raise GeneralError(f"mandatory option '{option}' not set")
    inventory = Inventory(config.inventory_file)
    fgts = inventory.get(host, "fortigate")

    create_dir(config.backup_dir)

    output = Output()

    # backup every FortiGate
    for name, fgt in fgts.items():
        log.debug("backup FortiGate '%s'", name)
        config_file = os.path.join(config.backup_dir, name + ".conf")
        if os.path.isfile(config_file):
            os.remove(config_file)

        try:
            data: str = fgt.backup()
        except GeneralError as err:
            output.add(err.message)
            continue
        except APIError as err:
            output.add(f"{name} returned {err.message}")
            continue

        if data.startswith("#config-version"):
            log.info("backup '%s' succeeded", name)
        else:
            data_json = json.loads(data)
            log.error("backup '%s' failed with error '%s'", name, data_json["http_status"])
            continue

        with open(config_file, "w", encoding="UTF-8") as file:
            file.writelines(data)

        if not os.path.isfile(config_file):
            output.add(f"backup file for '{name}' does not exist")
            continue

        if ftp_server:
            if ftp_server in inventory.assets:
                server = inventory.assets[ftp_server]
                log.debug("compressing configuration '%s'", name)
                time: str = datetime.datetime.now().strftime("%Y%m%d-%H%M")
                zip_file = os.path.join(config.backup_dir, name + "-" + time + ".conf.zip")
                file_to_zip(config_file, zip_file)
                log.debug("FTP transfer for '%s'", name)
                file_to_ftp(zip_file, server)
                os.remove(zip_file)
            else:
                raise GeneralWarning(f"ftp server '{ftp_server}' not found in inventory")

    if smtp_server:
        if smtp_server in inventory.assets:
            output.send_mail(inventory.assets[smtp_server])
