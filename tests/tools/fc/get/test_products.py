"""Test fc tools get version"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.tools.fc.get import products


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


@pytest.fixture(autouse=True)
def fc_login(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiCloud login to always return 200 without to really login"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloud.FortiCloudAsset.login",
        MagicMock(return_value=200),
    )


def test_products(monkeypatch: MonkeyPatch) -> None:
    """Test get products"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloud.FortiCloudAsset.post",
        MagicMock(
            return_value={
                "build": "1.0.0",
                "error": None,
                "message": "Request processed successfully",
                "status": 0,
                "token": "dummy_token",
                "version": "3.0",
                "assets": [
                    {
                        "description": "dummy_fortigate",
                        "entitlements": [],
                        "isDecommissioned": False,
                        "productModel": "FortiGate 100F",
                        "registrationDate": "2025-10-20T08:09:10",
                        "serialNumber": "FG100F0123456789",
                        "assetGroups": [],
                        "contracts": [],
                        "productModelEoR": "2099-10-20T08:09:10",
                        "productModelEoS": "2099-10-20T08:09:10",
                        "accountId": 123456,
                        "folderId": 12345,
                        "folderPath": "/dummy/folder",
                        "status": "Registered",
                    }
                ],
                "pageNumber": 1,
                "totalPages": 1,
            }
        ),
    )
    result = products("forticloud")
    data = result.get_result("forticloud")
    assert data[0]["description"] == "dummy_fortigate"


def test_products_empty(monkeypatch: MonkeyPatch) -> None:
    """Test get products when there are no products in list"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloud.FortiCloudAsset.post",
        MagicMock(
            return_value={
                "build": "1.0.0",
                "error": {
                    "errorCode": 301,
                    "message": "No product found",
                },
                "message": "No product found",
                "status": 0,
                "token": "dummy_token",
                "version": "3.0",
                "assets": None,
                "pageNumber": 0,
                "totalPages": 0,
            }
        ),
    )
    result = products("forticloud")
    msg = result.get_messages("forticloud")
    assert msg[0]["message"] == "No product found"
