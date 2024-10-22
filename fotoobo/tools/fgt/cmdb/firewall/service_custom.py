"""FortiGate CMDB firewall service custom module"""

from pathlib import Path
from typing import Any

from fotoobo.helpers.result import Result
from fotoobo.tools.fgt.get import api


def get_cmdb_firewall_service_custom(
    host: str, name: str, vdom: str, output_file: str
) -> Result[list[Any]]:
    """Get the firewall service custom object(s)

    The FortiGate api endpoint is: /cmdb/firewall.service/custom
    """
    result_raw = api(host=host, vdom=vdom, url=f"/cmdb/firewall.service/custom/{name}")

    if output_file:
        result_raw.save_raw(file=Path(output_file), key=host)

    result = Result[list[Any]]()
    assets = []
    if result_raw.get_result(host):
        for vd in result_raw.get_result(host):
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
