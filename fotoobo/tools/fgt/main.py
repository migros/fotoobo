"""
FortiGate backup utility
"""
import concurrent.futures
import json
import logging
from typing import Tuple, Union

from rich.progress import Progress

from fotoobo.exceptions import APIError, GeneralError
from fotoobo.fortinet.fortigate import FortiGate
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
        host:   The host from the inventory to get the backup. If no host is given all
                FortiGate devices in the inventory are backed up.

    Returns:
        The Result object with all the results
    """
    result = Result[str]()
    inventory = Inventory(config.inventory_file)
    fgts = inventory.get(host, "fortigate")

    def _get_single_backup(name: str, fgt: FortiGate) -> Tuple[str, str]:
        """Get the configuration backup from a single FortiGate.

        This private method is used for multithreading. It only queries one single FortiGate for its
        configuration backup and returns it.

        Args:
            name:   The name of the FortiGate (as defined in the inventory)
            fgt:    The FortiGate object to query

        Returns:
            name:   The name of the FortiGate (as defined in the inventory)
            data:   The configuration backup of the FortiGate (fgt)
        """
        log.debug("backup FortiGate '%s'", name)
        data: str = ""
        try:
            data = fgt.backup()
            if data.startswith("#config-version"):
                message = f"config backup for '{name}' succeeded"
                log.info(message)
                result.push_message(name, message)

            else:
                data_json = json.loads(data)
                message = f"backup '{name}' failed with error '{data_json['http_status']}'"
                log.error(message)
                result.push_message(name, message, level="error")

        except GeneralError as err:
            result.push_message(name, err.message, level="error")

        except APIError as err:
            result.push_message(name, f"{name} returned {err.message}", level="error")

        return name, data

    with Progress() as progress:
        task = progress.add_task("getting FortiGate versions...", total=len(fgts))
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for name, fgt in fgts.items():
                futures.append(executor.submit(_get_single_backup, name, fgt))

            for future in concurrent.futures.as_completed(futures):
                name, configuration_backup = future.result()
                result.push_result(name, configuration_backup)
                progress.update(task, advance=1)

    return result
