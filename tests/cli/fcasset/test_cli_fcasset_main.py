"""
Testing the fcasset cli app
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fcasset_help() -> None:
    """Test cli help for fcasset"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fcasset", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"get"}
