"""
FortiManager get ADOMs utility
"""

import logging
from typing import Dict, List

from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def adoms(host: str) -> List[Dict[str, str]]:
    """
    FortiManager get ADOMs

    Args:
        host (str): the host from the inventory to get the ADOMs list from

    Returns:
        list of dict: list of ADOMs where ADOM is a dict with keys: name, version
    """
    inventory = Inventory(config.inventory_file)
    fmg = inventory.get(host, "fortimanager")[host]
    adom_list = []
    log.debug("FortiManager get adoms ...")
    fmg.login()
    fmg_adoms = fmg.get_adoms()
    for adom in fmg_adoms:
        adom_list.append({"name": adom["name"], "version": f"{adom['os_ver']}.{adom['mr']}"})

    fmg.logout()
    return adom_list
