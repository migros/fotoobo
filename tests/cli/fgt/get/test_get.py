"""
Testing the cli fgt get
"""

from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import ResponseMock, parse_help_output

runner = CliRunner()


def test_cli_app_fgt_get_help(help_args_with_none: str) -> None:
    """Test cli help for fgt get"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "get"]
    args.append(help_args_with_none)
    args = list(filter(None, args))
    result = runner.invoke(app, args)
    assert result.exit_code in [0, 2]
    assert "Usage: root fgt get" in result.stdout
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"cmdb", "version"}


def test_cli_app_fgt_get_version_help(help_args: str) -> None:
    """Test cli help for fgt get version"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "get", "version"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    assert "Usage: root fgt get version" in result.stdout
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fgt_get_version(monkeypatch: MonkeyPatch) -> None:
    """Test cli options and commands for fgt get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(return_value=ResponseMock(json={"version": "v1.1.1"}, status_code=200)),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version", "test_fgt_1"])
    assert result.exit_code == 0
    assert result.stdout.count("1.1.1") == 1


def test_cli_app_fgt_get_version_dummy() -> None:
    """Test cli options and commands for fgt get version with unknown host"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version", "dummy_fgt"])
    assert result.exit_code == 1


def test_cli_app_fgt_get_version_all(monkeypatch: MonkeyPatch) -> None:
    """Test cli options and commands for fgt get version without specifying a host"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(return_value=ResponseMock(json={"version": "v1.1.1"}, status_code=200)),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version"])
    assert result.exit_code == 0
    assert result.stdout.count("1.1.1") == 3


def test_cli_app_fgt_get_version_401(monkeypatch: MonkeyPatch) -> None:
    """Test cli options and commands for fgt get version with error 401"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(
            return_value=ResponseMock(json={"dummy": "dummy"}, status_code=401),
        ),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version", "test_fgt_1"])
    assert "HTTP/401 Not Authorized" in result.stdout
    assert result.exit_code == 0
