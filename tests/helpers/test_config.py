"""
Test the config helper
"""
from typing import Callable, Union
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.helpers.config import Config


class TestConfig:
    """Test the config dataclass"""

    def test_config(self) -> None:
        """test the default config settings"""
        config = Config()
        assert config.inventory_file == Path("inventory.yaml")
        assert not config.logging
        assert not config.audit_logging
        assert not config.no_logo

    @pytest.mark.parametrize(
        "config_file,isfile_mock,load_yaml_file_mock,expected_inventory",
        (
            pytest.param(
                None,
                MagicMock(return_value=False),
                MagicMock(return_value=None),
                Path("inventory.yaml"),
                id="No config file given",
            ),
            pytest.param(
                Path("test/fotoobo.yaml"),
                MagicMock(return_value=True),
                MagicMock(return_value={"inventory": "test1", "logging": {"enabled": True}}),
                Path("test/test1"),
                id="Custom fotoobo.yaml",
            ),
            pytest.param(
                None,
                lambda file: file == Path("fotoobo.yaml"),
                MagicMock(return_value={"inventory": "/test2", "audit_logging": {"enabled": True}}),
                Path("/test2"),
                id="Use fotoobo.yaml in current directory",
            ),
            pytest.param(
                None,
                lambda file: file != Path("fotoobo.yaml"),
                MagicMock(return_value={"inventory": "test3"}),
                Path("~/.config/test3").expanduser(),
                id="Use fotoobo.yaml in .config/fotoobo.yaml",
            ),
        ),
    )
    # pylint: disable=too-many-arguments
    def test_load_configuration(
        self,
        config_file: Union[Path, None],
        isfile_mock: Union[MagicMock, Callable[[str], bool]],
        load_yaml_file_mock: MagicMock,
        expected_inventory: Path,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """test load configuration from file"""
        monkeypatch.setattr("fotoobo.helpers.files.Path.is_file", isfile_mock)
        monkeypatch.setattr("fotoobo.helpers.config.load_yaml_file", load_yaml_file_mock)
        config = Config()
        config.load_configuration(config_file)
        assert config.inventory_file == expected_inventory
