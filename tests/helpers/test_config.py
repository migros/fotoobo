"""
Test the config helper
"""
import os
from pathlib import Path
from typing import Callable, Optional, Union
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions.exceptions import GeneralError
from fotoobo.helpers.config import Config


class TestConfig:
    """Test the config dataclass"""

    @staticmethod
    def test_config() -> None:
        """test the default config settings"""
        config = Config()
        assert config.inventory_file == Path("inventory.yaml")
        assert not config.logging
        assert not config.audit_logging
        assert not config.no_logo

    @staticmethod
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
    def test_load_configuration(
        config_file: Optional[Path],
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

    @staticmethod
    @pytest.mark.parametrize(
        "env,yaml,expected",
        (
            pytest.param(True, True, "from_env", id="env and yaml set"),
            pytest.param(True, False, "from_env", id="only env set"),
            pytest.param(False, True, "from_yaml", id="only yaml set"),
            pytest.param(False, False, "from_yaml", id="env and yaml not set"),
        ),
    )
    def test_config_vault(env: bool, yaml: bool, expected: str, monkeypatch: MonkeyPatch) -> None:
        """Test the vault part of the configuration"""
        test_config = Config()
        vault_config = {
            "url": "https://vault.local",
            "namespace": "vault_namespace",
            "data_path": "/v1/kv/data/fotoobo",
        }
        if yaml:
            vault_config["role_id"] = "role_id_from_yaml"
            vault_config["secret_id"] = "secret_id_from_yaml"

        monkeypatch.setattr(
            "fotoobo.helpers.config.load_yaml_file", MagicMock(return_value={"vault": vault_config})
        )

        if env:
            os.environ["FOTOOBO_VAULT_ROLE_ID"] = "role_id_from_env"
            os.environ["FOTOOBO_VAULT_SECRET_ID"] = "secret_id_from_env"

        else:
            os.environ.pop("FOTOOBO_VAULT_ROLE_ID", True)
            os.environ.pop("FOTOOBO_VAULT_SECRET_ID", True)

        if env or yaml:
            test_config.load_configuration(Path("tests/fotoobo.yaml"))
            assert test_config.vault["url"] == "https://vault.local"
            assert test_config.vault["role_id"].endswith(expected)

        else:
            with pytest.raises(GeneralError, match=r"Missing vault configuration data:.*"):
                test_config.load_configuration(Path("tests/fotoobo.yaml"))
