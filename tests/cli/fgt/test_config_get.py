"""
Testing the cli fgt config get.
"""

import pytest
from typer.testing import CliRunner

from fotoobo.cli.main import app
from fotoobo.exceptions.exceptions import GeneralWarning
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_config_get_help(help_args_with_none: str) -> None:
    """
    Test cli help for fgt config get help.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "fgt", "config", "get"]
    args.append(help_args_with_none)
    args = list(filter(None, args))

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code in [0, 2]
    assert "Usage: root fgt config get" in result.stdout
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"configuration", "scope", "path"}
    assert options == {"-h", "--help"}
    assert not commands


@pytest.mark.parametrize(
    "file",
    (
        pytest.param("tests/data/fortigate_config_single.conf", id="single"),
        pytest.param("tests/data/fortigate_config_vdom.conf", id="vdom"),
    ),
)
def test_cli_app_fgt_config_get(file: str) -> None:
    """
    Test fgt config get.
    """

    # Act
    result = runner.invoke(
        app,
        ["-c", "tests/fotoobo.yaml", "fgt", "config", "get", file, "global", "/"],
    )

    # Assert
    assert result.exit_code == 0
    assert "option_2" in result.stdout
    assert "value_2" in result.stdout


@pytest.mark.parametrize(
    "file",
    (
        pytest.param("tests/data/fortigate_config_single.conf", id="single"),
        pytest.param("tests/data/fortigate_config_vdom.conf", id="vdom"),
    ),
)
def test_cli_app_fgt_config_get_no_path(file: str) -> None:
    """
    Test fgt config get with no path supplied.
    """

    # Act
    result = runner.invoke(
        app,
        ["-c", "tests/fotoobo.yaml", "fgt", "config", "get", file, "global"],
    )

    # Assert
    assert result.exit_code == 0
    assert "option_2" in result.stdout
    assert "value_2" in result.stdout


def test_cli_app_fgt_config_get_empty_config() -> None:
    """
    Test cli options and commands for fgt config get with an empty configuration.
    """

    # Act & Assert
    with pytest.raises(GeneralWarning, match=r"There is no info in"):
        runner.invoke(
            app,
            [
                "-c",
                "tests/fotoobo.yaml",
                "fgt",
                "config",
                "get",
                "tests/data/fortigate_config_empty.conf",
                "global",
            ],
            catch_exceptions=False,
        )


def test_cli_app_fgt_config_get_noexist_config_file() -> None:
    """
    Test cli options and commands for fgt config get with an nonexisting configuration.
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
                "get",
                "tests/data/fortigate_config_noexist.conf",
                "global",
                "/",
            ],
            catch_exceptions=False,
        )


def test_cli_app_fgt_config_get_dir() -> None:
    """
    Test cli fgt config get if a directory without configuration files is given.
    """

    # Act & Assert
    with pytest.raises(GeneralWarning, match=r"There is no info in"):
        runner.invoke(
            app,
            ["-c", "tests/fotoobo.yaml", "fgt", "config", "get", "tests/data", "global", "/"],
            catch_exceptions=False,
        )
