"""
Test fotoobo.utils.fgt.backup
"""

from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import APIError
from fotoobo.utils.fgt import backup


def test_backup_no_backup_dir(monkeypatch: MonkeyPatch, temp_dir: str) -> None:
    """Test fgt backup without backup_dir in config"""
    monkeypatch.setattr("fotoobo.utils.fgt.main.config.inventory_file", "tests/data/inventory.yaml")
    monkeypatch.setattr("fotoobo.utils.fgt.main.create_dir", MagicMock(return_value=True))
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(return_value="#config-version\ntest"),
    )
    monkeypatch.setattr("fotoobo.utils.fgt.main.os.path.isfile", MagicMock(return_value=True))
    monkeypatch.setattr("fotoobo.utils.fgt.main.os.remove", MagicMock(return_value=True))
    backup("test_fgt_1", temp_dir)
    assert True


def test_backup_all(monkeypatch: MonkeyPatch, temp_dir: str) -> None:
    """Test fgt backup with no 'hosts' so all FortiGates are backed up"""
    monkeypatch.setattr("fotoobo.utils.fgt.main.create_dir", MagicMock(return_value=True))
    monkeypatch.setattr("fotoobo.utils.fgt.main.config.inventory_file", "tests/data/inventory.yaml")
    backup("", temp_dir)
    assert True


def test_backup_single(monkeypatch: MonkeyPatch, temp_dir: str) -> None:
    """Test fgt backup single FortiGate"""
    monkeypatch.setattr("fotoobo.utils.fgt.main.config.inventory_file", "tests/data/inventory.yaml")
    monkeypatch.setattr("fotoobo.utils.fgt.main.create_dir", MagicMock(return_value=True))
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(return_value="#config-version\ntest"),
    )
    monkeypatch.setattr("fotoobo.utils.fgt.main.os.path.isfile", MagicMock(return_value=True))
    monkeypatch.setattr("fotoobo.utils.fgt.main.os.remove", MagicMock(return_value=True))
    backup("test_fgt_1", temp_dir)
    assert True


def test_backup_single_with_invalid_config(monkeypatch: MonkeyPatch, temp_dir: str) -> None:
    """Test fgt backup single FortiGate"""
    monkeypatch.setattr("fotoobo.utils.fgt.main.config.inventory_file", "tests/data/inventory.yaml")
    monkeypatch.setattr("fotoobo.utils.fgt.main.create_dir", MagicMock(return_value=True))
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(return_value='{"http_status": "666"}'),
    )
    monkeypatch.setattr("fotoobo.utils.fgt.main.os.path.isfile", MagicMock(return_value=True))
    monkeypatch.setattr("fotoobo.utils.fgt.main.os.remove", MagicMock(return_value=True))
    backup("test_fgt_1", temp_dir)
    assert True


def test_backup_api_error(monkeypatch: MonkeyPatch, temp_dir: str) -> None:
    """Test fgt backup with an API error"""
    monkeypatch.setattr("fotoobo.utils.fgt.main.os.path.isfile", MagicMock(return_value=True))
    monkeypatch.setattr("fotoobo.utils.fgt.main.os.remove", MagicMock(return_value=True))
    monkeypatch.setattr("fotoobo.utils.fgt.main.config.inventory_file", "tests/data/inventory.yaml")
    monkeypatch.setattr("fotoobo.utils.fgt.main.create_dir", MagicMock(return_value=True))
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(side_effect=APIError("dummy error")),
    )
    backup("test_fgt_1", temp_dir)
    assert True
