"""
Testing the ems get cli app
"""
from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from fotoobo.helpers.cli import parse_help_output
from tests.helper import ResponseMock

runner = CliRunner()


def test_cli_app_ems_get_help() -> None:
    """Test cli help for ems get"""
    result = runner.invoke(app, ["ems", "get", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"version", "workgroups"}


def test_cli_app_ems_get_version_help() -> None:
    """Test cli help for ems get version"""
    result = runner.invoke(app, ["ems", "get", "version", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_ems_get_workgroups_help() -> None:
    """Test cli help for ems get workgroups"""
    result = runner.invoke(app, ["ems", "get", "workgroups", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-c", "--custom", "-h", "--help"}
    assert not commands


def test_cli_app_ems_get_version(monkeypatch: MonkeyPatch) -> None:
    """Test cli help for ems get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(
            return_value=ResponseMock(json={"data": {"System": {"VERSION": "1.2.3"}}}, status=200)
        ),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "ems", "get", "version", "test_ems"])
    assert result.exit_code == 0
    assert result.stdout.count("1.2.3") == 1


def test_cli_app_ems_get_version_dummy() -> None:
    """Test cli options and commands for ems get version with a unknown host"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "ems", "get", "version", "dummy_ems"])
    assert result.exit_code == 1
