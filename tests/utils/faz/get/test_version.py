"""Test utils faz get version"""


from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralWarning
from fotoobo.utils.faz.get import version


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr("fotoobo.helpers.config.config.inventory_file", "tests/data/inventory.yaml")


@pytest.fixture(autouse=True)
def faz_login(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiAnalyzer Login to always return 200 without to really login"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortianalyzer.FortiAnalyzer.login",
        MagicMock(return_value=200),
    )


@pytest.fixture(autouse=True)
def faz_logout(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiAnalyzer Login to always return 200 without to really logout"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortianalyzer.FortiAnalyzer.logout",
        MagicMock(return_value=200),
    )


def test_version(monkeypatch: MonkeyPatch) -> None:
    """Test get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortianalyzer.FortiAnalyzer.get_version",
        MagicMock(return_value="1.1.1"),
    )
    data = version("test_faz")
    assert data == {"host": "test_faz", "version": "1.1.1"}
