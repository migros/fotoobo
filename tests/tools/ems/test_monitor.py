"""Test ems tools monitor module"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.tools.ems import monitor
from tests.helper import ResponseMock


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


@pytest.fixture(autouse=True)
def faz_login(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiClient EMS Login to always return 200 without to really login"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.login",
        MagicMock(return_value=200),
    )


def test_connections(monkeypatch: MonkeyPatch) -> None:
    """Test connections"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": [
                        {"token": "offlineNominal", "value": 1111, "name": "Offline"},
                        {"token": "offlineRecent", "value": 2222, "name": "Offline >1h"},
                        {"token": "online", "value": 3333, "name": "Online"},
                    ],
                }
            )
        ),
    )
    result = monitor.connections("test_ems")
    data = result.get_result("test_ems")
    assert data["data"][0]["token"] == "offlineNominal"
    assert data["data"][0]["value"] == 1111
    assert data["fotoobo"]["offlineNominal"] == 1111
    assert data["fotoobo"]["offlineRecent"] == 2222
    assert data["fotoobo"]["online"] == 3333


def test_endpoint_management_status(monkeypatch: MonkeyPatch) -> None:
    """Test endpoint_management_status"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": [
                        {"token": "managed", "value": 1000, "name": "Managed"},
                        {"token": "unmanaged", "value": 99, "name": "Unmanaged"},
                    ],
                }
            )
        ),
    )
    result = monitor.endpoint_management_status("test_ems")
    data = result.get_result("test_ems")
    assert data["data"][0]["token"] == "managed"
    assert data["data"][0]["value"] == 1000
    assert data["data"][1]["token"] == "unmanaged"
    assert data["data"][1]["value"] == 99
    assert data["fotoobo"]["managed"] == 1000
    assert data["fotoobo"]["unmanaged"] == 99


def test_endpoint_online_outofsync(monkeypatch: MonkeyPatch) -> None:
    """Test endpoint_management_status"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": {
                        "endpoints": [{"device_id": 666, "name": "dummy_device_name"}],
                        "total": 999,
                    },
                }
            )
        ),
    )
    result = monitor.endpoint_online_outofsync("test_ems")
    data = result.get_result("test_ems")
    assert data["fotoobo"]["outofsync"] == 999


def test_endpoint_os_versions(monkeypatch: MonkeyPatch) -> None:
    """Test endpoint_os_versions"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": [
                        {"token": "dummy_os_1", "name": "dummy_ver_1", "value": 333},
                        {"token": "dummy_os_2", "name": "dummy_ver_2", "value": 444},
                    ],
                }
            )
        ),
    )
    result = monitor.endpoint_os_versions("test_ems")
    data = result.get_result("test_ems")
    assert data["fotoobo"]["fctversionwindows"] == 777
    assert data["fotoobo"]["fctversionmac"] == 777
    assert data["fotoobo"]["fctversionlinux"] == 777


def test_system(monkeypatch: MonkeyPatch) -> None:
    """Test system

    To make it shorter this tests omits the following FortiClient EMS features in the mocked
    response:
        chromebook, ztna, epp, sase, ztna_user, epp_user, sase_user, vpn_only
    """
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": "System info retrieved successfully."},
                    "data": {
                        "name": "dummy_hostname",
                        "system_time": "2066-06-06 06:06:06",
                        "license": {
                            "sn": "FCTEMS0000000000",
                            "hid": "00000000-0000-0000-0000-000000000000-00000000",
                            "seats": {"fabric_agent": 1001, "sandbox_cloud": 1002},
                            "future_seats": {"fabric_agent": 1001, "sandbox_cloud": 1002},
                            "licenses": [
                                {
                                    "expiry_date": "2099-01-01T00:00:00",
                                    "start_date": "2098-01-01T00:00:00",
                                    "type": "fabric_agent",
                                },
                            ],
                            "is_trial": False,
                            "license_ver": 0,
                            "future_ver": 0,
                            "error": None,
                            "used": {"fabric_agent": 1001, "sandbox_cloud": 1002},
                        },
                    },
                }
            )
        ),
    )
    result = monitor.system("test_ems")
    data = result.get_result("test_ems")
    assert data["name"] == "dummy_hostname"
    assert data["license"]["seats"]["fabric_agent"] == 1001


def test_license(monkeypatch: MonkeyPatch) -> None:
    """Test license

    To make it shorter this tests omits the following FortiClient EMS features in the mocked
    response:
        chromebook, ztna, epp, sase, ztna_user, epp_user, sase_user, vpn_only
    """
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": {
                        "sn": "FCTEMS0000000000",
                        "hid": "00000000-0000-0000-0000-000000000000-00000000",
                        "seats": {"fabric_agent": 1000, "sandbox_cloud": 2000},
                        "future_seats": {"fabric_agent": 1000, "sandbox_cloud": 2000},
                        "licenses": [
                            {
                                "expiry_date": "2099-01-01T00:00:00",
                                "start_date": "2098-01-01T00:00:00",
                                "type": "fabric_agent",
                            },
                        ],
                        "is_trial": False,
                        "license_ver": 0,
                        "future_ver": 0,
                        "error": None,
                        "vdom_seats": {"fabric_agent": 1000, "sandbox_cloud": 2000},
                        "used": {
                            "fabric_agent": 100,
                            "sandbox_cloud": 400,
                        },
                    },
                }
            )
        ),
    )
    result = monitor.license("test_ems")
    data = result.get_result("test_ems")
    assert data["data"]["sn"] == "FCTEMS0000000000"
    assert data["fotoobo"]["fabric_agent_usage"] == 10
    assert data["fotoobo"]["sandbox_cloud_usage"] == 20
    assert data["fotoobo"]["license_expiry_days"] > 0
