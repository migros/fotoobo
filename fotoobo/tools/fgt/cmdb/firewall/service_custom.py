"""FortiGate CMDB firewall service custom module"""

from pathlib import Path
from typing import Any, Optional

from fotoobo.fortinet.fortigate import FortiGate
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory


def get_cmdb_firewall_service_custom(
    host: str, name: str, vdom: str, output_file: Optional[str]
) -> Result[list[Any]]:
    """Get the firewall service custom object(s)

    The FortiGate api endpoint is: /cmdb/firewall.service/custom
    """
    inventory = Inventory(config.inventory_file)
    fgt: FortiGate = inventory.get_item(host, "fortigate")
    result = Result[list[Any]]()

    service_custom_list = fgt.api_get(url=f"/cmdb/firewall.service/custom/{name}", vdom=vdom)

    if output_file:
        result.push_result(key=host, data=service_custom_list)
        result.save_raw(file=Path(output_file), key=host)

    assets = []
    if service_custom_list:
        for vd in service_custom_list:
            for asset in vd["results"]:

                data: dict[str, str] = {
                    "name": asset["name"],
                    "vdom": vd["vdom"],
                    "protocol": asset["protocol"],
                }

                if asset["protocol"] == "TCP/UDP/SCTP":
                    data["data_1"] = asset.get("tcp-portrange", "")
                    data["data_2"] = asset.get("udp-portrange", "")

                elif asset["protocol"] in ["ICMP", "ICMP6"]:
                    data["data_1"] = asset.get("icmptype", "")
                    data["data_2"] = asset.get("icmpcode", "")

                elif asset["protocol"] == "IP":
                    data["data_1"] = asset.get("protocol-number", "")
                    data["data_2"] = ""

                else:
                    data["data_1"] = ""
                    data["data_2"] = ""

                assets.append(data)

    result.push_result(host, assets)

    return result
