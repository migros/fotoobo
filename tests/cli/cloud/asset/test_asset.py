"""
Testing the cloud asset cli app
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_app_asset_help(help_args_with_none: str) -> None:
    """Test cli help for asset"""
    args = ["-c", "tests/fotoobo.yaml", "cloud", "asset"]
    args.append(help_args_with_none)
    args = list(filter(None, args))
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"get"}
