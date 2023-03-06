"""
Testing the cli app
"""
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import ResponseMock, parse_help_output

runner = CliRunner()


def test_cli_app_faz_get_help() -> None:
    """Test cli help for faz get"""
    result = runner.invoke(app, ["faz", "get", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"version"}


def test_cli_app_faz_get_version_help() -> None:
    """Test cli help for faz get version"""
    result = runner.invoke(app, ["faz", "get", "version", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help"}
    assert not commands


@patch(
    "fotoobo.fortinet.fortinet.requests.Session.post",
    MagicMock(
        return_value=ResponseMock(
            json={"result": [{"data": {"Version": "v1.1.1-build1111 111111 (GA)"}}]}, status=200
        )
    ),
)
def test_cli_app_faz_get_version() -> None:
    """Test cli options and commands for faz get version"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "faz", "get", "version", "test_faz"])
    assert result.exit_code == 0
    assert result.stdout.count("1.1.1") == 1


def test_cli_app_faz_get_version_dummy() -> None:
    """Test cli options and commands for faz get version with an unknown host"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "faz", "get", "version", "dummy_faz"])
    assert result.exit_code == 1


@patch(
    "fotoobo.fortinet.fortinet.requests.Session.post",
    MagicMock(
        return_value=ResponseMock(json={"result": [{"data": {"Version": "dummy"}}]}, status=200)
    ),
)
def test_cli_app_faz_get_version_none() -> None:
    """Test cli options and commands for faz get version when there is no version in the response"""
    result = runner.invoke(
        app, ["-c", "tests/dummy_fotoobo.yaml", "faz", "get", "version", "test_faz"]
    )
    assert result.exit_code == 0
    assert result.stdout.count("1.1.1") == 0
