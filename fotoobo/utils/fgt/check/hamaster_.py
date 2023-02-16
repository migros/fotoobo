"""
FortiGate check hamaster utility
"""

import logging
from typing import Dict, List, Optional

from easysnmp import snmp_get
from easysnmp.exceptions import EasySNMPTimeoutError
from rich.progress import track

from fotoobo.exceptions import GeneralError
from fotoobo.helpers.config import config
from fotoobo.helpers.output import Output
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


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
            master = snmp_get(  # pylint: disable=E1101
                "iso.3.6.1.4.1.12356.101.13.2.1.1.11.1",
                hostname=firewall["ip"],
                community=config.snmp_community,
                version=2,
                timeout=1,
                retries=3,
            ).value

            if master == "NOSUCHINSTANCE":
                raise GeneralError("no such instance")

            if master == firewall["expect"]:
                master_status = "OK"

            else:
                master_status = "not OK"
                output.add(
                    f"{firewall['name']} HA-Status NOT OK - expect: {firewall['expect']}"
                    + f" got: {master}"
                )

        except (EasySNMPTimeoutError, GeneralError) as err:
            log.error("%s returned an error: %s", firewall["name"], err)
            output.add(f"{firewall['name']} returned an error: {err}")

        data.append({"name": firewall["name"], "status": master_status})

    if smtp_server:
        if smtp_server in inventory.assets:
            output.send_mail(inventory.assets[smtp_server])

    return data
