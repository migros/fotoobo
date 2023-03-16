"""
FortiAnalyzer get version utility
"""

import logging
from typing import Dict

from fotoobo.helpers.config import config
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def version(host: str) -> Dict[str, str]:
    """
    FortiAnalyzer get version

    Args:
        host (str): host defined in inventory

    Raises:
        GeneralWarning: GeneralWarning

    Returns:
        Dict[str, str]: version data in a dict with keys: host, version
    """
    inventory = Inventory(config.inventory_file)
    assets = inventory.get(host, "fortianalyzer")
    log.debug("FortiAnalyzer get version ...")
    assets[host].login()
    faz_version = assets[host].get_version()
    assets[host].logout()

    return {"host": host, "version": faz_version}
