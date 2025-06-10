"""
FortiCloud cloud asset get utility
"""

import logging
from typing import Any

from fotoobo.fortinet.forticloudasset import FortiCloudAsset
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def products(host: str) -> Result[list[dict[str, Any]]]:
    """
    FortiCloud API get products from Asset Management

    Here we assume that just one page is returned. If it happens that more that one page is returned
    pagination has to be implemented.

    Args:
        host: Host defined in inventory

    Returns:
        The asset list as a result object
    """
    result = Result[list[dict[str, Any]]]()
    inventory = Inventory(config.inventory_file)
    fc: FortiCloudAsset = inventory.get_item(host, "forticloudasset")
    log.debug("FortiCloud get assets ...")
    response = fc.post("/products/list", payload={"serialNumber": "%"})
    if response["error"]:
        result.push_message(host, response["message"], "info")

    else:
        result.push_result(host, response["assets"])

    return result


def version(host: str) -> Result[str]:
    """
    FortiCloud API get version

    Args:
        host: Host defined in inventory

    Returns:
        The version string for the FortiCloud API in a result object
    """
    result = Result[str]()
    inventory = Inventory(config.inventory_file)
    fcasset: FortiCloudAsset = inventory.get_item(host, "forticloudasset")
    log.debug("FortiCloud Asset Management get version ...")
    result.push_result(host, fcasset.get_version())

    return result
