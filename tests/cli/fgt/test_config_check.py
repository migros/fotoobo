"""
Testing the cli fgt config check.
"""

from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from fotoobo.exceptions.exceptions import GeneralError, GeneralWarning
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_config_check_help(help_args_with_none: str) -> None:
    """
    Test cli help for fgt config check help.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "fgt", "config", "check"]
    args.append(help_args_with_none)
    args = list(filter(None, args))

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code in [0, 2]
    assert "Usage: root fgt config check" in result.stdout
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"configuration", "bundles"}
    assert options == {"-h", "--help", "--smtp"}
    assert not commands


def test_cli_app_fgt_config_check() -> None:
    """
    Test fgt config check.
    """

    # Act
    result = runner.invoke(
        app,
        [
            "-c",
            "tests/fotoobo.yaml",
            "fgt",
            "config",
            "check",
            "tests/data/fortigate_config_single.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )

    # Assert
    assert result.exit_code == 0


def test_cli_app_fgt_config_check_failed(monkeypatch: MonkeyPatch) -> None:
    """
    Test fgt config check when there are failed checks.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.tools.fgt.config.load_yaml_file",
        Mock(
            return_value=[
                {
                    "type": "count",
                    "scope": "vdom",
                    "path": "/root/leaf_81/leaf_82",
                    "checks": {"eq": 100},
                }
            ]
        ),
    )

    # Act
    result = runner.invoke(
        app,
        [
            "-c",
            "tests/fotoobo.yaml",
            "fgt",
            "config",
            "check",
            "tests/data/fortigate_config_single.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )

    # Assert
    assert result.exit_code == 0


def test_cli_app_fgt_config_check_empty_config() -> None:
    """
    Test cli options and commands for fgt config check with an empty configuration.
    """

    # Act
    result = runner.invoke(
        app,
        [
            "-c",
            "tests/fotoobo.yaml",
            "fgt",
            "config",
            "check",
            "tests/data/fortigate_config_empty.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )

    # Assert
    assert result.exit_code == 0


def test_cli_app_fgt_config_check_nonexist_config_file() -> None:
    """
    Test cli options and commands for fgt config check with an nonexisting configuration.
    """

    # Act & Assert
    with pytest.raises(GeneralWarning, match=r"There are no"):
        runner.invoke(
            app,
            [
                "-c",
                "tests/fotoobo.yaml",
                "fgt",
                "config",
                "check",
                "tests/data/fortigate_config_nonexist.conf",
                "tests/data/fortigate_checks.yaml",
            ],
            catch_exceptions=False,
        )


def test_cli_app_fgt_config_check_dir() -> None:
    """
    Test cli options and commands for fgt config check if a directory is given.
    """

    # Act
    result = runner.invoke(
        app,
        [
            "-c",
            "tests/fotoobo.yaml",
            "fgt",
            "config",
            "check",
            "tests/data",
            "tests/data/fortigate_checks.yaml",
        ],
    )

    # Assert
    assert result.exit_code == 0


def test_cli_app_fgt_config_check_invalid_bundle_file() -> None:
    """
    Test cli options and commands for fgt config check with an invalid check bundle file.
    """

    # Act & Assert
    with pytest.raises(GeneralError, match=r"No valid bundle file"):
        runner.invoke(
            app,
            [
                "-c",
                "tests/fotoobo.yaml",
                "fgt",
                "config",
                "check",
                "tests/data/fortigate_config_single.conf",
                "tests/data/fortigate_checks_invalid.yaml",
            ],
            catch_exceptions=False,
        )
