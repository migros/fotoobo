"""
Testing the cli app
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fmg_help() -> None:
    """Test cli help for fmg"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"assign", "get", "post"}


def test_cli_app_fmg_assign_help() -> None:
    """Test cli help for fmg assign"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "assign", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"adoms", "host", "policy"}
    assert options == {"-h", "--help", "-s", "--smtp", "-t", "--timeout"}
    assert not commands


def test_cli_app_fmg_post_help() -> None:
    """Test cli help for fmg post"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "post", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"file", "adom", "host"}
    assert options == {"-h", "--help"}
    assert not commands
