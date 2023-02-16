"""
The FortiManager set utility
"""
import logging

from fotoobo.exceptions import GeneralWarning
from fotoobo.helpers.config import config
from fotoobo.helpers.files import load_json_file
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def set(host: str, file: str, adom: str) -> None:  # pylint: disable=redefined-builtin
    """
    Set the given configuration from a JSON file to the FortiManager

    Args:
        host (str): The FortiManager defined in inventory
        file (str): The configuration file to oad the configuration from
        adom (str): The ADOM to assign the global policy to

    Raises:
        GeneralWarning: GeneralWarning
    """
    if not (payloads := load_json_file(file)):
        raise GeneralWarning(f"there is no data in the given file ({file})")

    inventory = Inventory(config.inventory_file)
    fmg = inventory.get(host, "fortimanager")[host]
    fmg.login()

    log.debug("FortiManager set command ...")
    log.info("start setting assets to '%s'", host + "/" + adom)

    fmg.set(adom, payloads)
    fmg.logout()
