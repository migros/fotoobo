"""
FortiClient EMS get module
"""

import logging

from fotoobo.fortinet.forticlientems import FortiClientEMS
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def version(host: str) -> Result[str]:
    """
    ems get version

    Args:
        host: Host defined in inventory

    Returns:
        Version data in a Result object
    """
    result = Result[str]()
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get_item(host, "forticlientems")
    log.debug("FortiClient EMS get version ...")
    ems.login()
    ems_version = ems.get_version()
    result.push_result(host, f"v{ems_version}")

    return result


def workgroups(host: str, custom: bool = False) -> Result[dict[str, str]]:
    """
    ems get workgroups

    Args:
        host:   Host defined in inventory
        custom: If true it only returns custom groups

    Returns:
        Workgroups data in a Results object with keys: id, total_devices
    """
    result = Result[dict[str, str]]()
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get_item(host, "forticlientems")
    log.debug("FortiClient EMS get workgroups ...")
    ems.login()
    raw_data = ems.api("get", f"/workgroups/index?custom={custom}").json()["data"]
    for entry in raw_data:
        result.push_result(entry["name"], {"id": entry["id"], "count": entry["total_devices"]})

    return result
