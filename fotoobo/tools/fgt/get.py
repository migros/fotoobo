"""
FortiGate get version utility
"""

import concurrent.futures
import logging
from typing import Optional, Tuple

from rich.progress import Progress

from fotoobo.exceptions import GeneralError, GeneralWarning
from fotoobo.fortinet.fortigate import FortiGate
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def version(host: Optional[str] = None) -> Result[str]:
    """FortiGate get version.

    Get the version(s) of one ore more FortiGates.

    Args:
        host:   The host from the inventory to get the version. If you omit host, it will run over
                all FortiGates in the inventory.

    Returns:
        The Result object with all the results
    """

    def _get_single_version(name: str, fgt: FortiGate) -> Tuple[str, str]:
        """Get the version from a FortiGate.

        This private method is used for multithreading. It only queries one single FortiGate for its
        version number status and returns it.

        Args:
            name:   The name of the FortiGate (as defined in the inventory)
            fgt:    The FortiGate object to query

        Returns:
            name:   The name of the FortiGate (as defined in the inventory)
            status: The HA status of the FortiGate (fgt)
        """
        log.debug("getting FortiGate version for %s", name)
        try:
            fortigate_version = fgt.get_version()
        except (GeneralWarning, GeneralError) as exception:
            fortigate_version = f"unknown due to {exception.message}"

        return name, fortigate_version

    inventory = Inventory(config.inventory_file)
    fgts = inventory.get(host, "fortigate")

    result = Result[str]()

    with Progress() as progress:
        task = progress.add_task("getting FortiGate versions...", total=len(fgts))
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for name, fgt in fgts.items():
                futures.append(executor.submit(_get_single_version, name, fgt))

            for future in concurrent.futures.as_completed(futures):
                name, fortigate_version = future.result()
                result.push_result(name, fortigate_version)
                progress.update(task, advance=1)

    return result
