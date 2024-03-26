"""Test fmg tools get adoms"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.tools.fmg.get import adoms


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


@pytest.fixture(autouse=True)
def fmg_login(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiManager Login to always return 200 without to really login"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.login",
        MagicMock(return_value=200),
    )


@pytest.fixture(autouse=True)
def fmg_logout(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiManager Login to always return 200 without to really logout"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.logout",
        MagicMock(return_value=200),
    )


def test_adoms(monkeypatch: MonkeyPatch) -> None:
    """Test get adoms"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.get_adoms",
        MagicMock(
            return_value=[
                {"name": "adom_1", "os_ver": "1", "mr": "2"},
                {"name": "adom_2", "os_ver": "3", "mr": "4"},
            ]
        ),
    )
    result = adoms("test_fmg")

    assert len(result.results) == 2
    assert result.get_result("adom_1") == "1.2"
    assert result.get_result("adom_2") == "3.4"
