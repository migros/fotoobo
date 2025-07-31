"""
Testing the cli app.
"""

# pylint: disable=redefined-outer-name
from typing import Generator
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


@pytest.fixture
def fix_config() -> Generator[None, None, None]:
    """
    This fixture is used to fix a broken config after a test.

    Whenever a test is invoked which uses a broken config all subsequent test would fail because
    of that broken config. This fixture is here to load a valid config again.
    """

    yield

    runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet"])


@pytest.fixture
def greet_string() -> str:
    """
    The string printed when the hidden command greet is used.
    """

    string = "🌼Aloha🌼, ⚽Hola⚽, ✨Bonjour✨, ⚡Hallo⚡,"
    string += " ☀Ciao☀, 🌟Konnichiwa🌟, 🎉Howdy-doody🎉!"

    return string


def test_cli_app_no_args() -> None:
    """
    Test main cli without issuing any arguments.
    """

    # Act
    result = runner.invoke(app, [])

    # Assert
    assert result.exit_code in [0, 2]
    assert "Usage: root [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "--help" in result.stdout
    assert "The Fortinet Toolbox (fotoobo)" in result.stdout


def test_cli_app_help(help_args: str) -> None:
    """
    Test main cli help.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {
        "-c",
        "--config",
        "-h",
        "--help",
        "--install-completion",
        "--loglevel",
        "--nologo",
        "-q",
        "--quiet",
        "--show-completion",
        "-V",
        "--version",
    }
    assert set(commands) == {"convert", "ems", "faz", "cloud", "fgt", "fmg", "get"}


@pytest.mark.parametrize(
    "cli_call",
    (
        pytest.param(["-c", "tests/fotoobo.yaml", "get", "version"], id="get version"),
        pytest.param(["-c", "tests/fotoobo.yaml", "-V"], id="option -V"),
        pytest.param(["-c", "tests/fotoobo.yaml", "--version"], id="option --version"),
    ),
)
def test_cli_app_get_version(cli_call: list[str]) -> None:
    """
    Test main cli command: get version.
    """

    # Act
    result = runner.invoke(app, cli_call)

    # Assert
    assert result.exit_code == 0
    assert "fotoobo version" in result.stdout
    assert "typer" not in result.stdout


def test_cli_app_get_inventory(monkeypatch: MonkeyPatch) -> None:
    """
    Test main cli command: show inventory.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.inventory.inventory.load_yaml_file",
        Mock(return_value={"dummy": {"hostname": "dummy.local"}}),
    )

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "inventory"])

    # Assert
    assert result.exit_code == 0
    assert "fotoobo inventory" in result.stdout


def test_cli_app_greet(greet_string: str) -> None:
    """
    Test cli app greet.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet"])

    # Assert
    assert result.exit_code == 0
    assert greet_string in result.stdout


def test_cli_app_greet_alice(greet_string: str) -> None:
    """
    Test cli app greet alice.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet", "Alice"])

    # Assert
    assert result.exit_code == 0
    assert "Hi Alice, " + greet_string in result.stdout


def test_cli_app_greet_with_bye(greet_string: str) -> None:
    """
    Test cli app greet with option --bye set.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet", "-b"])

    # Assert
    assert result.exit_code == 0
    assert greet_string in result.stdout
    assert "Good Bye" in result.stdout


def test_cli_app_greet_help(help_args: str) -> None:
    """
    Test cli help for greet.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "greet"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"name"}
    assert options == {"-b", "--bye", "-l", "--log", "-h", "--help"}
    assert not commands


def test_cli_main_logging() -> None:
    """
    Test the logging switch.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet"])

    # Assert
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "level, exit_code",
    (
        pytest.param("DEBUG", 0, id="DEBUG"),
        pytest.param("INFO", 0, id="INFO"),
        pytest.param("WARNING", 0, id="WARN"),
        pytest.param("ERROR", 0, id="ERROR"),
        pytest.param("CRITICAL", 0, id="CRITICAL"),
        pytest.param("DUMMY", 1, id="DUMMY"),
        pytest.param(..., 1, id="Empty"),
    ),
)
def test_cli_main_logging_log_level(level: str, exit_code: int) -> None:
    """
    Test the log level setting.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "--loglevel", level, "greet"])

    # Assert
    assert result.exit_code == exit_code


def test_cli_main_logo() -> None:
    """
    Test the logo presence.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "version"])

    # Assert
    assert result.exit_code == 0
    assert " f o t o o b o " in result.stdout


def test_cli_main_no_logo() -> None:
    """
    Test the logo absence with --nologo.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "--nologo", "get", "version"])

    # Assert
    assert result.exit_code == 0
    assert not " f o t o o b o " in result.stdout


def test_cli_main_broken(fix_config: None) -> None:  # pylint: disable=unused-argument
    """
    Test when invoking with broken fotoobo.yaml config.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo_broken.yaml", "greet"])

    # Assert
    assert result.exit_code == 1
