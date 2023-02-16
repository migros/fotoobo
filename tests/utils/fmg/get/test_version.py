"""Test utils fmg get version"""


from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralWarning
from fotoobo.utils.fmg.get import version


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr("fotoobo.helpers.config.config.inventory_file", "tests/data/inventory.yaml")


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


def test_version(monkeypatch: MonkeyPatch) -> None:
    """Test get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.get_version",
        MagicMock(return_value="1.1.1"),
    )
    data = version("test_fmg")
    assert data == {"host": "test_fmg", "version": "1.1.1"}
