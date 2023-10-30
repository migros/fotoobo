"""
This module defines some helpers for the test package. These may be used by every test package.
"""

from typing import Any, Dict, Set, Tuple
from unittest.mock import MagicMock

from requests.exceptions import HTTPError


class ResponseMock:
    """This class mocks a http response object."""

    def __init__(self, **kwargs) -> None:
        """
        Give the mock the response you except.

        Args:
            text (str, optional): text response. Defaults to "".
            json (Any, optional): json response. Defaults to "".
            status (int, optional): http status code. Defaults to 444 (No Response)
        """
        self.text = kwargs.get("text", "")
        self.json = MagicMock(return_value=kwargs.get("json", None))
        self.status_code = kwargs.get("status", 444)
        self.ok = kwargs.get("ok", True)
        self.content = kwargs.get("content", "")
        self.reason = kwargs.get("reason", "")
        self.raise_for_status = MagicMock()

        if self.status_code >= 300:
            self.raise_for_status = MagicMock(
                side_effect=HTTPError("mocked HTTPError", response=self)
            )


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
