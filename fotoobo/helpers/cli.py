"""
Helper functions for testing the cli
"""

from typing import Any, Dict, List, Optional

from rich.text import Text
from rich.tree import Tree


def walk_cli_info(
    info: Dict[str, Any], tree: Tree, command_path: Optional[List[str]] = None
) -> Tree:
    """
    Recursively create the cli command tree from a Typer info dict.

    Args:
        info (Dict): The Typer info dict from Typer.Context.to_info_dict() to walk through
        tree (Tree): The rich tree object to build
        command_path (List): The command path as a list

    Returns:
        Tree: The complete rich Tree object
    """
    command_path = command_path or []
    commands = info["commands"]

    for command in sorted(commands):
        if commands[command]["hidden"]:
            continue
        text = Text(overflow="ellipsis", no_wrap=True)
        text.append(commands[command]["name"], style="bold cyan")
        text.append(" " * max((20 - len(command_path) * 4 - len(command)), 2))
        text.append(commands[command]["help"].split("\n")[0], style="grey53")
        branch = tree.add(text)
        if "commands" in commands[command]:
            walk_cli_info(commands[command], branch, command_path + [command])

    return tree
