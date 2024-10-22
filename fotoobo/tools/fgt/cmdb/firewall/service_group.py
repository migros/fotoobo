"""FortiGate CMDB firewall service group module"""

from pathlib import Path
from typing import Any

from fotoobo.helpers.result import Result
from fotoobo.tools.fgt.get import api


def get_cmdb_firewall_service_group(
    host: str, name: str, vdom: str, output_file: str
) -> Result[list[Any]]:
    """Get the firewall service group object(s)

    The FortiGate api endpoint is: /cmdb/firewall.service/group
    """
    result_raw = api(host=host, vdom=vdom, url=f"/cmdb/firewall/addrgrp/{name}")

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
                    "content": "\n".join(_["name"] for _ in asset["member"]),
                }

                assets.append(data)

    result.push_result(host, assets)

    return result
