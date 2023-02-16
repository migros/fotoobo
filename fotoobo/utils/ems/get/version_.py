"""
FortiClient EMS get version utility
"""
import logging
from typing import Dict

from fotoobo.fortinet.forticlientems import FortiClientEMS
from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def version(host: str) -> Dict[str, str]:
    """
    ems get version

    Args:
        host (str): host defined in inventory

    Returns:
        Dict[str, str]: version data in a dict with keys: host, version
    """
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get(host, "forticlientems")[host]
    log.debug("FortiClient EMS get version ...")
    ems.login()
    ems_version = ems.get_version()

    return {"host": host, "version": ems_version}
