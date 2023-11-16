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
from fotoobo.helpers.config import config
from fotoobo.helpers.files import load_yaml_file
from fotoobo.helpers.vault import Client

from .generic import GenericDevice

log = logging.getLogger("fotoobo")


class Inventory:
    """
    Represents an inventory full of Fortinet and generic devices. Instantiate the inventory by
    providing an inventory file in yaml format as described in the documentation at
    https://fotoobo.readthedocs.io/en/latest/usage/inventory.html
    """

    def __init__(self, inventory_file: Path) -> None:
        """Initialize the inventory

        Args:
            inventory file: The Path object to the inventory file.
        """
        log.debug("Initialize the fotoobo inventory")
        self._inventory_file: Path = inventory_file
        self._globals: Dict[str, Any] = {
            "fortianalyzer": {},
            "forticlientems": {},
            "fortigate": {},
            "fortimanager": {},
        }
        self.assets: Dict[str, Any] = {}
        self.vault_data: Dict[str, Dict[str, str]] = {}

        # Load assets from inventory file
        self._load_inventory()

        # Load credentials from a configured Hashicorp vault and enrich assets
        if config.vault:
            self._load_data_from_vault(config.vault)
            self._replace_with_vault_data()

        # Create object for FortiGates
        self.fortigates = {
            name: asset for (name, asset) in self.assets.items() if isinstance(asset, FortiGate)
        }

    def get(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> Dict[str, Any]:
        """
        Get a dictionary of assets from the inventory with given 'filters'.

        Args:
            name:   Which asset to get. If blank get every asset. Wildcard * is supported in any
                    position. E.g. "FortiGate", "*Gate", "Forti*ate", "Forti*".
            type:   Which asset type to get. If blank get every asset.

        Returns:
            Dictionary of assets with name as key

        Raises:
            GeneralWarning if no asset was found in the inventory that matches name or type
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

    def get_item(
        self,
        name: str = "",
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
    ) -> Any:
        """
        Get a single asset from the inventory. To be sure the item has the correct type you can
        specify the desired type and a GeneralWarning is raised if the type does not match.

        Args:
            name:   Which exact asset to get.
            type:   If you specify a type it is checked if it matches the type of the asset

        Returns:
            Inventory asset

        Raises:
            GeneralWarning if the asset was not found in the inventory
            GeneralWarning if the specified type does not match the type of the item
        """
        log.debug("getting asset with name '%s'", name)
        try:
            asset = self.assets[name]

        except KeyError as error:
            raise GeneralWarning(
                f"Asset with name '{name}' was not found in the inventory"
            ) from error

        if type and type != asset.type:
            raise GeneralWarning(f"Asset with name '{name}' is not of type '{type}'")

        return asset

    def _load_inventory(self) -> None:
        """
        Load the inventory from a file given
        """
        log.debug("Load the assets from the inventory file")
        # Expand user home shortcuts in the inventory file path
        expanded_inventory_file = self._inventory_file.expanduser()
        log.debug("loading assets from '%s'", expanded_inventory_file)
        inventory_raw: Dict[str, Any] = dict(load_yaml_file(expanded_inventory_file) or {})

        # Set the globals
        # This has to be done before the looping over all inventory items so that the globals are
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
                try:
                    self.assets[name] = FortiGate(**asset)
                except GeneralWarning as err:
                    log.warning("%s: %s", name, err)

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

    def _load_data_from_vault(self, vault_dict: Dict[str, Any]) -> None:
        """Load the credentials from a vault"""
        log.debug("Loading credentials from vault '%s'", vault_dict["url"])
        vault = Client(**vault_dict)
        data = vault.get_data()
        self.vault_data = data.get("ok", {}).get("data", {}).get("data", {})

    def _replace_with_vault_data(self) -> None:
        """Replace asset attributes with data from the vault"""
        for name, asset in self.assets.items():
            for attribute in dir(asset):
                if not attribute.startswith("_"):
                    if getattr(asset, attribute) == "VAULT":
                        try:
                            setattr(asset, attribute, self.vault_data[name][attribute])
                            log.debug(
                                "Vault attribute '%s.%s' replaced successfully", name, attribute
                            )
                        except KeyError:
                            log.warning("Vault attribute '%s.%s' not found", name, attribute)

    def _set_globals(self, data: Dict[str, Any]) -> None:
        """
        Set some defaults for device types

        Args:
            data:   defaults by device where key is the device type and value defines
                    its defaults
        """
        for key, value in data.items():
            self._globals[key] = value
