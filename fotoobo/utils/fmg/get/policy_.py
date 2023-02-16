"""
FortiManager get policy utility
"""
import logging
from typing import Any, List, Optional

from fotoobo.exceptions import GeneralError
from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


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
