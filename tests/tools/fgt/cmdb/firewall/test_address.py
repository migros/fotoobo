"""
Test fgt cmdb firewall address
"""

# pylint: disable=no-member
# mypy: disable-error-code=attr-defined
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

import fotoobo
from fotoobo.tools.fgt.cmdb.firewall import get_cmdb_firewall_address


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


def test_get_cmdb_firewall_address(monkeypatch: MonkeyPatch) -> None:
    """Test the get cmdb firewall address method"""
    result_mock = [
        {
            "results": [
                {
                    "name": "dummy_1",
                    "type": "fqdn",
                    "fqdn": "dummy.local",
                },
                {
                    "name": "dummy_2",
                    "type": "geography",
                    "country": "dummy-country",
                },
                {
                    "name": "dummy_3",
                    "type": "ipmask",
                    "subnet": "1.1.1.1 2.2.2.2",
                },
                {
                    "name": "dummy_4",
                    "type": "iprange",
                    "start-ip": "1.1.1.1",
                    "end-ip": "2.2.2.2",
                },
                {
                    "name": "dummy_5",
                    "type": "dummy-type",
                },
            ],
            "vdom": "vdom_1",
        }
    ]
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.api_get", MagicMock(return_value=result_mock)
    )
    monkeypatch.setattr("fotoobo.helpers.result.Result.save_raw", MagicMock(return_value=True))
    result = get_cmdb_firewall_address("test_fgt_1", "", "", "test.json")
    data = result.get_result("test_fgt_1")
    assert len(data) == 5
    assert data[0]["content"] == "dummy.local"
    assert data[1]["content"] == "dummy-country"
    assert data[2]["content"] == "1.1.1.1/2.2.2.2"
    assert data[3]["content"] == "1.1.1.1 - 2.2.2.2"
    assert data[4]["content"] == ""
    fotoobo.fortinet.fortigate.FortiGate.api_get.assert_called_with(
        url="/cmdb/firewall/address/", vdom=""
    )
    fotoobo.helpers.result.Result.save_raw.assert_called_with(
        file=Path("test.json"), key="test_fgt_1"
    )
