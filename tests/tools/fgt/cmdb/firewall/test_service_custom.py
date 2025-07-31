"""
Test fgt cmdb firewall service custom.
"""

# mypy: disable-error-code=attr-defined

from pathlib import Path
from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.fgt.cmdb.firewall import get_cmdb_firewall_service_custom


def test_get_cmdb_firewall_service_custom(monkeypatch: MonkeyPatch) -> None:
    """
    Test the get cmdb firewall service custom method.
    """

    # Arrange
    result_mock = [
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
    ]
    api_get_mock = Mock(return_value=result_mock)
    monkeypatch.setattr("fotoobo.fortinet.fortigate.FortiGate.api_get", api_get_mock)
    save_raw_mock = Mock(return_value=True)
    monkeypatch.setattr("fotoobo.helpers.result.Result.save_raw", save_raw_mock)

    # Act
    result = get_cmdb_firewall_service_custom("test_fgt_1", "", "", "test.json")

    # Assert
    data = result.get_result("test_fgt_1")
    assert len(data) == 5
    assert data[0]["data_1"] == "88"
    assert data[1]["data_1"] == "8"
    assert data[2]["data_1"] == "8"
    assert data[3]["data_1"] == "89"
    assert data[4]["data_1"] == ""
    api_get_mock.assert_called_with(url="/cmdb/firewall.service/custom/", vdom="")
    save_raw_mock.assert_called_with(file=Path("test.json"), key="test_fgt_1")
