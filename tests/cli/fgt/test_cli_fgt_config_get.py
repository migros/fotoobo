"""
Testing the cli fgt config get
"""


import pytest
from typer.testing import CliRunner

from fotoobo.cli.main import app
from fotoobo.exceptions.exceptions import GeneralWarning
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_config_get_help() -> None:
    """Test cli help for fgt config get help"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "config", "get", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"configuration", "scope", "path"}
    assert options == {"-h", "--help"}
    assert not commands


def test_cli_app_fgt_config_get_no_args() -> None:
    """Test fgt config get with no arguments"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "fgt", "config", "get"])
    assert result.exit_code == 0
    assert "Usage: callback fgt config get [OPTIONS]" in result.stdout
    assert "--help" in result.stdout
    assert "Get configuration or parts of it" in result.stdout


@pytest.mark.parametrize(
    "file",
    (
        pytest.param("tests/data/fortigate_config_single.conf", id="single"),
        pytest.param("tests/data/fortigate_config_vdom.conf", id="vdom"),
    ),
)
def test_cli_app_fgt_config_get(file: str) -> None:
    """Test fgt config get"""
    result = runner.invoke(
        app,
        ["-c", "tests/fotoobo.yaml", "fgt", "config", "get", file, "global", "/"],
    )
    assert result.exit_code == 0
    assert "option_2" in result.stdout
    assert "value_2" in result.stdout


@pytest.mark.parametrize(
    "file",
    (
        pytest.param("tests/data/fortigate_config_single.conf", id="single"),
        pytest.param("tests/data/fortigate_config_vdom.conf", id="vdom"),
    ),
)
def test_cli_app_fgt_config_get_no_path(file: str) -> None:
    """Test fgt config get with no path supplied"""
    result = runner.invoke(
        app,
        ["-c", "tests/fotoobo.yaml", "fgt", "config", "get", file, "global"],
    )
    assert result.exit_code == 0
    assert "option_2" in result.stdout
    assert "value_2" in result.stdout


def test_cli_app_fgt_config_get_empty_config() -> None:
    """Test cli options and commands for fgt config get with an empty configuration"""
    with pytest.raises(GeneralWarning, match=r"There is no info in"):
        runner.invoke(
            app,
            [
                "-c",
                "tests/fotoobo.yaml",
                "fgt",
                "config",
                "get",
                "tests/data/fortigate_config_empty.conf",
                "global",
            ],
            catch_exceptions=False,
        )


def test_cli_app_fgt_config_get_noexist_config_file() -> None:
    """Test cli options and commands for fgt config get with an nonexisting configuration"""
    with pytest.raises(GeneralWarning, match=r"There are no"):
        runner.invoke(
            app,
            [
                "-c",
                "tests/fotoobo.yaml",
                "fgt",
                "config",
                "get",
                "tests/data/fortigate_config_noexist.conf",
                "global",
                "/",
            ],
            catch_exceptions=False,
        )


def test_cli_app_fgt_config_get_dir() -> None:
    """Test cli fgt config get if a directory without configuration files is given"""
    with pytest.raises(GeneralWarning, match=r"There is no info in"):
        runner.invoke(
            app,
            ["-c", "tests/fotoobo.yaml", "fgt", "config", "get", "tests/data", "global", "/"],
            catch_exceptions=False,
        )
