"""
Testing the ems monitor cli app
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from fotoobo.helpers.cli import parse_help_output

runner = CliRunner()


def test_cli_app_ems_monitor_help() -> None:
    """Test cli help for ems monitor"""
    result = runner.invoke(app, ["ems", "monitor", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {
        "connections",
        "endpoint-management-status",
        "endpoint-os-versions",
        "endpoint-outofsync",
        "license",
        "system",
    }


def test_cli_app_ems_monitor_connections_help() -> None:
    """Test cli help for ems monitor connections"""
    result = runner.invoke(app, ["ems", "monitor", "connections", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_endpoint_management_status_help() -> None:
    """Test cli help for ems monitor endpoint-management-status"""
    result = runner.invoke(app, ["ems", "monitor", "endpoint-management-status", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_endpoint_os_versions_help() -> None:
    """Test cli help for ems monitor endpoint-os-versions"""
    result = runner.invoke(app, ["ems", "monitor", "endpoint-os-versions", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_endpoint_outofsync_help() -> None:
    """Test cli help for ems monitor endpoint-outofsync"""
    result = runner.invoke(app, ["ems", "monitor", "endpoint-outofsync", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_license_help() -> None:
    """Test cli help for ems monitor license"""
    result = runner.invoke(app, ["ems", "monitor", "license", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_system_help() -> None:
    """Test cli help for ems monitor system"""
    result = runner.invoke(app, ["ems", "monitor", "system", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help"}
    assert not commands
