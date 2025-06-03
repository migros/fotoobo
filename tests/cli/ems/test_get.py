"""
Testing the ems get cli app
"""

from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import ResponseMock, parse_help_output

runner = CliRunner()


def test_cli_app_ems_get_help(help_args_with_none: str) -> None:
    """Test cli help for ems get"""
    args = ["-c", "tests/fotoobo.yaml", "ems", "get"]
    args.append(help_args_with_none)
    args = list(filter(None, args))
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"version", "workgroups"}


def test_cli_app_ems_get_version_help(help_args: str) -> None:
    """Test cli help for ems get version"""
    args = ["-c", "tests/fotoobo.yaml", "ems", "get", "version"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_ems_get_workgroups_help(help_args: str) -> None:
    """Test cli help for ems get workgroups"""
    args = ["-c", "tests/fotoobo.yaml", "ems", "get", "workgroups"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-c", "--custom", "-h", "--help"}
    assert not commands


def test_cli_app_ems_get_workgroups(monkeypatch: MonkeyPatch) -> None:
    """Test cli help for ems get workgroups"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "data": [
                        {"name": "Test-grp1", "id": 12345, "total_devices": 123},
                        {"name": "Test-grp2", "id": 54321, "total_devices": 321},
                    ]
                },
                status_code=200,
            )
        ),
    )
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "get", "workgroups", "test_ems"]
    )
    assert result.exit_code == 0
    assert "Test-grp1 │ 12345 │ 123" in result.stdout
    assert "Test-grp2 │ 54321 │ 321" in result.stdout


def test_cli_app_ems_get_version(monkeypatch: MonkeyPatch) -> None:
    """Test cli help for ems get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(
            return_value=ResponseMock(
                json={"data": {"System": {"VERSION": "1.2.3"}}}, status_code=200
            )
        ),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "ems", "get", "version", "test_ems"])
    assert result.exit_code == 0
    assert "test_ems        │ v1.2.3" in result.stdout


def test_cli_app_ems_get_version_dummy() -> None:
    """Test cli options and commands for ems get version with a unknown host"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "ems", "get", "version", "dummy_ems"])
    assert result.exit_code == 1
