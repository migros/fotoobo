"""
FortiManager assign utility
"""

import logging
from pathlib import Path

from fotoobo.exceptions.exceptions import GeneralWarning
from fotoobo.helpers.config import config
from fotoobo.helpers.files import load_json_file
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def assign(adoms: str, policy: str, host: str, timeout: int = 60) -> Result[str]:
    """
    Assign the global policy to the given ADOM

    Args:
        adoms:  The ADOMs to assign the global policy to. Specify multiple ADOMs as a comma
                separated list (no spaces).
        policy: Specify the global policy to assign [Default: 'default'].
        host:   The FortiManager defined in inventory.
        timeout Timeout in sec. to wait for the FortiManager task to finish [Default: 60].
    """
    result = Result[str]()
    inventory = Inventory(config.inventory_file)
    fmg = inventory.get_item(host, "fortimanager")
    fmg.login()

    log.debug("Assigning global policy/objects to ADOM %s", adoms)
    task_id = fmg.assign_all_objects(adoms=adoms, policy=policy)
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
            result_message = f"{message['task_id']}: {message['name']}"
            if message["detail"]:
                result_message += f" / {message['detail']}"

            result_message += f" ({elapsed})"
            getattr(log, level)(result_message)
            result.push_message(host, result_message, level)
            if message["history"]:
                for line in message["history"]:
                    result_message = f"- {line['detail']}"
                    getattr(log, level)(result_message)
                    result.push_message(host, result_message, level)

    fmg.logout()
    return result


def post(file: Path, adom: str, host: str) -> None:
    """
    POST the given configuration from a JSON file to the FortiManager

    Args:
        file (str): The configuration file to oad the configuration from
        adom (str): The ADOM to assign the global policy to
        host (str): The FortiManager defined in inventory

    Raises:
        GeneralWarning: GeneralWarning
    """
    if not (payloads := load_json_file(file)):
        raise GeneralWarning(f"there is no data in the given file ({file})")

    inventory = Inventory(config.inventory_file)
    fmg = inventory.get_item(host, "fortimanager")
    fmg.login()

    log.debug("FortiManager post command ...")
    log.info("start POSTing assets to '%s'", host + "/" + adom)

    fmg.post(adom, payloads)
    fmg.logout()
