"""
FortiGate backup utility
"""
import json
import logging
from typing import Union

from fotoobo.exceptions import APIError, GeneralError
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def backup(
    host: Union[str, None] = None,
) -> Result[str]:
    """
    Create a FortiGate configuration backup into a file and optionally upload it to an FTP server.

    Args:
        host (str):         The host from the inventory to get the backup. If no host is given all
                            FortiGate devices in the inventory are backed up.
        backup_dir (Path):   The directory to save tha backup(s) to
        ftp_server (str):   The FTP server from the inventory to upload the backup to. You may omit
                            this argument to only safe the backup to a file. This argument also
                            compresses the configuration file into a zip file.
        smtp_server (str):  The SMTP server from the inventory to send mail messages if errors occur
    """
    result = Result[str]()

    inventory = Inventory(config.inventory_file)
    fortigates = inventory.get(host, "fortigate")

    # backup every FortiGate
    for name, fgt in fortigates.items():
        log.debug("backup FortiGate '%s'", name)

        try:
            data: str = fgt.backup()

            result.push_result(name, data)

        except GeneralError as err:
            result.push_message(name, err.message, level="error")
            continue

        except APIError as err:
            result.push_message(name, f"{name} returned {err.message}", level="error")
            continue

        if data.startswith("#config-version"):
            success_message = f"config backup for '{name}' succeeded"
            log.info(success_message)
            result.push_message(name, success_message)

        else:
            data_json = json.loads(data)
            error_str = f"backup '{name}' failed with error '{data_json['http_status']}'"
            log.error(error_str)
            result.push_message(name, error_str, level="error")
            continue

    return result
