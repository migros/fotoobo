"""
Test fotoobo.tools.fgt.backup
"""

from pathlib import Path
from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import APIError
from fotoobo.tools.fgt import backup


def test_backup_all(monkeypatch: MonkeyPatch) -> None:
    """
    Test fgt backup with no 'hosts' so all FortiGates are backed up
    """
    test_config = "#config-version\ntest"

    monkeypatch.setattr(
        "fotoobo.tools.fgt.main.config.inventory_file", Path("tests/data/inventory.yaml")
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(return_value=test_config),
    )

    result = backup()

    all_results = result.all_results()
    assert len(all_results) == 2
    assert all_results["test_fgt_1"] == test_config
    assert all_results["test_fgt_2"] == test_config

    assert len(result.messages) == 2
    assert len(result.messages["test_fgt_1"]) == 1
    message = result.messages["test_fgt_1"][0]
    assert message["level"] == "info"
    assert "succeeded" in message["message"]

    assert len(result.messages["test_fgt_2"]) == 1
    message = result.messages["test_fgt_2"][0]
    assert message["level"] == "info"
    assert "succeeded" in message["message"]


def test_backup_single(monkeypatch: MonkeyPatch) -> None:
    """
    Test fgt backup single FortiGate
    """
    test_config = "#config-version\ntest"

    monkeypatch.setattr(
        "fotoobo.tools.fgt.main.config.inventory_file", Path("tests/data/inventory.yaml")
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(return_value=test_config),
    )

    result = backup("test_fgt_1")

    all_results = result.all_results()
    assert len(all_results) == 1
    assert all_results["test_fgt_1"] == test_config

    assert len(result.messages["test_fgt_1"]) == 1
    message = result.messages["test_fgt_1"][0]
    assert message["level"] == "info"
    assert "succeeded" in message["message"]


def test_backup_single_with_invalid_config(monkeypatch: MonkeyPatch) -> None:
    """
    Test fgt backup single FortiGate
    """
    test_config = '{"http_status": "456"}'
    monkeypatch.setattr(
        "fotoobo.tools.fgt.main.config.inventory_file", Path("tests/data/inventory.yaml")
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(return_value=test_config),
    )

    result = backup("test_fgt_1")

    all_results = result.all_results()
    assert len(all_results) == 1
    assert all_results["test_fgt_1"] == test_config

    assert len(result.messages["test_fgt_1"]) == 1
    message = result.messages["test_fgt_1"][0]
    assert message["level"] == "error"
    assert "failed" in message["message"]


def test_backup_api_error(monkeypatch: MonkeyPatch) -> None:
    """
    Test fgt backup with an API error
    """
    monkeypatch.setattr(
        "fotoobo.tools.fgt.main.config.inventory_file", Path("tests/data/inventory.yaml")
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(side_effect=APIError("dummy error")),
    )

    result = backup("test_fgt_2")

    all_results = result.all_results()
    assert len(all_results) == 1
    assert not all_results["test_fgt_2"]

    assert len(result.messages["test_fgt_2"]) == 1
    message = result.messages["test_fgt_2"][0]
    assert message["level"] == "error"
    assert "test_fgt_2 returned unknown" in message["message"]
