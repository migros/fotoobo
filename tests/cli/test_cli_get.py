"""
Testing the cli get app
"""


from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_get_no_args() -> None:
    """Test get cli without issuing any arguments"""
    result = runner.invoke(app, ["get"])
    assert result.exit_code == 2
    assert "Usage: callback get [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "Try 'callback get -h' for help." in result.stdout
    assert "Error" in result.stdout
    assert "Missing command" in result.stdout


def test_cli_get_help() -> None:
    """Test cli help for get"""
    result = runner.invoke(app, ["get", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"commands", "inventory", "version"}


def test_cli_get_commands_help() -> None:
    """Test cli help for get commands"""
    result = runner.invoke(app, ["get", "commands", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_get_inventory_help() -> None:
    """Test cli help for get inventory"""
    result = runner.invoke(app, ["get", "inventory", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_get_version_help() -> None:
    """Test cli help for get version"""
    result = runner.invoke(app, ["get", "version", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help", "-v"}
    assert not commands
