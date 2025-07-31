"""
Test fmg tools get policy.
"""

from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from fotoobo.exceptions import GeneralError
from fotoobo.tools.fmg.get import policy
from tests.helper import ResponseMock


def test_policy(monkeypatch: MonkeyPatch) -> None:
    """
    Test get policy.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.api",
        Mock(
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

    # Act
    result = policy("test_fmg", "", "")

    # Assert
    data = result.get_result("test_fmg")
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
    """
    Test get policy with exception when status is not 200.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.api",
        Mock(
            return_value=ResponseMock(
                json={"result": [{"status": {"code": 42, "message": "msg"}}]},
                status=200,
            )
        ),
    )

    # Act & Assert
    with pytest.raises(GeneralError, match=r"FortiManager test_fmg returned 42: msg"):
        policy("test_fmg", "", "")
