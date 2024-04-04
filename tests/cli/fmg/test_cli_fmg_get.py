"""
Testing the cli app
"""

from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from fotoobo.exceptions import GeneralError, GeneralWarning
from tests.helper import ResponseMock, parse_help_output

runner = CliRunner()


def test_cli_app_fmg_get_help() -> None:
    """Test cli help for fmg get"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "get", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"adoms", "devices", "policy", "version"}


def test_cli_app_fmg_get_adoms_help() -> None:
    """Test cli help for fmg get adoms"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "get", "adoms", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fmg_get_devices_help() -> None:
    """Test cli help for fmg get devices"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "get", "devices", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-r", "--raw"}
    assert not commands


def test_cli_app_fmg_get_policy_help() -> None:
    """Test cli help for fmg get policy"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "get", "policy", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host", "adom", "policy_name", "filename"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fmg_get_version_help() -> None:
    """Test cli help for fmg get version"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "get", "version", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fmg_get_adoms(monkeypatch: MonkeyPatch) -> None:
    """Test fmg get adoms"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={"result": [{"data": [{"name": "dummy", "os_ver": "1", "mr": "1"}]}]},
                status_code=200,
            )
        ),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "get", "adoms", "test_fmg"])
    assert result.exit_code == 0
    assert result.stdout.count("dummy") == 1


def test_cli_app_fmg_get_adoms_unknown_device(monkeypatch: MonkeyPatch) -> None:
    """Test cli options and commands for fmg get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={"result": [{"data": [{"name": "dummy"}]}]}, status_code=200
            )
        ),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "get", "adoms", "dummy_fmg"])
    assert result.exit_code == 1


def test_cli_app_fmg_get_version(monkeypatch: MonkeyPatch) -> None:
    """Test cli options and commands for fmg get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={"result": [{"data": {"Version": "v1.1.1-build1111 111111 (GA)"}}]},
                status_code=200,
            )
        ),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "get", "version", "test_fmg"])
    assert result.exit_code == 0
    assert result.stdout.count("1.1.1") == 1


def test_cli_app_fmg_get_version_dummy() -> None:
    """Test cli options and commands for fmg get version with unknown hostname"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fmg", "get", "version", "dummy_fmg"])
    assert result.exit_code == 1


def test_cli_app_fmg_get_version_exception_warning(monkeypatch: MonkeyPatch) -> None:
    """Test cli when it raises a GeneralWarning exception"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.login",
        MagicMock(side_effect=GeneralWarning("dummy")),
    )
    with pytest.raises(GeneralWarning, match=r"dummy"):
        runner.invoke(
            app,
            ["-c", "tests/fotoobo.yaml", "fmg", "get", "version", "test_fmg"],
            catch_exceptions=False,
        )


def test_cli_app_fmg_get_version_exception_error(monkeypatch: MonkeyPatch) -> None:
    """Test cli when it raises a GeneralError exception"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.login",
        MagicMock(side_effect=GeneralError("dummy")),
    )
    with pytest.raises(GeneralError, match=r"dummy"):
        runner.invoke(
            app,
            ["-c", "tests/fotoobo.yaml", "fmg", "get", "version", "test_fmg"],
            catch_exceptions=False,
        )
