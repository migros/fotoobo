"""
Helper functions for testing the cli
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from rich.text import Text
from rich.tree import Tree

# from typer import Typer
# from typer.testing import CliRunner


def parse_help_output(  # pylint: disable=too-many-branches
    output: str,
) -> Tuple[Dict[str, str], Set[str], Dict[str, str]]:
    """
    Parse the output of the cli help and returns the available options and commands

    Args:
        output (str): the help output from the cli

    Returns:
        Tuple[Dict, Set, Dict]:    Dicts and Sets of strings containing arguments,
                                    options and commands
    """
    arguments = {}
    options = set()
    commands = {}
    context = None
    for line in output.split("\n"):

        if line.startswith("╰──"):
            context = None
            continue

        if context == "arg":
            if not line.startswith("│       "):
                parts = line[3:-1].strip().split(maxsplit=2)
                if len(parts) > 2:
                    arguments[parts[0]] = parts[2]

        if context == "opt":
            if line[1:-1].strip().startswith("-"):
                parts = line[1:-1].strip().split()
                if len(parts) > 1:
                    options.add(parts[0].strip(","))
                    if parts[1].startswith("-"):
                        options.add(parts[1])

        if context == "cmd":
            if not line.startswith("│   "):
                parts = line[1:-1].strip().split(maxsplit=1)
                if len(parts) > 1:
                    commands[parts[0]] = parts[1]

        if line.startswith("╭─ Arguments ─"):
            context = "arg"

        if line.startswith("╭─ Options ─"):
            context = "opt"

        if line.startswith("╭─ Commands ─"):
            context = "cmd"

    return arguments, options, commands


# def walk_cli_tree(typer_app: Typer, tree: Tree, command_path: Optional[List[str]] = None) -> Tree:
#     """
#     Recursively create the cli command tree from a Typer app.

#     Args:
#         cli_app Typer): The Typer app to walk through
#         tree (Tree): The rich tree object to build
#         command_path (List[str]): The command path as a list

#     Returns:
#         Tree: The complete rich Tree object
#     """
#     command_path = command_path or []

#     result = CliRunner().invoke(typer_app, command_path + ["-h"])
#     _, _, commands = parse_help_output(result.stdout)

#     for command in sorted(commands):
#         text = Text(overflow="ellipsis", no_wrap=True)
#         text.append(command, style="bold cyan")
#         text.append(" " * max((20 - len(command_path) * 4 - len(command)), 2))
#         text.append(commands[command], style="grey53")
#         branch = tree.add(text)
#         walk_cli_tree(typer_app, branch, command_path + [command])

#     return tree


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
