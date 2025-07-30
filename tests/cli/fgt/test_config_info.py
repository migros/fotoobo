"""
Testing the cli fgt config info
"""

import pytest
from typer.testing import CliRunner

from fotoobo.cli.main import app
from fotoobo.exceptions.exceptions import GeneralWarning
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_config_info_help(help_args_with_none: str) -> None:
    """Test cli help for fgt config info help"""
    args = ["-c", "tests/fotoobo.yaml", "fgt", "config", "info"]
    args.append(help_args_with_none)
    args = list(filter(None, args))
    result = runner.invoke(app, args)
    assert result.exit_code in [0, 2]
    assert "Usage: root fgt config info" in result.stdout
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"configuration"}
    assert options == {"-h", "--help", "-l", "--list"}
    assert not commands


@pytest.mark.parametrize(
    "file",
    (
        pytest.param("tests/data/fortigate_config_single.conf", id="single"),
        pytest.param("tests/data/fortigate_config_vdom.conf", id="vdom"),
    ),
)
def test_cli_app_fgt_config_info(file: str) -> None:
    """Test fgt config info"""
    result = runner.invoke(
        app,
        [
            "-c",
            "tests/fotoobo.yaml",
            "fgt",
            "config",
            "info",
            file,
        ],
    )
    assert result.exit_code == 0
    assert "FGT999" in result.stdout


def test_cli_app_fgt_config_info_empty_config() -> None:
    """Test cli options and commands for fgt config info with an empty configuration"""
    with pytest.raises(GeneralWarning, match=r"There is no info in"):
        runner.invoke(
            app,
            [
                "-c",
                "tests/fotoobo.yaml",
                "fgt",
                "config",
                "info",
                "tests/data/fortigate_config_empty.conf",
            ],
            catch_exceptions=False,
        )


def test_cli_app_fgt_config_info_nonexist_config_file() -> None:
    """Test cli options and commands for fgt config info with an nonexisting configuration"""
    with pytest.raises(GeneralWarning, match=r"There are no"):
        runner.invoke(
            app,
            [
                "-c",
                "tests/fotoobo.yaml",
                "fgt",
                "config",
                "info",
                "tests/data/fortigate_config_nonexist.conf",
            ],
            catch_exceptions=False,
        )


def test_cli_app_fgt_config_info_dir() -> None:
    """Test cli options and commands for fgt config info if a directory is given"""
    with pytest.raises(GeneralWarning, match=r"There is no info in"):
        runner.invoke(
            app,
            [
                "-c",
                "tests/fotoobo.yaml",
                "fgt",
                "config",
                "info",
                "tests/data",
            ],
            catch_exceptions=False,
        )
