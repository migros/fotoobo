"""
FortiGate get version utility
"""

import logging
from typing import Optional

from rich.progress import track

from fotoobo.exceptions import GeneralError, GeneralWarning
from fotoobo.helpers.result import Result
from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def version(host: Optional[str] = None) -> Result[str]:
    """
    FortiGate get version

    Args:
        host (str): the host from the inventory to get the version. If you omit host, it will
                    run over all FortiGates in the inventory.
    """
    inventory = Inventory(config.inventory_file)
    fgts = inventory.get(host, "fortigate")

    result = Result[str]()
    for name, fgt in track(fgts.items(), description="getting FortiGate versions..."):
        log.debug("getting FortiGate version for %s", name)
        try:
            fortigate_version = fgt.get_version()
        except (GeneralWarning, GeneralError) as exception:
            fortigate_version = f"unknown due to {exception.message}"

        result.push_result(name, fortigate_version)

    return result
