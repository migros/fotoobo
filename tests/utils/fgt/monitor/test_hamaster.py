"""
Test utils fgt check hamaster
"""

from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.utils.fgt.monitor import hamaster
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


@pytest.mark.parametrize(
    "ret_val, expected",
    (
        pytest.param("dummy_1", "not OK", id="not OK"),
        pytest.param("dummy_2", "OK", id="OK"),
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
                                    "name": "dummy",
                                    "ha_mode": 1,
                                    "ha_slave": [
                                        {"prio": 1, "name": "dummy_1"},
                                        {"prio": 2, "name": "dummy_2"},
                                    ],
                                    "ip": "1.2.3.4",
                                }
                            ]
                        }
                    ]
                },
                status=200,
            )
        ),
    )
    monkeypatch.setattr(
        "fotoobo.utils.fgt.monitor._snmp_get",
        MagicMock(return_value=ret_val),
    )
    monkeypatch.setattr("fotoobo.helpers.output.Output.send_mail", MagicMock(return_value=None))
    data = hamaster("test_fmg", smtp_server="test_smtp")
    assert data == [{"name": "dummy", "status": expected}]
