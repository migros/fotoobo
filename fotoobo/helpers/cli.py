"""
Helper functions for testing the cli
"""

from typing import Any

from rich.text import Text
from rich.tree import Tree


def command_to_cli_info(command: Any) -> dict[str, Any]:
    """
    Create the cli command info needed to render the fotoobo command tree.

    Args:
        command: The Typer command object to convert

    Returns:
        A dict containing the command tree information
    """

    info = {
        "name": command.name or "root",
        "help": command.help or "",
        "hidden": bool(getattr(command, "hidden", False)),
    }

    commands = getattr(command, "commands", None)
    if commands:
        info["commands"] = {
            name: command_to_cli_info(subcommand) for name, subcommand in commands.items()
        }

    return info


def walk_cli_info(info: dict[str, Any], tree: Tree, command_path: list[str] | None = None) -> Tree:
    """
    Recursively create the cli command tree from a Typer command info dict.

    Args:
        info:         The Typer command info dict to walk through
        tree:         The rich tree object to build
        command_path: The command path as a list

    Returns:
        The complete rich Tree object
    """
    command_path = command_path or []
    commands = info["commands"]

    for command in sorted(commands):
        if commands[command]["hidden"]:
            continue

        text = Text(overflow="ellipsis", no_wrap=True)
        text.append(commands[command]["name"], style="bold cyan")
        text.append(" " * max((25 - len(command_path) * 4 - len(command)), 2))
        text.append(commands[command]["help"].split("\n")[0], style="grey53")
        branch = tree.add(text)

        if "commands" in commands[command]:
            walk_cli_info(commands[command], branch, command_path + [command])

    return tree
