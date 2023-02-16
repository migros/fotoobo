"""Test utils fotoobo get"""

from typing import Any
from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch

from fotoobo.helpers.config import config
from fotoobo.utils.get import commands, inventory, version


def test_get_commands(capsys: Any) -> None:
    """Test get commands"""
    config.cli_info = {
        "info_name": "fotoobo",
        "command": {
            "commands": {
                "level1cmd1": {
                    "commands": {},
                    "help": "help1_1\n\nhelp1_2",
                    "hidden": False,
                    "name": "level1cmd1",
                },
                "level1cmd2": {
                    "commands": {},
                    "help": "help2_1\n\nhelp2_2",
                    "hidden": True,
                    "name": "level1cmd2",
                },
            }
        },
    }
    commands()
    out, _ = capsys.readouterr()
    assert "─ cli commands structure ─╮" in out
    assert "│ fotoobo" in out
    assert "─ level1cmd1" in out
    assert "─ level1cmd2" not in out
    assert "help1_1" in out
    assert "help1_2" not in out


def test_get_inventory(capsys: Any, monkeypatch: MonkeyPatch) -> None:
    """Test get inventory"""
    monkeypatch.setattr(
        "fotoobo.inventory.inventory.load_yaml_file",
        MagicMock(
            return_value={
                "dummy_1": {"hostname": "name_1"},
                "dummy_2": {"hostname": "name_2", "type": "type_2"},
            }
        ),
    )
    inventory()
    out, _ = capsys.readouterr()
    assert "fotoobo inventory" in out
    assert "dummy_1 │ name_1" in out
    assert "dummy_2 │ name_2   │ type_2" in out


def test_get_version(capsys: Any) -> None:
    """Test get version"""
    version()
    out, _ = capsys.readouterr()
    assert "fotoobo version" in out


def test_get_version_verbose(capsys: Any) -> None:
    """Test get version with verbose level set"""
    version(True)
    out, _ = capsys.readouterr()
    assert "fotoobo version" in out
    assert "typer" in out
