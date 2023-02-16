"""
FortiManager get devices utility
"""

import logging
from typing import Dict, List

from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def devices(host: str) -> List[Dict[str, str]]:
    """
    FortiManager get logical devices
    In a cluster only the cluster device is returned, not the physical nodes

    Args:
        host (str): the FortiManager from the inventory to get the Fortinet devices list from

    Returns:
        list of dict: list of devices where
    """
    inventory = Inventory(config.inventory_file)
    fmg = inventory.get(host, "fortimanager")[host]
    log.debug("FortiManager get devices ...")
    fmg.login()
    payload = {
        "method": "get",
        "params": [
            {
                "loadsub": 1,
                "sortings": [{"build": 1}],
                "option": "object member",
                "url": "/dvmdb/device",
            }
        ],
    }
    response = fmg.api("post", payload=payload)
    fmg.logout()
    device_list = []
    for device in response.json()["result"][0]["data"]:
        device_list.append(
            {
                "name": device["name"],
                "version": f"{device['os_ver']}.{device['mr']}.{device['patch']}",
                "ha_mode": str(device["ha_mode"]),
                "platform": device["platform_str"],
                "desc": device["desc"],
            }
        )

    return device_list
