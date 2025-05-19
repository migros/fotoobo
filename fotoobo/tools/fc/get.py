"""
FortiCloud get utility
"""

import logging
from typing import Any

from fotoobo.fortinet.forticloud import FortiCloudAsset
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def products(host: str) -> Result[Any]:
    """
    Return the assets from Asset management in FortiCloud"""
    result = Result[Any]()
    inventory = Inventory(config.inventory_file)
    fc: FortiCloudAsset = inventory.get_item(host, "forticloud")
    log.debug("FortiCloud get assets ...")
    response = fc.post("/products/list", payload={"serialNumber": "%"})

    if "error" in response and response["error"]:
        result.push_message(host, response["error"]["message"], "error")

    else:
        result.push_result(host, response["assets"])

    return result


def version(host: str) -> Result[str]:
    """
    FortiCloud API get version

    Args:
        host: Host defined in inventory

    Returns:
        The version string for the FortiCloud API
    """
    result = Result[str]()
    inventory = Inventory(config.inventory_file)
    fc: FortiCloudAsset = inventory.get_item(host, "forticloud")
    log.debug("FortiCloud get version ...")
    result.push_result(host, fc.get_version())

    return result
