"""
Testing the cli get app
"""

from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_get_no_args() -> None:
    """Test get cli without issuing any arguments"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get"])
    assert result.exit_code == 0
    assert "Usage: callback get [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "--help" in result.stdout
    assert "Get information about fotoobo" in result.stdout


def test_cli_get_help() -> None:
    """Test cli help for get"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"commands", "inventory", "version"}


def test_cli_get_commands_help() -> None:
    """Test cli help for get commands"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "commands", "-h"])
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
    assert "│ callback" in out
    assert "─ get" in out
    assert "─ greet" not in out
    assert "Print the fotoobo commands" in out


def test_cli_get_inventory_help() -> None:
    """Test cli help for get inventory"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "inventory", "-h"])
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
    assert "test_fgt_1 │ dummy" in result.stdout
    assert "test_ems   │ dummy" in result.stdout
    # Will be shortened in some testing scenarios (especially on GitHub)
    assert "forticlie" in result.stdout


def test_cli_get_version_help() -> None:
    """Test cli help for get version"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "get", "version", "-h"])
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
