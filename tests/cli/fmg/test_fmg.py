"""
Testing the cli app
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fmg_help(help_args_with_none: str) -> None:
    """Test cli help for fmg"""
    args = ["-c", "tests/fotoobo.yaml", "fmg"]
    args.append(help_args_with_none)
    args = list(filter(None, args))
    result = runner.invoke(app, args)
    assert result.exit_code in [0, 2]
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"assign", "get", "post"}


def test_cli_app_fmg_assign_help(help_args: str) -> None:
    """Test cli help for fmg assign"""
    args = ["-c", "tests/fotoobo.yaml", "fmg", "assign"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"adoms", "host", "policy"}
    assert options == {"-h", "--help", "-s", "--smtp", "-t", "--timeout"}
    assert not commands


def test_cli_app_fmg_post_help(help_args: str) -> None:
    """Test cli help for fmg post"""
    args = ["-c", "tests/fotoobo.yaml", "fmg", "post"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"file", "adom", "host"}
    assert options == {"-h", "--help", "-s", "--smtp"}
    assert not commands
