"""
FortiManager assign utility
"""

import logging

from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def assign(host: str, adoms: str, timeout: int = 60) -> None:
    """
    Assign the global policy to the given ADOM

    Args:
        host (str):  The FortiManager defined in inventory

        adoms (str): The ADOMs to assign the global policy to. Specify multiple ADOMs as a comma
        separated list (no spaces)

    Raises:
        GeneralWarning: _description_
    """
    inventory = Inventory(config.inventory_file)
    fmg = inventory.get(host, "fortimanager")[host]
    fmg.login()

    log.debug("Assigning global policy/objects to ADOM %s", adoms)
    task_id = fmg.assign_all_objects(adoms)
    if task_id > 0:
        log.info("created FortiManager task id %s", task_id)
        messages = fmg.wait_for_task(task_id, timeout=timeout)
        for message in messages:
            level = "debug" if message["state"] == 4 else "error"
            elapsed = (
                str(message["end_tm"] - message["start_tm"]) + " sec"
                if message["end_tm"] > 0
                else "unfinished"
            )
            getattr(log, level)(
                "FortiManager task %s: %s%s (%s)",
                message["task_id"],
                message["name"],
                f" / {message['detail']}" if message["detail"] else "",
                elapsed,
            )
            if message["history"]:
                for line in message["history"]:
                    getattr(log, level)("- %s", line["detail"])

    fmg.logout()
