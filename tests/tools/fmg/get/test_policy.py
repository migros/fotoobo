"""Test fmg tools get policy"""


from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralError
from fotoobo.tools.fmg.get import policy
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


def test_policy(monkeypatch: MonkeyPatch) -> None:
    """Test get policy"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": [
                        {
                            "status": {"code": 0},
                            "data": [
                                {
                                    "status": "0",
                                    "global-label": "1",
                                    "policyid": "2",
                                    "srcaddr": "3",
                                    "groups": "4",
                                    "dstaddr": "5",
                                    "service": "6",
                                    "action": "7",
                                    "send-deny-packet": "8",
                                    "comments": "9",
                                    "dummy": "10",
                                }
                            ],
                        }
                    ],
                },
                status=200,
            )
        ),
    )
    data = policy("test_fmg", "", "")
    assert data == [
        {
            "status": "0",
            "global-label": "1",
            "policyid": "2",
            "srcaddr": "3",
            "groups": "4",
            "dstaddr": "5",
            "service": "6",
            "action": "7",
            "send-deny-packet": "8",
            "comments": "9",
        }
    ]


def test_policy_exception_status_not_0(monkeypatch: MonkeyPatch) -> None:
    """Test get policy with exception when status is not 200"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.api",
        MagicMock(
            return_value=ResponseMock(
                json={"result": [{"status": {"code": 42, "message": "msg"}}]},
                status=200,
            )
        ),
    )
    with pytest.raises(GeneralError, match=r"FortiManager test_fmg returned 42: msg"):
        policy("test_fmg", "", "")
