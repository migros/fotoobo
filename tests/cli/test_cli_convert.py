"""
Testing the cli convert app
"""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_convert_no_args() -> None:
    """Test convert cli without issuing any arguments"""
    result = runner.invoke(app, ["convert"])
    assert result.exit_code == 2
    assert "Usage: callback convert [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "Try 'callback convert -h' for help." in result.stdout
    assert "Error" in result.stdout
    assert "Missing command" in result.stdout


def test_cli_convert_help() -> None:
    """Test cli help for convert"""
    result = runner.invoke(app, ["convert", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"checkpoint"}


@patch("fotoobo.utils.convert.load_json_file", MagicMock(return_value=[]))
def test_cli_convert_checkpoint_unsupported() -> None:
    """Test convert cli command: convert checkpoint assets with unsupported type"""
    result = runner.invoke(app, ["convert", "checkpoint", "infile", "outfile", "unsupported"])
    assert result.exit_code == 1
