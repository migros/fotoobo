"""
Testing the cli get app
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_get_help(help_args_with_none: str) -> None:
    """Test cli help for get"""
    args = ["-c", "tests/fotoobo.yaml", "get"]
    args.append(help_args_with_none)
    args = list(filter(None, args))
    result = runner.invoke(app, args)
    assert result.exit_code in [0, 2]
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"commands", "inventory", "version"}


def test_cli_get_commands_help(help_args: str) -> None:
    """Test cli help for get commands"""
    args = ["-c", "tests/fotoobo.yaml", "get", "commands"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert not commands


def test_get_commands() -> None:
    """Test get commands"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "commands"])

    out = result.stdout
    assert "─ cli commands structure ─╮" in out
    assert "─ get" in out
    assert "─ greet" not in out
    assert "Print the fotoobo commands" in out


def test_cli_get_inventory_help(help_args: str) -> None:
    """Test cli help for get inventory"""
    args = ["-c", "tests/fotoobo.yaml", "get", "inventory"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert not commands


def test_get_inventory() -> None:
    """Test get inventory"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "inventory"])
    assert result.exit_code == 0
    assert "fotoobo inventory" in result.stdout
    assert "test_fgt_1 " in result.stdout
    assert "test_ems " in result.stdout
    # Will be shortened in some testing scenarios (especially on GitHub)
    assert "forticlientems" in result.stdout
    assert "forticloudasset" in result.stdout


def test_cli_get_version_help(help_args: str) -> None:
    """Test cli help for get version"""
    args = ["-c", "tests/fotoobo.yaml", "get", "version"]
    args.append(help_args)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help", "-v"}
    assert not commands


def test_cli_get_version() -> None:
    """Test cli get version"""

    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "version"])
    assert result.exit_code == 0

    assert "fotoobo version" in result.stdout
    assert "fotoobo │ " in result.stdout
    assert "typer" not in result.stdout


def test_cli_get_version_verbose() -> None:
    """Test cli get version"""

    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "version", "-v"])
    assert result.exit_code == 0

    assert "fotoobo version" in result.stdout
    assert "fotoobo  │ " in result.stdout
    assert "jinja2   │" in result.stdout
    assert "rich     │" in result.stdout
    assert "requests │" in result.stdout
    assert "PyYAML   │" in result.stdout
    assert "typer    │" in result.stdout
