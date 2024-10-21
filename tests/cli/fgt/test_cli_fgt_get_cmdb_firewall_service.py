"""
Testing the cli fgt get cmdb firewall service
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_get_cmdb_firewall_service_help() -> None:
    """Test cli help for fgt get cmdb firewall service"""
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "firewall", "service", "-h"]
    )
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"custom", "group"}


def test_cli_app_fgt_get_cmdb_firewall_service_no_args() -> None:
    """Test fgt get cmdb firewall service with no arguments"""
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "firewall", "service"]
    )
    assert result.exit_code == 0
    assert "Usage: callback fgt get cmdb firewall service [OPTIONS] COMMAND" in result.stdout
    assert "--help" in result.stdout
    assert "Get FortiGate cmdb firewall service custom." in result.stdout


def test_cli_app_fgt_get_cmdb_firewall_service_custom_help() -> None:
    """Test cli help for fgt get cmdb firewall service custom"""
    result = runner.invoke(
        app,
        ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "firewall", "service", "custom", "-h"],
    )
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host", "name"}
    assert options == {"-h", "--help", "-o", "--output", "--vdom"}
    assert not commands


def test_cli_app_fgt_get_cmdb_firewall_service_group_help() -> None:
    """Test cli help for fgt get cmdb firewall service group"""
    result = runner.invoke(
        app,
        ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "firewall", "service", "group", "-h"],
    )
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host", "name"}
    assert options == {"-h", "--help", "-o", "--output", "--vdom"}
    assert not commands
