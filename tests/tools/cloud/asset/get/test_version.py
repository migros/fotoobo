"""Test fcasset tools get version"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.tools.cloud.asset.get import version


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


@pytest.fixture(autouse=True)
def fc_login(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiCloudAsset login to always return 200 without to really login"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloudasset.FortiCloudAsset.login",
        MagicMock(return_value=200),
    )


def test_version(monkeypatch: MonkeyPatch) -> None:
    """Test get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloudasset.FortiCloudAsset.get_version",
        MagicMock(return_value="3.0"),
    )
    result = version("forticloudasset")
    data = result.get_result("forticloudasset")
    assert data == "3.0"
