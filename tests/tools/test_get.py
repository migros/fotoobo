"""Test fotoobo get tools"""

from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from rich.tree import Tree

from fotoobo.tools.get import commands, inventory, version


def test_get_commands(monkeypatch: MonkeyPatch) -> None:
    """Test get commands"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.cli_info",
        {
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
        },
    )

    result = commands().get_result("commands")

    assert isinstance(result, Tree)
    assert "level1cmd1" in result.children[0].label.plain  # type: ignore
    assert "help1_1" in result.children[0].label.plain  # type: ignore


def test_get_inventory(monkeypatch: MonkeyPatch) -> None:
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
    result = inventory().get_result("inventory")

    assert isinstance(result, list)
    assert result[0]["host"] == "dummy_1"
    assert result[1]["host"] == "dummy_2"
    assert result[1]["hostname"] == "name_2"


def test_get_version() -> None:
    """Test get version"""
    result = version().get_result("version")

    assert len(result) == 1
    assert result[0]["module"] == "fotoobo"


def test_get_version_verbose() -> None:
    """Test get version with verbose level set"""
    result = version(True).get_result("version")

    assert len(result) >= 1

    version_keys = []
    for entry in result:
        version_keys.append(entry["module"])

    assert "jinja2" in version_keys
    assert "rich" in version_keys
    assert "requests" in version_keys
    assert "PyYAML" in version_keys
    assert "typer" in version_keys
