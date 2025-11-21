"""
Test the config helper.
"""

import os
from pathlib import Path
from typing import Any, Callable
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from fotoobo.exceptions.exceptions import GeneralError
from fotoobo.helpers.config import Config


class TestConfig:
    """
    Test the config dataclass.
    """

    @staticmethod
    def test_config() -> None:
        """
        Test the default config settings.
        """

        # Act
        config = Config()

        # Assert
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
                Mock(return_value=False),
                Mock(return_value=None),
                Path("inventory.yaml"),
                id="No config file given",
            ),
            pytest.param(
                Path("test/fotoobo.yaml"),
                Mock(return_value=True),
                Mock(return_value={"inventory": "test1", "logging": {"enabled": True}}),
                Path("test/test1"),
                id="Custom fotoobo.yaml",
            ),
            pytest.param(
                None,
                lambda file: file == Path("fotoobo.yaml"),
                Mock(return_value={"inventory": "/test2", "audit_logging": {"enabled": True}}),
                Path("/test2"),
                id="Use fotoobo.yaml in current directory",
            ),
            pytest.param(
                None,
                lambda file: file != Path("fotoobo.yaml"),
                Mock(return_value={"inventory": "test3"}),
                Path("~/.config/test3").expanduser(),
                id="Use fotoobo.yaml in .config/fotoobo.yaml",
            ),
        ),
    )
    def test_load_configuration(
        config_file: Path | None,
        isfile_mock: Mock | Callable[[str], bool],
        load_yaml_file_mock: Mock,
        expected_inventory: Path,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Test load configuration from file.
        """

        # Arrange
        monkeypatch.setattr("fotoobo.helpers.files.Path.is_file", isfile_mock)
        monkeypatch.setattr("fotoobo.helpers.config.load_yaml_file", load_yaml_file_mock)
        config = Config()

        # Act
        config.load_configuration(config_file)

        # Assert
        assert config.inventory_file == expected_inventory

    @staticmethod
    @pytest.mark.parametrize(
        "logging_type",
        (
            pytest.param("logging", id="logging"),
            (pytest.param("audit_logging", id="audit_logging")),
        ),
    )
    @pytest.mark.parametrize(
        "logging,expected",
        (
            pytest.param(
                None, r"Setting (audit_)?logging has to be a dictionary", id="*logging is None"
            ),
            pytest.param(
                {"log_file": None},
                r"Setting (audit_)?logging.log_file has to be a dictionary",
                id="Log_file is None",
            ),
            pytest.param(
                {"log_file": {"name": None}},
                r"Missing (audit_)?logging.log_file configuration: name",
                id="Empty log_file.name",
            ),
            pytest.param(
                {"log_file": {"dummy": None}},
                r"Missing (audit_)?logging.log_file configuration: name",
                id="Missing log_file.name",
            ),
            # pytest.param(False, False, "from_yaml", id="env and yaml not set"),
        ),
    )
    def test_config_logging(
        logging_type: str,
        logging: dict[str, Any] | None,
        expected: str,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Test load logging or audit_logging configuration with errors.
        """

        # Arrange
        test_config = Config()
        monkeypatch.setattr(
            "fotoobo.helpers.config.load_yaml_file", Mock(return_value={logging_type: logging})
        )

        # Act & Assert
        with pytest.raises(GeneralError, match=expected):
            test_config.load_configuration(Path("tests/fotoobo.yaml"))

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
        """
        Test the vault part of the configuration.
        """

        # Arrange
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
            "fotoobo.helpers.config.load_yaml_file", Mock(return_value={"vault": vault_config})
        )

        # Act
        if env:
            os.environ["FOTOOBO_VAULT_ROLE_ID"] = "role_id_from_env"
            os.environ["FOTOOBO_VAULT_SECRET_ID"] = "secret_id_from_env"

        else:
            os.environ.pop("FOTOOBO_VAULT_ROLE_ID", True)
            os.environ.pop("FOTOOBO_VAULT_SECRET_ID", True)

        # Assert
        if env or yaml:
            test_config.load_configuration(Path("tests/fotoobo.yaml"))
            assert test_config.vault["url"] == "https://vault.local"
            assert test_config.vault["role_id"].endswith(expected)

        else:
            with pytest.raises(GeneralError, match=r"Missing vault configuration:.*"):
                test_config.load_configuration(Path("tests/fotoobo.yaml"))
