"""
Test the inventory
"""

from pathlib import Path
from typing import Optional

import pytest

from fotoobo.exceptions import GeneralWarning
from fotoobo.inventory.inventory import Inventory


class TestInventory:
    """Test inventory"""

    @staticmethod
    def test_init() -> None:
        """
        Test the __init__ method

        Here we load the test inventory from the tests directory and check if the resulting
        inventory has the correct entries and options. It also checks if the global options in the
        inventory file are written to the devices and if the options on devices have precedence over
        the global options.
        """
        inventory = Inventory(Path("tests/data/inventory.yaml"))
        assert isinstance(inventory.assets, dict)
        assert len(inventory.assets) == 8
        assert len(inventory.fortigates) == 3
        assert inventory.assets["test_fgt_1"].https_port == 111
        assert inventory.assets["test_fgt_2"].https_port == 222
        assert "test_fgt_3" not in inventory.assets  # not in inventory due to no hostname
        assert inventory.assets["test_fgt_4"].hostname == "dummy"
        assert inventory.assets["test_fgt_4"].token == ""
        assert "test_fgt_5" not in inventory.assets  # not in inventory due to no hostname
        assert inventory.assets["test_ems"].https_port == 443

    @staticmethod
    @pytest.mark.parametrize(
        "test_name, test_type, expected_len",
        (
            pytest.param(None, None, 8, id="no name, no type"),
            pytest.param("test_fgt_1", None, 1, id="name, no type"),
            pytest.param("*_fgt_1", None, 1, id="wildcard name 1, no type"),
            pytest.param("test_*_1", None, 1, id="wildcard name 2, no type"),
            pytest.param("test_fgt_*", None, 3, id="wildcard name 3, no type"),
            pytest.param(None, "fortigate", 3, id="no name, type"),
        ),
    )
    def test_get(test_name: Optional[str], test_type: Optional[str], expected_len: int) -> None:
        """Test Inventory.get()"""
        inventory = Inventory(Path("tests/data/inventory.yaml"))
        assets = inventory.get(test_name, test_type)
        assert len(assets) == expected_len

    @staticmethod
    @pytest.mark.parametrize(
        "test_name, test_type",
        (
            pytest.param("dummy", "dummy", id="wrong name, wrong type"),
            pytest.param("test_fgt_1", "dummy", id="name, wrong type"),
            pytest.param(None, "dummy", id="no name, wrong type"),
            pytest.param("dummy", None, id="wrong name, no type"),
            pytest.param("*dummy", None, id="wrong wildcard name 1, no type"),
            pytest.param("dum*my", None, id="wrong wildcard name 2, no type"),
            pytest.param("dummy*", None, id="wrong wildcard name 3, no type"),
        ),
    )
    def test_get_with_exception(test_name: Optional[str], test_type: Optional[str]) -> None:
        """Test Inventory.get() when an exception is raised"""
        inventory = Inventory(Path("tests/data/inventory.yaml"))
        with pytest.raises(GeneralWarning, match=r"no asset of type .* and name .*"):
            inventory.get(test_name, test_type)

    @staticmethod
    @pytest.mark.parametrize(
        "test_type",
        (
            pytest.param(None, id="without type"),
            pytest.param("fortigate", id="with type"),
        ),
    )
    def test_get_item(test_type: Optional[str]) -> None:
        """Test Inventory.get_item()"""
        inventory = Inventory(Path("tests/data/inventory.yaml"))
        asset = inventory.get_item("test_fgt_1", test_type)
        assert asset.hostname == "dummy"

    @staticmethod
    @pytest.mark.parametrize(
        "test_name, test_type",
        (
            pytest.param("", None, id="empty name"),
            pytest.param("dummy", None, id="nonexisting name"),
            pytest.param("test_fgt_1", "dummy_type", id="wrong type"),
        ),
    )
    def test_get_item_with_exception(test_name: str, test_type: Optional[str]) -> None:
        """Test Inventory.get_item() when an exception is raised"""
        inventory = Inventory(Path("tests/data/inventory.yaml"))
        with pytest.raises(GeneralWarning, match=r"Asset with name"):
            inventory.get_item(test_name, test_type)
