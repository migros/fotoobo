"""Test fmg tools get devices"""


from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.tools.fmg.get import devices
from tests.helper import ResponseMock


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


def test_devices(monkeypatch: MonkeyPatch) -> None:
    """Test get devices"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": [
                        {
                            "data": [
                                {
                                    "name": "dummy_1",
                                    "os_ver": 1,
                                    "mr": 2,
                                    "patch": 3,
                                    "ha_mode": 0,
                                    "platform_str": "dummy_platform_1",
                                    "desc": "dummy_description_1",
                                },
                                {
                                    "name": "dummy_2",
                                    "os_ver": 4,
                                    "mr": 5,
                                    "patch": 6,
                                    "ha_mode": 1,
                                    "platform_str": "dummy_platform_2",
                                    "desc": "dummy_description_2",
                                },
                            ],
                        },
                    ],
                },
                status=200,
            ),
        ),
    )
    data = devices("test_fmg")
    assert len(data) == 2
    assert data[0]["name"] == "dummy_1"
    assert data[0]["version"] == "1.2.3"
    assert data[0]["ha_mode"] == "0"
    assert data[0]["platform"] == "dummy_platform_1"
    assert data[0]["desc"] == "dummy_description_1"
    assert data[1]["name"] == "dummy_2"
    assert data[1]["version"] == "4.5.6"
    assert data[1]["ha_mode"] == "1"
    assert data[1]["platform"] == "dummy_platform_2"
    assert data[1]["desc"] == "dummy_description_2"
