"""
Testing the cli app
"""
from pathlib import Path
from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_help() -> None:
    """Test cli help for fgt"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"backup", "monitor", "get", "config"}


def test_cli_app_fgt_backup_help() -> None:
    """Test cli help for fgt backup"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "backup", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"--backup-dir", "-b", "--ftp", "-f", "--smtp", "-s", "-h", "--help"}
    assert not commands


def test_cli_app_fgt_backup_single(monkeypatch: MonkeyPatch, temp_dir: str) -> None:
    """Test cli fgt backup with no FortiGate given so it backups all"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(return_value="#config-version\ntest-1234"),
    )
    Path(temp_dir / Path("test_fgt_1.conf")).unlink(missing_ok=True)
    Path(temp_dir / Path("test_fgt_2.conf")).unlink(missing_ok=True)
    assert not Path.exists(Path(temp_dir / Path("test_fgt_1.conf")))
    assert not Path.exists(Path(temp_dir / Path("test_fgt_2.conf")))
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "fgt", "backup", "test_fgt_1", "-b", temp_dir]
    )
    assert result.exit_code == 0
    assert Path.exists(Path(temp_dir / Path("test_fgt_1.conf")))
    assert not Path.exists(Path(temp_dir / Path("test_fgt_2.conf")))


def test_cli_app_fgt_backup_all(monkeypatch: MonkeyPatch, temp_dir: str) -> None:
    """Test cli fgt backup with no FortiGate given so it backups all"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.backup",
        MagicMock(return_value="#config-version\ntest-1234"),
    )
    Path(temp_dir / Path("test_fgt_1.conf")).unlink(missing_ok=True)
    Path(temp_dir / Path("test_fgt_2.conf")).unlink(missing_ok=True)
    assert not Path.exists(Path(temp_dir / Path("test_fgt_1.conf")))
    assert not Path.exists(Path(temp_dir / Path("test_fgt_2.conf")))
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "backup", "-b", temp_dir])
    assert result.exit_code == 0
    assert Path.exists(Path(temp_dir / Path("test_fgt_1.conf")))
    assert Path.exists(Path(temp_dir / Path("test_fgt_2.conf")))
