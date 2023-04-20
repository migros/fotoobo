"""
FortiClient EMS monitor module
"""

import logging
from datetime import datetime
from typing import Any, Dict

from fotoobo.fortinet.forticlientems import FortiClientEMS
from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def connections(host: str) -> Dict[Any, Any]:
    """
    Get connections information from FortiClient EMS.

    The data returned is the raw data part from the EMS response. Additionally the data is enriched
    with calculated and interesting values. All the enriched values are in the "fotoobo" in the
    returned dict.

    Args:
        host (str): FortiClient EMS host defined in the inventory

    Returns: Dict[str, Any]
    """
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get(host, "forticlientems")[host]
    ems.login()
    response = ems.api("get", "/endpoints/connection/donut")
    data: Dict[str, Any] = {}
    data["data"] = list(response.json()["data"])

    data["fotoobo"] = {}
    for item in data["data"]:
        data["fotoobo"][item["token"]] = item["value"]

    return data


def endpoint_management_status(host: str) -> Dict[str, Any]:
    """
    Get management information about endpoints registered in FortiClient EMS.

    The data returned is the raw data part from the EMS response. Additionally the data is enriched
    with calculated and interesting values. All the enriched values are in the key "fotoobo" in the
    returned dict:

        - {{ fotoobo.managed }}     Amount of managed endpoints
        - {{ fotoobo.unmanaged }}   Amount of unmanaged endpoints

    Args:
        host (str): FortiClient EMS host defined in the inventory

    Returns: Dict[str, Any]
    """
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get(host, "forticlientems")[host]
    ems.login()

    response = ems.api("get", "/endpoints/management/donut")

    data = {}
    data["data"] = dict(response.json())["data"]

    managed = unmanaged = 0
    for item in data["data"]:
        if item["token"] == "managed":
            managed = item["value"]
            log.debug("management: managed: %s", managed)

        if item["token"] == "unmanaged":
            unmanaged = item["value"]
            log.debug("management: unmanaged: %s", unmanaged)

    data["fotoobo"] = {"managed": managed, "unmanaged": unmanaged}
    return data


def endpoint_online_outofsync(host: str) -> Dict[str, Any]:
    """
    Get amount of FortiClient EMS devices which are online but policy not in sync.

    The data returned is a dict with a key "fotoobo" with the relevant data. In this utility only
    one key value pair is present.

        - {{ fotoobo.outofsync }}   Amount of managed endpoints which are online but their policy
            is not in synch with FortiClient EMS

    Args:
        host (str): FortiClient EMS host defined in the inventory

    Returns: Dict[str, Any]
    """
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get(host, "forticlientems")[host]
    ems.login()

    response = ems.api(
        "get", "/endpoints/index?offset=0&count=1&connection=online&status=outofsync"
    )

    data = {"fotoobo": {"outofsync": response.json()["data"]["total"]}}
    log.debug("endpoints outofsync: %s", data["fotoobo"]["outofsync"])

    return data


def endpoint_os_versions(host: str) -> Dict[str, Any]:
    """
    Get management information about endpoints registered in FortiClient EMS.

    The data returned is the raw data part from the EMS response. Additionally the data is enriched
    with calculated and interesting values. All the enriched values are in the key "fotoobo" in the
    returned dict:

        - {{ fotoobo.fctversionlinux }}     Amount of managed linux endpoints
        - {{ fotoobo.fctversionmac }}       Amount of managed mac endpoints
        - {{ fotoobo.fctversionwindows }}   Amount of managed windows endpoints

    Args:
        host (str): FortiClient EMS host defined in the inventory

    Returns: Dict[str, Any]
    """
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get(host, "forticlientems")[host]
    ems.login()

    data: Dict[str, Any] = {}
    data["data"] = {}
    data["fotoobo"] = {}

    for fctversion_os in ["fctversionwindows", "fctversionmac", "fctversionlinux"]:
        response = ems.api("get", f"/endpoints/{fctversion_os}/donut")
        data["data"][fctversion_os] = dict(response.json())["data"]
        count = sum(item["value"] for item in data["data"][fctversion_os])
        data["fotoobo"][fctversion_os] = count

    return data


def system(host: str) -> Dict[str, Any]:
    """
    Get system information from FortiClient EMS.

    Args:
        host (str): FortiClient EMS host defined in inventory

    Returns: Dict[str, Any]
    """
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get(host, "forticlientems")[host]
    ems.login()

    # get EMS serial number (just for debug logging and because it's possible)
    response = ems.api("get", "/system/serial_number")
    log.debug("serial number: %s (from /system/serial_number)", response.json()["data"])

    # get EMS system info
    response = ems.api("get", "/system/info/")
    log.debug("serial number: %s (from /system/info/)", response.json()["data"]["license"]["sn"])

    return dict(response.json()["data"])


def license(host: str) -> Dict[str, Any]:  # pylint: disable=redefined-builtin
    """
    Get license information from FortiClient EMS.

    The data returned is the raw data part from the EMS response. Additionally the data is enriched
    with calculated and interesting values. All the enriched values are in the key "fotoobo" in the
    returned dict:

        - {{ fotoobo.[MODULE]_usage }}          License usage in percent by MODULE where MODULE is
            one of:
                - fabric_agent
                - ztna
                - epp
                - sandbox_cloud
                - chromebook
                - sase
                - ztna_user
                - epp_user
                - sase_user
                - vpn_only
        - {{ fotoobo.license_expiry_days }}     Days until your FortiClient EMS license expires.
            Be aware that it only shows the expiry of the "fabric_agent" fabric_agent as for now.
            If you wish mor granular view this utility has to be improved accordingly.

    Args:
        host (str): FortiClient EMS host defined in the inventory

    Returns: Dict[str, Any]
    """
    inventory = Inventory(config.inventory_file)
    ems: FortiClientEMS = inventory.get(host, "forticlientems")[host]
    ems.login()
    response = ems.api("get", "/license/get")
    data = dict(response.json()["data"])

    for lic in data["licenses"]:

        if lic["type"] == "fabric_agent":
            log.debug("license expiry: %s", lic["expiry_date"])
            license_expiry = datetime.strptime(lic["expiry_date"], "%Y-%m-%dT%H:%M:%S")
            license_expiry_days = int((license_expiry - datetime.now()).days)
            log.debug("days to license expiry: %s", license_expiry_days)

    data["fotoobo"] = {}
    data["fotoobo"]["license_expiry_days"] = license_expiry_days
    for key in data["seats"]:
        if data["seats"][key] > 0:
            log.debug(f"{key} license count: %s", data["seats"][key])
            log.debug(f"{key} license used: %s", data["used"][key])
            license_usage = int(100 / data["seats"][key] * data["used"][key])
            log.debug(f"{key} license usage : %s%%", license_usage)
            data["fotoobo"][key + "_usage"] = license_usage

    return data
