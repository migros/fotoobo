"""
Test fgt cmdb firewall service group
"""

# pylint: disable=no-member
# mypy: disable-error-code=attr-defined
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

import fotoobo
from fotoobo.helpers.result import Result
from fotoobo.tools.fgt.cmdb.firewall import get_cmdb_firewall_service_group


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


def test_get_cmdb_firewall_addrgrp(monkeypatch: MonkeyPatch) -> None:
    """Test the get cmdb firewall service group method"""
    result_mock = Result[list[Any]]()
    result_mock.push_result(
        "test_fgt_1",
        [
            {
                "results": [
                    {"name": "group_1", "member": [{"name": "member_1"}, {"name": "member_2"}]},
                    {"name": "group_2", "member": [{"name": "member_3"}, {"name": "member_4"}]},
                ],
                "vdom": "vdom_1",
            }
        ],
    )
    monkeypatch.setattr(
        "fotoobo.tools.fgt.cmdb.firewall.service_group.api_get", MagicMock(return_value=result_mock)
    )
    monkeypatch.setattr("fotoobo.helpers.result.Result.save_raw", MagicMock(return_value=True))
    result = get_cmdb_firewall_service_group("test_fgt_1", "", "", "test.json")
    data = result.get_result("test_fgt_1")
    assert len(data) == 2
    assert data[0]["content"] == "member_1\nmember_2"
    assert data[1]["content"] == "member_3\nmember_4"
    fotoobo.tools.fgt.cmdb.firewall.service_group.api_get.assert_called_with(
        host="test_fgt_1", vdom="", url="/cmdb/firewall/addrgrp/"
    )
    fotoobo.helpers.result.Result.save_raw.assert_called_with(
        file=Path("test.json"), key="test_fgt_1"
    )
