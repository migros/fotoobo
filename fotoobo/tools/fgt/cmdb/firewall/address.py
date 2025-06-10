"""FortiGate CMDB firewall address module"""

from pathlib import Path
from typing import Any, Optional


from fotoobo.fortinet.fortigate import FortiGate
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory


def get_cmdb_firewall_address(
    host: str, name: str, vdom: str, output_file: Optional[str]
) -> Result[list[Any]]:
    """Get the firewall address object(s)

    The FortiGate api endpoint is: /cmdb/firewall/address
    """
    inventory = Inventory(config.inventory_file)
    fgt: FortiGate = inventory.get_item(host, "fortigate")
    result = Result[list[Any]]()

    address_list = fgt.api_get(url=f"/cmdb/firewall/address/{name}", vdom=vdom)
    result.push_result(key=host, data=address_list)

    if output_file:
        result.push_result(key=host, data=address_list)
        result.save_raw(file=Path(output_file), key=host)

    assets = []
    if address_list:
        for vd in address_list:
            for asset in vd["results"]:

                data: dict[str, str] = {
                    "name": asset["name"],
                    "vdom": vd["vdom"],
                    "type": asset["type"],
                }

                if asset["type"] == "fqdn":
                    data["content"] = asset["fqdn"]

                elif asset["type"] == "geography":
                    data["content"] = asset["country"]

                elif asset["type"] == "ipmask":
                    data["content"] = "/".join(
                        [asset["subnet"].split(" ")[0], asset["subnet"].split(" ")[1]]
                    )

                elif asset["type"] == "iprange":
                    data["content"] = " - ".join([asset["start-ip"], asset["end-ip"]])

                else:
                    data["content"] = ""

                assets.append(data)

    result.push_result(host, assets)

    return result
