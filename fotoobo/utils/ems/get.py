"""
FortiClient EMS get module
"""
import logging
from typing import Dict, List

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


def workgroups(host: str, custom: bool = False) -> List[Dict[str, str]]:
    """
    ems get workgroups

    Args:
        host (str): host defined in inventory
        custom (bool): if true it only returns custom groups

    Returns:
        List[Dict[str, str]]: workgroups data in a list of dict with keys: name, id, total_devices
    """
    groups = []
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get(host, "forticlientems")[host]
    log.debug("FortiClient EMS get workgroups ...")
    ems.login()
    result = ems.api("get", f"/workgroups/index?custom={custom}").json()["data"]
    for _ in result:
        groups.append({"Name": _["name"], "id": str(_["id"]), "Count": str(_["total_devices"])})

    return groups
