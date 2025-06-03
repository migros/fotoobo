"""
Testing the cli app
"""

# pylint: disable=redefined-outer-name
from typing import Generator, List
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


@pytest.fixture
def fix_config() -> Generator[None, None, None]:
    """
    This fixture is used to fix a broken config after a test.

    Whenever a test is invoked which uses a broken config all subsequent test would fail because
    of that broken config. This fixture is here to load a valid config again."""
    yield
    runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet"])


@pytest.fixture
def greet_string() -> str:
    """The string printed when the hidden command greet is used"""
    string = "🌼Aloha🌼, ⚽Hola⚽, ✨Bonjour✨, ⚡Hallo⚡,"
    string += " ☀Ciao☀, 🌟Konnichiwa🌟, 🎉Howdy-doody🎉!"
    return string


def test_cli_app_no_args() -> None:
    """Test main cli without issuing any arguments"""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage: root [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "--help" in result.stdout
    assert "The Fortinet Toolbox (fotoobo)" in result.stdout


def test_cli_app_help(help_args: str) -> None:
    """Test main cli help"""
    args = ["-c", "tests/fotoobo.yaml"]
    args.append(help_args)
    result = runner.invoke(app, args)
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
def test_cli_app_get_version(cli_call: List[str]) -> None:
    """Test main cli command: get version"""
    result = runner.invoke(app, cli_call)
    assert result.exit_code == 0
    assert "fotoobo version" in result.stdout
    assert "typer" not in result.stdout


def test_cli_app_get_inventory(monkeypatch: MonkeyPatch) -> None:
    """Test main cli command: show inventory"""
    monkeypatch.setattr(
        "fotoobo.inventory.inventory.load_yaml_file",
        MagicMock(return_value={"dummy": {"hostname": "dummy.local"}}),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "inventory"])
    assert result.exit_code == 0
    assert "fotoobo inventory" in result.stdout


def test_cli_app_greet(greet_string: str) -> None:
    """Test cli app greet"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet"])
    assert result.exit_code == 0
    assert greet_string in result.stdout


def test_cli_app_greet_alice(greet_string: str) -> None:
    """Test cli app greet alice"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet", "Alice"])
    assert result.exit_code == 0
    assert "Hi Alice, " + greet_string in result.stdout


def test_cli_app_greet_with_bye(greet_string: str) -> None:
    """Test cli app greet with option --bye set"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet", "-b"])
    assert result.exit_code == 0
    assert greet_string in result.stdout
    assert "Good Bye" in result.stdout


def test_cli_app_greet_help(help_args: str) -> None:
    """Test cli help for greet"""
    args = ["-c", "tests/fotoobo.yaml", "greet"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"name"}
    assert options == {"-b", "--bye", "-l", "--log", "-h", "--help"}
    assert not commands


def test_cli_main_logging() -> None:
    """test the logging switch"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "greet"])
    assert result.exit_code == 0


def test_cli_main_logging_log_level() -> None:
    """test the log level setting"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "--loglevel", "INFO", "greet"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "--loglevel", "DUMMY", "greet"])
    assert result.exit_code == 1


def test_cli_main_logo() -> None:
    """test the logo presence"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "version"])
    assert result.exit_code == 0
    assert " f o t o o b o " in result.stdout


def test_cli_main_no_logo() -> None:
    """test the logo absence with --nologo"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "--nologo", "get", "version"])
    assert result.exit_code == 0
    assert not " f o t o o b o " in result.stdout


def test_cli_main_broken(fix_config: None) -> None:  # pylint: disable=unused-argument
    """Test when invoking with broken fotoobo.yaml config"""
    result = runner.invoke(app, ["-c", "tests/fotoobo_broken.yaml", "greet"])
    assert result.exit_code == 1
