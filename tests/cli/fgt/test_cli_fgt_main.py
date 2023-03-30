"""
Testing the cli app
"""
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_help() -> None:
    """Test cli help for fgt"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"backup", "check", "get", "config"}
