"""
FortiClient EMS get module
"""
import logging
from typing import Dict, List

from fotoobo.fortinet.forticlientems import FortiClientEMS
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def version(host: str) -> Result[str]:
    """
    ems get version

    Args:
        host (str): host defined in inventory

    Returns:
        Result[Dict[str, str]]: version data in a dict with keys: host, version
    """
    result = Result[str]()

    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get_item(host, "forticlientems")
    log.debug("FortiClient EMS get version ...")
    ems.login()
    ems_version = ems.get_version()

    result.push_result(host, f"v{ems_version}")

    return result


def workgroups(host: str, custom: bool = False) -> Result[List[Dict[str, str]]]:
    """
    ems get workgroups

    Args:
        host (str): host defined in inventory
        custom (bool): if true it only returns custom groups

    Returns:
        List[Dict[str, str]]: workgroups data in a list of dict with keys: name, id, total_devices
    """
    result = Result[List[Dict[str, str]]]()

    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get_item(host, "forticlientems")

    log.debug("FortiClient EMS get workgroups ...")
    ems.login()

    raw_data = ems.api("get", f"/workgroups/index?custom={custom}").json()["data"]
    for entry in raw_data:
        result.push_result(entry["name"], entry["total_devices"])

    return result
