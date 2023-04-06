"""
Testing the cli fgt config check
"""


from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_config_help() -> None:
    """Test cli help for fgt config help"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "config", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"check", "info"}


def test_cli_app_fgt_config_check_no_args() -> None:
    """Test fgt config check with no arguments"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "config", "check"])
    assert result.exit_code == 2
