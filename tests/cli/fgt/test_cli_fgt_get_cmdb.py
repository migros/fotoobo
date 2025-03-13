"""
Testing the cli fgt get cmdb
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_get_cmdb_help() -> None:
    """Test cli help for fgt get cmdb"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"firewall"}


def test_cli_app_fgt_get_cmdb_no_args() -> None:
    """Test fgt get cmdb with no arguments"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb"])
    assert result.exit_code == 0
    assert "Usage: root fgt get cmdb [OPTIONS] COMMAND" in result.stdout
    assert "--help" in result.stdout
    assert "FortiGate get cmdb firewall commands." in result.stdout
