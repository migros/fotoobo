"""FortiGate CMDB firewall addrgrp module"""

from pathlib import Path
from typing import Any, Dict, List

from fotoobo.fortinet.fortigate import FortiGate
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory


def get_cmdb_firewall_addrgrp(
    host: str, name: str, vdom: str, output_file: str
) -> Result[List[Any]]:
    """Get the firewall address group object(s)

    The FortiGate api endpoint is: /cmdb/firewall/addrgrp
    """
    inventory = Inventory(config.inventory_file)
    fgt: FortiGate = inventory.get_item(host, "fortigate")
    result = Result[List[Any]]()

    addrgrp_list = fgt.api_get(url=f"/cmdb/firewall/addrgrp/{name}", vdom=vdom)

    if output_file:
        result.push_result(key=host, data=addrgrp_list)
        result.save_raw(file=Path(output_file), key=host)

    assets = []
    if addrgrp_list:
        for vd in addrgrp_list:
            for asset in vd["results"]:
                # print(asset)
                data: Dict[str, str] = {
                    "name": asset["name"],
                    "vdom": vd["vdom"],
                    "content": "\n".join(_["name"] for _ in asset["member"]),
                }

                assets.append(data)

    result.push_result(host, assets)

    return result
