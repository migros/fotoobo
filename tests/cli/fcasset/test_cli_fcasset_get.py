"""
Testing the fcasset get cli app
"""

from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fcasset_get_help() -> None:
    """Test cli help for fcasset get"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fcasset", "get", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"products", "version"}


def test_cli_app_fcasset_get_version_help() -> None:
    """Test cli help for fcasset get version"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fcasset", "get", "version", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fcasset_get_version(monkeypatch: MonkeyPatch) -> None:
    """Test cli options and commands for fcasset get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloudasset.FortiCloudAsset.post",
        MagicMock(return_value={"version": "3.0"}),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fcasset", "get", "version"])
    assert result.exit_code == 0
    assert "forticloudasset " in result.stdout
    assert " │ 3.0" in result.stdout


def test_cli_app_fcasset_get_products_help() -> None:
    """Test cli help for fc get products"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fcasset", "get", "products", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"--raw", "-r", "--output", "-o", "-h", "--help"}
    assert not commands
