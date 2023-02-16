"""
FortiClient EMS get workgroups utility
"""
import logging
from typing import Dict, List

from fotoobo.fortinet.forticlientems import FortiClientEMS
from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


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
