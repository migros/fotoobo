"""
Testing the cli fgt monitor
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_monitor_help(help_args_with_none: str) -> None:
    """Test cli help for fgt monitor"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "monitor"]
    args.append(help_args_with_none)
    args = list(filter(None, args))
    result = runner.invoke(app, args)
    assert result.exit_code in [0, 2]
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"hamaster"}


def test_cli_app_fgt_monitor_hamaster_help(help_args: str) -> None:
    """Test cli help for fgt monitor hamaster"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "monitor", "hamaster"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {
        "-h",
        "--help",
        "-o",
        "--output",
        "-r",
        "--raw",
        "--smtp",
        "-t",
        "--template",
    }
    assert not commands
