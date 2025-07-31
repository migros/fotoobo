"""
Test the cli fgt config.
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_fgt_config_help(help_args_with_none: str) -> None:
    """
    Test cli help for fgt config help.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "fgt", "config"]
    args.append(help_args_with_none)
    args = list(filter(None, args))

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code in [0, 2]
    assert "Usage: root fgt config" in result.stdout
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"check", "get", "info"}
