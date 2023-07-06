"""
Devices class for storing device information
"""

import logging
import re
from pathlib import Path
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
    Represents an inventory full of Fortinet and generic devices. Instantiate the inventory by
    providing an inventory file in yaml format as described in the documentation at
    https://fotoobo.readthedocs.io/en/latest/usage/inventory.html
    """

    def __init__(self, inventory_file: Path):
        """Initialize the inventory"""
        self._inventory_file: Path = inventory_file
        self._globals: Dict[str, Any] = {
            "fortianalyzer": {},
            "forticlientems": {},
            "fortigate": {},
            "fortimanager": {},
        }
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
            name:   Which asset to get. If blank get every asset. Wildcard * is supported in any
                    position. E.g. "FortiGate", "*Gate", "Forti*ate", "Forti*".
            type:   Which asset type to get. If blank get every asset.

        Returns:
            Dict of assets with name as key

        Raises:
            GeneralWarning if no asset was found that matches name or type
        """
        log.debug("getting assets with name '%s' and type '%s'", name, type)
        name_pattern = f"^{name}$".replace("*", ".*")
        assets = {}
        for _name, _asset in self.assets.items():
            if not name and not type:
                assets[_name] = _asset

            elif not name and getattr(_asset, "type", None) == type:
                assets[_name] = _asset

            elif name and re.match(name_pattern, _name):
                if (type and getattr(_asset, "type", None) == type) or not type:
                    assets[_name] = _asset

        if not assets:
            raise GeneralWarning(
                f"no asset of type '{type}' and name '{name}' was found in the inventory"
            )

        return assets

    def _load_inventory(self) -> None:
        """
        Load the inventory from a file given
        """
        # Expand user home shortcuts in the inventory file path
        expanded_inventory_file = self._inventory_file.expanduser()
        log.debug("loading assets from '%s'", expanded_inventory_file)
        inventory_raw: Dict[str, Any] = dict(load_yaml_file(expanded_inventory_file) or {})

        # set the globals
        # this has to be done before the looping over all inventory items so that the globals are
        # already set during looping
        if "globals" in inventory_raw:
            self._set_globals(inventory_raw["globals"])

        for name, asset in inventory_raw.items():
            # skip globals
            if name == "globals":
                continue

            # enrich the raw asset data with the globals
            if asset.get("type", None) in self._globals:
                asset = {**self._globals[asset["type"]], **asset}

            if asset.get("type", "") == "fortigate":
                self.assets[name] = FortiGate(**asset)

            elif asset.get("type", "") == "forticlientems":
                self.assets[name] = FortiClientEMS(**asset)

            elif asset.get("type", "") == "fortianalyzer":
                self.assets[name] = FortiAnalyzer(**asset)

            elif asset.get("type", "") == "fortimanager":
                self.assets[name] = FortiManager(**asset)

            else:
                self.assets[name] = GenericDevice(**asset)

    # pylint: disable=pointless-string-statement
    """
        # create asset object using the match and case keywords
        match asset_type:
            case "fortigate":
                self.assets[name] = FortiGate(**asset)
            case "forticlientems":
                self.assets[name] = FortiClientEMS(**asset)
            case "fortianalyzer":
                self.assets[name] = FortiAnalyzer(**asset)
            case "fortimanager":
                self.assets[name] = FortiManager(**asset)
            case _:
                self.assets[name] = GenericDevice(**asset)
    """

    def _set_globals(self, data: Dict[str, Any]) -> None:
        """
        Set some defaults for device types

        Args:
            data:   defaults by device where key is the device type and value defines
                    its defaults
        """
        for key, value in data.items():
            self._globals[key] = value
