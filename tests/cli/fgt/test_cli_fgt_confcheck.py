"""
Testing the cli fgt confcheck
"""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_confcheck_help() -> None:
    """Test cli help for fgt confcheck help"""
    result = runner.invoke(app, ["fgt", "confcheck", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"configuration", "bundles"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fgt_confcheck_no_args() -> None:
    """Test fgt confcheck with no arguments"""
    result = runner.invoke(app, ["fgt", "confcheck"])
    assert result.exit_code == 2


def test_cli_app_fgt_confcheck() -> None:
    """Test fgt confcheck"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "confcheck",
            "tests/data/fortigate_config_single.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 0


@patch(
    "fotoobo.utils.fgt.confcheck.load_yaml_file",
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
def test_cli_app_fgt_confcheck_failed() -> None:
    """Test fgt confcheck when there are failed checks"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "confcheck",
            "tests/data/fortigate_config_single.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 0


def test_cli_app_fgt_confcheck_empty_config() -> None:
    """Test cli options and commands for fgt confcheck with an empty configuration"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "confcheck",
            "tests/data/fortigate_config_empty.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 0


def test_cli_app_fgt_confcheck_nonexist_config_file() -> None:
    """Test cli options and commands for fgt confcheck with an nonexisting configuration"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "confcheck",
            "tests/data/fortigate_config_nonexist.conf",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 1


def test_cli_app_fgt_confcheck_dir() -> None:
    """Test cli options and commands for fgt confcheck if a directory is given as config source"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "confcheck",
            "tests/data",
            "tests/data/fortigate_checks.yaml",
        ],
    )
    assert result.exit_code == 0


def test_cli_app_fgt_confcheck_invalid_bundle_file() -> None:
    """Test cli options and commands for fgt confcheck with an invalid check bundle file"""
    result = runner.invoke(
        app,
        [
            "fgt",
            "confcheck",
            "tests/data/fortigate_config_single.conf",
            "tests/data/fortigate_checks_invalid.yaml",
        ],
    )
    assert result.exit_code == 1
