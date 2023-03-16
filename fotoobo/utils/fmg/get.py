"""
FortiManager get ADOMs utility
"""

import logging
from typing import Any, Dict, List, Optional

from fotoobo.exceptions.exceptions import GeneralError
from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def adoms(host: str) -> List[Dict[str, str]]:
    """
    FortiManager get ADOMs

    Args:
        host (str): the host from the inventory to get the ADOMs list from

    Returns:
        list of dict: list of ADOMs where ADOM is a dict with keys: name, version
    """
    inventory = Inventory(config.inventory_file)
    fmg = inventory.get(host, "fortimanager")[host]
    adom_list = []
    log.debug("FortiManager get adoms ...")
    fmg.login()
    fmg_adoms = fmg.get_adoms()
    for adom in fmg_adoms:
        adom_list.append({"name": adom["name"], "version": f"{adom['os_ver']}.{adom['mr']}"})

    fmg.logout()
    return adom_list


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


def policy(host: str, adom: str, policy_name: str, fields: Optional[List[str]] = None) -> List[Any]:
    """
    FortiManager get policy
    """
    fields = fields or [
        "status",
        # "_last_hit",  # data-format not clear
        "global-label",
        # "_hitcount",  # data-format not clear (it's not equal to the value in FortiManager)
        "policyid",
        "srcaddr",
        "groups",
        "dstaddr",
        "service",
        "action",
        "send-deny-packet",
        "comments",
    ]
    inventory = Inventory(config.inventory_file)
    fmg = inventory.get(host, "fortimanager")[host]
    log.debug("FortiManager get policy '%s' from '%s' ...", policy_name, adom)
    fmg.login()
    payload = {
        "method": "get",
        "params": [
            {
                "option": "object member",
                "url": f"/pm/config/adom/{adom}/pkg/{policy_name}/firewall/policy",
            }
        ],
        "session": "",
        "id": 1,
    }
    result = fmg.api("post", payload=payload, timeout=30)
    data = result.json()

    if data["result"][0]["status"]["code"] != 0:
        code = data["result"][0]["status"]["code"]
        message = data["result"][0]["status"]["message"]
        log.error("FortiManager '%s' returned '%s': '%s'", host, code, message)
        raise GeneralError(f"FortiManager {host} returned {code}: {message}")

    policies = []
    for pol in data["result"][0]["data"]:
        policies.append({field: pol.get(field, None) for field in fields})

    fmg.logout()
    return policies


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
