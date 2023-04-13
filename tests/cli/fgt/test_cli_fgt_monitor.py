"""
Testing the cli fgt check
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_monitor_help() -> None:
    """Test cli help for fgt check"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "monitor", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"hamaster"}


def test_cli_app_fgt_monitor_hamaster_help() -> None:
    """Test cli help for fgt check hamaster"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "monitor", "hamaster", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "--smtp"}
    assert not commands
