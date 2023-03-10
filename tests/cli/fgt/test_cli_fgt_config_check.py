"""
Testing the cli fgt config check
"""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_config_check_help() -> None:
    """Test cli help for fgt config check help"""
    result = runner.invoke(app, ["fgt", "config", "check", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"configuration", "bundles"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fgt_config_check_no_args() -> None:
    """Test fgt config check with no arguments"""
    result = runner.invoke(app, ["fgt", "config", "check"])
    assert result.exit_code == 2


def test_cli_app_fgt_config_check() -> None:
    """Test fgt config check"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "config",
            "check",
            "tests/data/fortigate_config_single.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 0


@patch(
    "fotoobo.utils.fgt.config.check.load_yaml_file",
    MagicMock(
        return_value=[
            {
                "type": "count",
                "scope": "vdom",
                "path": "/root/leaf_81/leaf_82",
                "checks": {"eq": 100},
            }
        ]
    ),
)
def test_cli_app_fgt_config_check_failed() -> None:
    """Test fgt config check when there are failed checks"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "config",
            "check",
            "tests/data/fortigate_config_single.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 0


def test_cli_app_fgt_config_check_empty_config() -> None:
    """Test cli options and commands for fgt config check with an empty configuration"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "config",
            "check",
            "tests/data/fortigate_config_empty.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 0


def test_cli_app_fgt_config_check_nonexist_config_file() -> None:
    """Test cli options and commands for fgt config check with an nonexisting configuration"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "config",
            "check",
            "tests/data/fortigate_config_nonexist.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 1


def test_cli_app_fgt_config_check_dir() -> None:
    """Test cli options and commands for fgt config check if a directory is given"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "config",
            "check",
            "tests/data",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 0


def test_cli_app_fgt_config_check_invalid_bundle_file() -> None:
    """Test cli options and commands for fgt config check with an invalid check bundle file"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "config",
            "check",
            "tests/data/fortigate_config_single.conf",
            "tests/data/fortigate_checks_invalid.yaml",
        ],
    )
    assert result.exit_code == 1
