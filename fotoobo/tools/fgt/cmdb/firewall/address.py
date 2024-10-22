"""FortiGate CMDB firewall address module"""

from pathlib import Path
from typing import Any

from fotoobo.helpers.result import Result
from fotoobo.tools.fgt.get import api


def get_cmdb_firewall_address(
    host: str, name: str, vdom: str, output_file: str
) -> Result[list[Any]]:
    """Get the firewall address object(s)

    The FortiGate api endpoint is: /cmdb/firewall/address
    """
    result_raw = api(host=host, vdom=vdom, url=f"/cmdb/firewall/address/{name}")

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
