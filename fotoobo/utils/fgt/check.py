"""
FortiGate check hamaster utility
"""

import logging
from typing import Dict, List, Optional

from pysnmp.hlapi import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    getCmd,
)
from rich.progress import track

from fotoobo.exceptions import GeneralError
from fotoobo.helpers.config import config
from fotoobo.helpers.output import Output
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def _snmp_get(  # pylint: disable=too-many-arguments
    oid: str, hostname: str, community: str, version: int = 2, timeout: int = 2, retries: int = 2
) -> str:
    """
    Get a single SNMPv2 value from a given OID

    Args:
        hostname (str): Host to send the SNMP query to
        community (str): SNMP community string
        version (int, optional): SNMP version. Set it to 2 for SNMPv2c. All other values will result
            in SNMP version 1. Defaults to 2.
        timeout (int, optional): Query timeout in seconds. Defaults to 2.
        retries (int, optional): Retries. Defaults to 2.

    Raises:
        GeneralError: Any SNMP error ocurred

    Returns:
        str: _description_
    """
    mp_model = 1 if version == 2 else 0
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=mp_model),
        UdpTransportTarget((hostname, 161), timeout, retries),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )

    error_indication, error_status, error_index, var_binds = next(iterator)

    if error_indication:
        log.debug("SNMP error: %s at %s", error_indication, error_index)
        raise GeneralError(f"SNMP error: {error_indication}")

    if error_status:
        log.debug("SNMP error: %s", error_status)
        raise GeneralError(f"SNMP error: {error_status}")

    for var_bind in var_binds:

        value: str = var_bind.prettyPrint()

        if "=" in value:
            value = value.split("=")[-1].strip()

        else:
            raise GeneralError(f"SNMP value not found in {value}")

    return value


def hamaster(  # pylint: disable=too-many-locals
    host: str, smtp_server: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    FortiGate check hamaster

    Args:
        host (str):  the FortiManager host from the inventory to get the device list from. If you
                     omit host, it will run over the default FortiManager (fmg).
        smtp_server: the SMTP server from the inventory to send mail messages if errors occur
    """
    inventory = Inventory(config.inventory_file)
    fmg = inventory.get(host, "fortimanager")[host]

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
    fmg.login()
    response = fmg.api("post", payload=payload)
    fmg.logout()
    firewalls = []

    for device in response.json()["result"][0]["data"]:
        if device["ha_mode"] == 1:
            expect = ""
            highest = 0
            for node in device["ha_slave"]:
                if node["prio"] > highest:
                    highest = node["prio"]
                    expect = node["name"]
            firewalls.append({"name": device["name"], "ip": device["ip"], "expect": expect})

    data = []
    output = Output()

    for firewall in track(firewalls, description="getting HA info ..."):
        master_status: str = "unknown"

        try:
            ha_master = _snmp_get(
                "iso.3.6.1.4.1.12356.101.13.2.1.1.11.1",
                hostname=firewall["ip"],
                community=config.snmp_community,
                version=2,
                timeout=1,
                retries=3,
            )

            if ha_master == firewall["expect"]:
                master_status = "OK"

            else:
                master_status = "not OK"
                output.add(
                    f"{firewall['name']} HA-Status NOT OK - expect: {firewall['expect']}"
                    + f" got: {ha_master}"
                )

        except GeneralError as err:
            log.error("%s returned an error: %s", firewall["name"], err)
            output.add(f"{firewall['name']} returned an error: {err}")

        data.append({"name": firewall["name"], "status": master_status})

    if smtp_server:
        if smtp_server in inventory.assets:
            output.send_mail(inventory.assets[smtp_server])

    return data
