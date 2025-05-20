"""
Testing the fc get cli app
"""

from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fc_get_help() -> None:
    """Test cli help for fc get"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fc", "get", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"products", "version"}


def test_cli_app_fc_get_version_help() -> None:
    """Test cli help for fc get version"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fc", "get", "version", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fc_get_version(monkeypatch: MonkeyPatch) -> None:
    """Test cli options and commands for fc get version"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloud.FortiCloudAsset.post",
        MagicMock(return_value={"version": "3.0"}),
    )
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fc", "get", "version"])
    assert result.exit_code == 0
    assert "forticloud │ 3.0" in result.stdout


def test_cli_app_fc_get_products_help() -> None:
    """Test cli help for fc get products"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fc", "get", "products", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"--raw", "-r", "--output", "-o", "-h", "--help"}
    assert not commands
