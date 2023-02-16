"""
FortiManager get version utility
"""

import logging
from typing import Dict

from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def version(host: str) -> Dict[str, str]:
    """
    FortiManager get version

    Args:
        host (str): the host from the inventory to get the version

    Returns:
        Dict[str, str]: version data in a dict with keys: host, version
    """
    inventory = Inventory(config.inventory_file)
    fmg = inventory.get(host, "fortimanager")[host]
    log.debug("FortiManager get version ...")
    fmg.login()
    fmg_version = fmg.get_version()
    fmg.logout()

    return {"host": host, "version": fmg_version}
