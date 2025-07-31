"""
Testing the cloud asset get cli app.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_asset_get_help(help_args_with_none: str) -> None:
    """
    Test cli help for asset get.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "cloud", "asset", "get"]
    args.append(help_args_with_none)
    args = list(filter(None, args))

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code in [0, 2]
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"products", "version"}


def test_cli_app_asset_get_version_help(help_args: str) -> None:
    """
    Test cli help for asset get version.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "cloud", "asset", "get", "version"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_asset_get_version(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli options and commands for asset get version.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloudasset.FortiCloudAsset.post",
        Mock(return_value={"version": "3.0"}),
    )

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "cloud", "asset", "get", "version"])

    # Assert
    assert result.exit_code == 0
    assert "forticloudasset " in result.stdout
    assert " │ 3.0" in result.stdout


def test_cli_app_asset_get_products_help(help_args: str) -> None:
    """
    Test cli help for asset get products.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "cloud", "asset", "get", "products"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"--raw", "-r", "--output", "-o", "-h", "--help"}
    assert not commands
