"""
Test fmg tools get devices.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.fmg.get import devices
from tests.helper import ResponseMock


def test_devices(monkeypatch: MonkeyPatch) -> None:
    """
    Test get devices.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.api",
        Mock(
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

    # Act
    result = devices("test_fmg")

    # Assert
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
