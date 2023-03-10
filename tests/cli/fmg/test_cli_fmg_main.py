"""
Testing the cli app
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fmg_help() -> None:
    """Test cli help for fmg"""
    result = runner.invoke(app, ["fmg", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"assign", "get", "set"}


def test_cli_app_fmg_assign_help() -> None:
    """Test cli help for fmg assign"""
    result = runner.invoke(app, ["fmg", "assign", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host", "adoms"}
    assert options == {"-h", "--help", "-t", "--timeout"}
    assert not commands


def test_cli_app_fmg_set_help() -> None:
    """Test cli help for fmg set"""
    result = runner.invoke(app, ["fmg", "set", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host", "file", "adom"}
    assert options == {"-h", "--help"}
    assert not commands
