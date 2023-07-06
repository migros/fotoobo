"""
Test fgt tools get version
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralError, GeneralWarning
from fotoobo.tools.fgt.get import version


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


@pytest.mark.parametrize(
    "host",
    (
        pytest.param("", id="test version with no host"),
        pytest.param("test_fgt_1", id="test version with valid host"),
    ),
)
def test_version(host: str, monkeypatch: MonkeyPatch) -> None:
    """Test get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.get_version", MagicMock(return_value="1.1.1")
    )
    result = version(host)
    if host:
        assert isinstance(result.get_result(host), str)
        assert result.get_result(host) == "1.1.1"
    else:
        assert len(result.results) == 2
        assert result.get_result("test_fgt_2") == "1.1.1"


@pytest.mark.parametrize(
    "side_effect",
    (
        pytest.param(GeneralWarning("dummy message"), id="GeneralWarning"),
        pytest.param(GeneralError("dummy message"), id="GeneralError"),
    ),
)
def test_version_exception_from_fortigate(side_effect: Any, monkeypatch: MonkeyPatch) -> None:
    """Test get version with exception thrown from FortiGate module"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.get_version",
        MagicMock(side_effect=side_effect),
    )
    result = version("test_fgt_1")
    assert result.get_result("test_fgt_1") == "unknown due to dummy message"


def test_version_no_fortigates(monkeypatch: MonkeyPatch) -> None:
    """Test get version with no FortiGates in inventory"""
    monkeypatch.setattr(
        "fotoobo.tools.fgt.get.Inventory._load_inventory", MagicMock(return_value=None)
    )
    with pytest.raises(GeneralWarning, match=r"no asset of type 'fortigate' .* was found.*"):
        version("")
