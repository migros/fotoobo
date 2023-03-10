"""
Test the inventory
"""

from typing import Optional
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralWarning
from fotoobo.inventory.inventory import Inventory


class TestInventory:
    """Test inventory"""

    @staticmethod
    def test_init(monkeypatch: MonkeyPatch) -> None:
        """Test the __init__ method"""
        monkeypatch.setattr(
            "fotoobo.inventory.inventory.load_yaml_file",
            MagicMock(
                return_value={
                    "fgt_1": {"hostname": "hostname_1", "token": "", "type": "fortigate"},
                    "generic_2": {"hostname": "hostname_2"},
                }
            ),
        )
        inventory = Inventory("dummy")
        assert isinstance(inventory.assets, dict)
        assert len(inventory.assets) == 2
        assert len(inventory.fortigates) == 1

    @staticmethod
    @pytest.mark.parametrize(
        "test_name, test_type, expected_len",
        (
            pytest.param(None, None, 7, id="no name, no type"),
            pytest.param("test_fgt_1", None, 1, id="name, no type"),
            pytest.param(None, "fortigate", 2, id="no name, type"),
        ),
    )
    def test_get(test_name: Optional[str], test_type: Optional[str], expected_len: int) -> None:
        """Test Inventory.get()"""
        inventory = Inventory("tests/data/inventory.yaml")
        assets = inventory.get(test_name, test_type)
        assert len(assets) == expected_len

    @staticmethod
    @pytest.mark.parametrize(
        "test_name, test_type, expected_message",
        (
            pytest.param("dummy", "dummy", r"asset dummy is not.*", id="wrong name, wrong type"),
            pytest.param("test_fgt_1", "dummy", r"no .*type 'dum.*", id="name, wrong type"),
            pytest.param(None, "dummy", r"no.*type 'dummy'.*", id="no name, wrong type"),
        ),
    )
    def test_get_with_exception(
        test_name: Optional[str], test_type: Optional[str], expected_message: str
    ) -> None:
        """Test Inventory.get() when a exception is raised"""
        inventory = Inventory("tests/data/inventory.yaml")
        with pytest.raises(GeneralWarning, match=expected_message):
            inventory.get(test_name, test_type)
