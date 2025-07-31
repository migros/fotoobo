"""
Testing the cli fgt get.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import ResponseMock, parse_help_output

runner = CliRunner()


def test_cli_app_fgt_get_help(help_args_with_none: str) -> None:
    """
    Test cli help for fgt get.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "fgt", "get"]
    args.append(help_args_with_none)
    args = list(filter(None, args))

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code in [0, 2]
    assert "Usage: root fgt get" in result.stdout
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"cmdb", "version"}


def test_cli_app_fgt_get_version_help(help_args: str) -> None:
    """
    Test cli help for fgt get version.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "fgt", "get", "version"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    assert "Usage: root fgt get version" in result.stdout
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fgt_get_version(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli options and commands for fgt get version.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        Mock(return_value=ResponseMock(json={"version": "v1.1.1"}, status_code=200)),
    )

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version", "test_fgt_1"])

    # Assert
    assert result.exit_code == 0
    assert result.stdout.count("1.1.1") == 1


def test_cli_app_fgt_get_version_dummy() -> None:
    """
    Test cli options and commands for fgt get version with unknown host.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version", "dummy_fgt"])

    # Assert
    assert result.exit_code == 1


def test_cli_app_fgt_get_version_all(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli options and commands for fgt get version without specifying a host.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        Mock(return_value=ResponseMock(json={"version": "v1.1.1"}, status_code=200)),
    )

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version"])

    # Assert
    assert result.exit_code == 0
    assert result.stdout.count("1.1.1") == 3


def test_cli_app_fgt_get_version_401(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli options and commands for fgt get version with error 401.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        Mock(
            return_value=ResponseMock(json={"dummy": "dummy"}, status_code=401),
        ),
    )

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "get", "version", "test_fgt_1"])

    # Assert
    assert "HTTP/401 Not Authorized" in result.stdout
    assert result.exit_code == 0
