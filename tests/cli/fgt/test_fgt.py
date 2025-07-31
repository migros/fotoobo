"""
Testing the cli app.
"""

from pathlib import Path
from unittest.mock import Mock

from pytest import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_help(help_args_with_none: str) -> None:
    """
    Test cli help for fgt.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "fgt"]
    args.append(help_args_with_none)
    args = list(filter(None, args))

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code in [0, 2]
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"backup", "monitor", "get", "config"}


def test_cli_app_fgt_backup_help(help_args: str) -> None:
    """
    Test cli help for fgt backup.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "fgt", "backup"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"--backup-dir", "-b", "--ftp", "-f", "--smtp", "-s", "-h", "--help"}
    assert not commands


def test_cli_app_fgt_backup_single(monkeypatch: MonkeyPatch, function_dir: Path) -> None:
    """
    Test cli fgt backup with no FortiGate given so it backups all.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        Mock(return_value="#config-version\ntest-1234"),
    )

    # Act
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "fgt", "backup", "test_fgt_1", "-b", str(function_dir)]
    )

    # Assert
    assert result.exit_code == 0
    assert (function_dir / "test_fgt_1.conf").exists()
    assert not (function_dir / "test_fgt_2.conf").exists()


def test_cli_app_fgt_backup_all(monkeypatch: MonkeyPatch, function_dir: Path) -> None:
    """
    Test cli fgt backup with no FortiGate given so it backups all.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        Mock(return_value="#config-version\ntest-1234"),
    )

    # Act
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "fgt", "backup", "-b", str(function_dir)]
    )

    # Assert
    assert result.exit_code == 0
    assert (function_dir / "test_fgt_1.conf").exists()
    assert (function_dir / "test_fgt_2.conf").exists()
