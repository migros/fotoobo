"""Test ems tools get version"""


from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.tools.ems.get import version


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


@pytest.fixture(autouse=True)
def faz_login(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiClient EMS Login to always return 200 without to really login"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.login",
        MagicMock(return_value=200),
    )


def test_version(monkeypatch: MonkeyPatch) -> None:
    """Test get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.get_version",
        MagicMock(return_value="1.1.1"),
    )
    result = version("test_ems")
    data = result.get_result("test_ems")
    assert data == "v1.1.1"
