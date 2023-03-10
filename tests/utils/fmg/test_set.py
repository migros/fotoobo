"""Test utils fmg set"""


from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralWarning
from fotoobo.utils.fmg import set  # pylint: disable=redefined-builtin


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr("fotoobo.helpers.config.config.inventory_file", "tests/data/inventory.yaml")


@pytest.fixture(autouse=True)
def fmg_login(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiManager login to always return 200 without to really login"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.login",
        MagicMock(return_value=200),
    )


@pytest.fixture(autouse=True)
def fmg_logout(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiManager logout to always return 200 without to really logout"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.logout",
        MagicMock(return_value=200),
    )


def test_set(monkeypatch: MonkeyPatch) -> None:
    """Test set"""
    monkeypatch.setattr(
        "fotoobo.utils.fmg.set_.load_json_file", MagicMock(return_value={"dummy": "dummy"})
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.set", MagicMock(return_value=None)
    )
    set("test_fmg", "", "")
    assert True


def test_set_exception_empty_payload_file(monkeypatch: MonkeyPatch) -> None:
    """Test set with exception when device is not defined"""
    monkeypatch.setattr("fotoobo.utils.fmg.set_.load_json_file", MagicMock(return_value=[]))
    with pytest.raises(GeneralWarning, match=r"there is no data in the given file \(dummy_file\)"):
        set("dummy", "dummy_file", "")
