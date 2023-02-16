"""
Devices class for storing device information
"""

import logging
from typing import Any, Dict, Optional

from fotoobo.exceptions import GeneralWarning
from fotoobo.fortinet.fortianalyzer import FortiAnalyzer
from fotoobo.fortinet.forticlientems import FortiClientEMS
from fotoobo.fortinet.fortigate import FortiGate
from fotoobo.fortinet.fortimanager import FortiManager
from fotoobo.helpers.files import load_yaml_file
from .generic import GenericDevice

log = logging.getLogger("fotoobo")


class Inventory:
    """
    Represents an inventory file given
    """

    def __init__(self, inventory_file: str):
        self._inventory_file: str = inventory_file
        self.assets: Dict[str, Any] = {}
        self._load_inventory()
        self.fortigates = {
            name: asset for (name, asset) in self.assets.items() if isinstance(asset, FortiGate)
        }

    def get(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> Dict[str, Any]:
        """
        Get a list of assets from the inventory

        Args:
            asset (str, optional): Which asset to get. If blank get every asset
            type (str, optional) : Which asset type to get. If blank get every asset.

        Returns:
            Dict[str, Any]: Dict of assets with name as key
        """
        log.debug("getting assets with name '%s' and type '%s'", name, type)
        if name and name not in self.assets:
            raise GeneralWarning(f"asset {name} is not defined in inventory")
        assets = {}
        for _name, _asset in self.assets.items():
            if not name and not type:
                assets[_name] = _asset
            if not name and getattr(_asset, "type", None) == type:
                assets[_name] = _asset
            if name and _name == name:
                if (type and getattr(_asset, "type", None) == type) or not type:
                    assets[_name] = _asset
        if type and len(assets) == 0:
            raise GeneralWarning(f"no asset of type '{type}' was found in the inventory")
        return assets

    def _load_inventory(self) -> None:
        """
        Load the inventory from a file given
        """
        log.debug("loading assets from '%s'", self._inventory_file)
        inventory_raw: Dict[str, Any] = dict(load_yaml_file(self._inventory_file) or {})
        for name, asset in inventory_raw.items():
            if asset.get("type", "") == "fortigate":
                self.assets[name] = FortiGate(**inventory_raw[name])

            elif asset.get("type", "") == "forticlientems":
                self.assets[name] = FortiClientEMS(**inventory_raw[name])

            elif asset.get("type", "") == "fortianalyzer":
                self.assets[name] = FortiAnalyzer(**inventory_raw[name])

            elif asset.get("type", "") == "fortimanager":
                self.assets[name] = FortiManager(**inventory_raw[name])

            else:
                self.assets[name] = GenericDevice(**inventory_raw[name])
