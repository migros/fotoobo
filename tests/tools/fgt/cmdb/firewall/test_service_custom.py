"""
Test fgt cmdb firewall service custom
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
from fotoobo.tools.fgt.cmdb.firewall import get_cmdb_firewall_service_custom


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


def test_get_cmdb_firewall_service_custom(monkeypatch: MonkeyPatch) -> None:
    """Test the get cmdb firewall service custom method"""
    result_mock = Result[list[Any]]()
    result_mock.push_result(
        "test_fgt_1",
        [
            {
                "results": [
                    {
                        "name": "dummy_1",
                        "protocol": "TCP/UDP/SCTP",
                        "tcp-portrange": "88",
                        "udp-portrange": "99",
                    },
                    {
                        "name": "dummy_2",
                        "protocol": "ICMP",
                        "icmptype": "8",
                        "icmpcode": "9",
                    },
                    {
                        "name": "dummy_3",
                        "protocol": "ICMP6",
                        "icmptype": "8",
                        "icmpcode": "9",
                    },
                    {
                        "name": "dummy_4",
                        "protocol": "IP",
                        "protocol-number": "89",
                    },
                    {
                        "name": "dummy_5",
                        "protocol": "dummy-type",
                    },
                ],
                "vdom": "vdom_1",
            }
        ],
    )
    monkeypatch.setattr(
        "fotoobo.tools.fgt.cmdb.firewall.service_custom.api_get",
        MagicMock(return_value=result_mock),
    )
    monkeypatch.setattr("fotoobo.helpers.result.Result.save_raw", MagicMock(return_value=True))
    result = get_cmdb_firewall_service_custom("test_fgt_1", "", "", "test.json")
    data = result.get_result("test_fgt_1")
    assert len(data) == 5
    assert data[0]["data_1"] == "88"
    assert data[1]["data_1"] == "8"
    assert data[2]["data_1"] == "8"
    assert data[3]["data_1"] == "89"
    assert data[4]["data_1"] == ""
    fotoobo.tools.fgt.cmdb.firewall.service_custom.api_get.assert_called_with(
        host="test_fgt_1", vdom="", url="/cmdb/firewall.service/custom/"
    )
    fotoobo.helpers.result.Result.save_raw.assert_called_with(
        file=Path("test.json"), key="test_fgt_1"
    )
