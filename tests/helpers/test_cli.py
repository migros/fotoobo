"""
Test the CLI helper.
"""

from types import SimpleNamespace

import pytest
from rich.tree import Tree

from fotoobo.helpers.cli import command_to_cli_info, walk_cli_info


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        pytest.param(
            SimpleNamespace(name="visible", help="The visible help.", hidden=False),
            {
                "name": "visible",
                "help": "The visible help.",
                "hidden": False,
            },
            id="single-command",
        ),
        pytest.param(
            SimpleNamespace(name=None, help=None),
            {
                "name": "root",
                "help": "",
                "hidden": False,
            },
            id="fallbacks-without-hidden",
        ),
        pytest.param(
            SimpleNamespace(name="empty", help="The empty help.", hidden=False, commands={}),
            {
                "name": "empty",
                "help": "The empty help.",
                "hidden": False,
            },
            id="empty-commands",
        ),
        pytest.param(
            SimpleNamespace(name="secret", help="The secret help.", hidden=True),
            {
                "name": "secret",
                "help": "The secret help.",
                "hidden": True,
            },
            id="hidden-command",
        ),
        pytest.param(
            SimpleNamespace(
                name=None,
                help=None,
                hidden=False,
                commands={
                    "visible": SimpleNamespace(
                        name="visible",
                        help="The visible help.",
                        hidden=False,
                    ),
                    "nested": SimpleNamespace(
                        name="nested",
                        help="The nested help.",
                        hidden=False,
                        commands={
                            "child": SimpleNamespace(
                                name="child",
                                help="The child help.",
                                hidden=True,
                            ),
                        },
                    ),
                },
            ),
            {
                "name": "root",
                "help": "",
                "hidden": False,
                "commands": {
                    "visible": {
                        "name": "visible",
                        "help": "The visible help.",
                        "hidden": False,
                    },
                    "nested": {
                        "name": "nested",
                        "help": "The nested help.",
                        "hidden": False,
                        "commands": {
                            "child": {
                                "name": "child",
                                "help": "The child help.",
                                "hidden": True,
                            },
                        },
                    },
                },
            },
            id="nested-commands",
        ),
    ],
)
def test_command_to_cli_info(command: SimpleNamespace, expected: dict[str, object]) -> None:
    """
    Test the command_to_cli_info() function.
    """

    # Act
    info = command_to_cli_info(command)

    # Assert
    assert info == expected


def test_walk_cli_info() -> None:
    """
    Test the walk_cli_info() function.
    """

    # Arrange
    cli_dict = {
        "commands": {
            "easter": {
                "name": "easter",
                "help": "The easter help.",
                "hidden": True,
            },
            "get": {
                "name": "get",
                "help": "The get help.",
                "hidden": False,
                "commands": {
                    "get_one": {
                        "name": "get_one",
                        "help": "The get_one help.",
                        "hidden": False,
                    },
                    "get_two": {
                        "name": "get_two",
                        "help": "The get_two help.",
                        "hidden": False,
                    },
                },
            },
        }
    }
    tree = Tree("fotoobo", guide_style="bold bright_blue")

    # Act
    tree = walk_cli_info(cli_dict, tree)

    # Assert
    assert isinstance(tree, Tree)
    assert tree.label == "fotoobo"
    assert len(tree.children) == 1
    assert str(tree.children[0].label).startswith("get")
    assert len(tree.children[0].children) == 2
