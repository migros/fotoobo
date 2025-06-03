"""
Testing the cli fgt get cmdb firewall
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_get_cmdb_firewall_help(help_args_with_none: str) -> None:
    """Test cli help for fgt get cmdb firewall"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "firewall"]
    args.append(help_args_with_none)
    args = list(filter(None, args))
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"address", "addrgrp", "service-custom", "service-group"}


def test_cli_app_fgt_get_cmdb_firewall_address_help(help_args: str) -> None:
    """Test cli help for fgt get cmdb firewall address"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "firewall", "address"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host", "name"}
    assert options == {"-h", "--help", "-o", "--output", "--vdom"}
    assert not commands


def test_cli_app_fgt_get_cmdb_firewall_addrgrp_help(help_args: str) -> None:
    """Test cli help for fgt get cmdb firewall address group"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "firewall", "addrgrp"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host", "name"}
    assert options == {"-h", "--help", "-o", "--output", "--vdom"}
    assert not commands


def test_cli_app_fgt_get_cmdb_firewall_service_custom_help(help_args: str) -> None:
    """Test cli help for fgt get cmdb firewall service-custom"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "firewall", "service-custom"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host", "name"}
    assert options == {"-h", "--help", "-o", "--output", "--vdom"}
    assert not commands


def test_cli_app_fgt_get_cmdb_firewall_service_group_help(help_args: str) -> None:
    """Test cli help for fgt get cmdb firewall service-group"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "get", "cmdb", "firewall", "service-group"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host", "name"}
    assert options == {"-h", "--help", "-o", "--output", "--vdom"}
    assert not commands
