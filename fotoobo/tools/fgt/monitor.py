"""
FortiGate check hamaster utility
"""

import concurrent.futures
import logging
from typing import Dict, Tuple

from rich.progress import Progress

from fotoobo.fortinet.fortigate import FortiGate
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def hamaster(host: str) -> Result[str]:  # pylint: disable=too-many-locals
    """FortiGate check hamaster.

    This method first gets all the devices from a FortiManager to find all the managed FortiGates
    clusters. Then it queries every cluster for its HA status directly to its shared management ip.
    Be aware that the device names in FortiManager must match the names in the inventory because we
    search for the devices we found in Fortimanager in our inventory to connect to to them.

    Args:
        host:   The FortiManager host from the inventory to get the device list from. If you omit
                host, it will run over the default FortiManager (fmg).

    Returns:
        The Result object with all the results
    """

    def _get_single_status(name: str, fgt: FortiGate) -> Tuple[str, str]:
        """Get the HA master status from a FortiGate.

        This private method is used for multithreading. It only queries one single FortiGate for its
        HA master status and returns it.

        Args:
            name:   The name of the FortiGate (as defined in the inventory)
            fgt:    The FortiGate object to query

        Returns:
            name:   The name of the FortiGate (as defined in the inventory)
            status: The HA status of the FortiGate (fgt)
        """
        response = fgt.api("get", "/monitor/system/ha-checksums")
        ha_checksums = response.json()
        status: str = "is not the expected master"
        for node in ha_checksums["results"]:
            if node["serial_no"] == ha_checksums["serial"]:
                if node["is_root_master"] == 1:
                    status = "ok"

        return name, status

    inventory = Inventory(config.inventory_file)
    fmg = inventory.get_item(host, "fortimanager")

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

    result = Result[str]()
    fgts: Dict[str, FortiGate] = {}
    for device in response.json()["result"][0]["data"]:
        if device["ha_mode"] == 1:
            expected_master = ""
            highest = 0
            # Loop over all the cluster nodes and find the node with the hightest priority
            for node in device["ha_slave"]:
                if node["prio"] > highest:
                    highest = node["prio"]
                    expected_master = node["name"].lower()

            try:
                fortigate: FortiGate = inventory.assets[expected_master]
                # Replace the FortiGates Hostname with the cluster IP address. In case of a HA
                # failover the designated master may not be reachable so we connect to the cluster
                # IP address.
                fortigate.hostname = device["ip"]
                fgts[expected_master] = fortigate

            # There is a KeyError if a designated cluster master is not defined in the inventory
            except KeyError:
                log.debug("device %s not found in inventory", expected_master)
                result.push_result(expected_master, "not found in inventory")

    with Progress() as progress:
        task = progress.add_task("getting FortiGate HA status...", total=len(fgts))
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for name, fgt in fgts.items():
                futures.append(executor.submit(_get_single_status, name, fgt))

            for future in concurrent.futures.as_completed(futures):
                name, status = future.result()
                result.push_result(name, status)
                progress.update(task, advance=1)

    return result
