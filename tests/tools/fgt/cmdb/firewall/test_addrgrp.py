"""
Test fgt cmdb firewall address group.
"""

# mypy: disable-error-code=attr-defined

from pathlib import Path
from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.fgt.cmdb.firewall import get_cmdb_firewall_addrgrp


def test_get_cmdb_firewall_addrgrp(monkeypatch: MonkeyPatch) -> None:
    """
    Test the get cmdb firewall address group method.
    """

    # Arrange
    result_mock = [
        {
            "results": [
                {"name": "group_1", "member": [{"name": "member_1"}, {"name": "member_2"}]},
                {"name": "group_2", "member": [{"name": "member_3"}, {"name": "member_4"}]},
            ],
            "vdom": "vdom_1",
        }
    ]
    api_get_mock = Mock(return_value=result_mock)
    monkeypatch.setattr("fotoobo.fortinet.fortigate.FortiGate.api_get", api_get_mock)
    save_raw_mock = Mock(return_value=True)
    monkeypatch.setattr("fotoobo.helpers.result.Result.save_raw", save_raw_mock)

    # Act
    result = get_cmdb_firewall_addrgrp("test_fgt_1", "", "", "test.json")

    # Assert
    data = result.get_result("test_fgt_1")
    assert len(data) == 2
    assert data[0]["content"] == "member_1\nmember_2"
    assert data[1]["content"] == "member_3\nmember_4"
    api_get_mock.assert_called_with(url="/cmdb/firewall/addrgrp/", vdom="")
    save_raw_mock.assert_called_with(file=Path("test.json"), key="test_fgt_1")
