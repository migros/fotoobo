"""
Test fgt tools check hamaster
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.tools.fgt.monitor import hamaster
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


@pytest.mark.parametrize(
    "ret_val, expected",
    (
        pytest.param(
            {
                "results": [
                    {"is_root_master": 0, "serial_no": "FG11111111111111"},
                    {"is_root_master": 1, "serial_no": "FG00000000000000"},
                ],
                "serial": "FG11111111111111",
            },
            "is not the expected master",
            id="not OK",
        ),
        pytest.param(
            {
                "results": [
                    {"is_root_master": 1, "serial_no": "FG11111111111111"},
                    {"is_root_master": 0, "serial_no": "FG00000000000000"},
                ],
                "serial": "FG11111111111111",
            },
            "ok",
            id="OK",
        ),
    ),
)
def test_hamaster(monkeypatch: MonkeyPatch, ret_val: str, expected: str) -> None:
    """Test check hamaster"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": [
                        {
                            "data": [
                                {
                                    "name": "test_fgt",
                                    "ha_mode": 1,
                                    "ha_slave": [
                                        {"prio": 100, "name": "test_fgt_1"},
                                        {"prio": 200, "name": "test_fgt_2"},  # designated master
                                    ],
                                    "ip": "1.2.3.4",
                                },
                                {
                                    "name": "dummy",
                                    "ha_mode": 1,
                                    "ha_slave": [
                                        {"prio": 100, "name": "dummy_1"},
                                        {"prio": 200, "name": "dummy_2"},  # designated master
                                    ],
                                    "ip": "1.2.3.4",
                                },
                            ]
                        }
                    ]
                },
                status=200,
            )
        ),
    )
    monkeypatch.setattr(
        "fotoobo.tools.fgt.monitor.FortiGate.api",
        MagicMock(return_value=ResponseMock(json=ret_val)),
    )
    monkeypatch.setattr(
        "fotoobo.helpers.result.Result.send_messages_as_mail",
        MagicMock(return_value=None),
    )
    result = hamaster("test_fmg")
    assert result.get_result("test_fgt_2") == expected
    assert result.get_result("dummy_2") == "not found in inventory"
