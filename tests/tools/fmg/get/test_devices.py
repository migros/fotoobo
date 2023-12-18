"""Test fmg tools get devices"""


from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.tools.fmg.get import devices
from tests.helper import ResponseMock


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
                                    "ha_slave": [{"name": "node_1"}, {"name": "node_2"}],
                                },
                            ],
                        },
                    ],
                },
                status=200,
            ),
        ),
    )
    result = devices("test_fmg")

    assert len(result.results) == 2

    host_1 = result.get_result("dummy_1")
    assert host_1["version"] == "1.2.3"
    assert host_1["ha_mode"] == "0"
    assert host_1["platform"] == "dummy_platform_1"
    assert host_1["desc"] == "dummy_description_1"
    assert host_1["ha_nodes"] == []

    host_2 = result.get_result("dummy_2")
    assert host_2["version"] == "4.5.6"
    assert host_2["ha_mode"] == "1"
    assert host_2["platform"] == "dummy_platform_2"
    assert host_2["desc"] == "dummy_description_2"
    assert host_2["ha_nodes"] == ["node_1", "node_2"]
