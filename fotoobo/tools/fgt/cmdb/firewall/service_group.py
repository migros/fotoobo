"""FortiGate CMDB firewall service group module"""

from pathlib import Path
from typing import Any, Optional

from fotoobo.fortinet.fortigate import FortiGate
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory


def get_cmdb_firewall_service_group(
    host: str, name: str, vdom: str, output_file: Optional[str]
) -> Result[list[Any]]:
    """Get the firewall service group object(s)

    The FortiGate api endpoint is: /cmdb/firewall.service/group
    """
    inventory = Inventory(config.inventory_file)
    fgt: FortiGate = inventory.get_item(host, "fortigate")
    result = Result[list[Any]]()

    service_group_list = fgt.api_get(url=f"/cmdb/firewall/addrgrp/{name}", vdom=vdom)

    if output_file:
        result.push_result(key=host, data=service_group_list)
        result.save_raw(file=Path(output_file), key=host)

    assets = []
    if service_group_list:
        for vd in service_group_list:
            for asset in vd["results"]:
                data: dict[str, str] = {
                    "name": asset["name"],
                    "vdom": vd["vdom"],
                    "content": "\n".join(_["name"] for _ in asset["member"]),
                }

                assets.append(data)

    result.push_result(host, assets)

    return result
