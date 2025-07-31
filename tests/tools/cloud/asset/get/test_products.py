"""
Test fcasset tools get version.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.cloud.asset.get import products


def test_products(monkeypatch: MonkeyPatch) -> None:
    """
    Test get products.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloudasset.FortiCloudAsset.post",
        Mock(
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

    # Act
    result = products("forticloudasset")

    # Assert
    data = result.get_result("forticloudasset")
    assert data[0]["description"] == "dummy_fortigate"


def test_products_empty(monkeypatch: MonkeyPatch) -> None:
    """
    Test get products when there are no products in list.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloudasset.FortiCloudAsset.post",
        Mock(
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

    # Act
    result = products("forticloudasset")

    # Assert
    msg = result.get_messages("forticloudasset")
    assert msg[0]["message"] == "No product found"
