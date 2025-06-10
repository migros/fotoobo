"""
This module defines some helpers for the test package. These may be used by every test package.
"""

from typing import Any
from unittest.mock import MagicMock

from requests.exceptions import HTTPError


class ResponseMock:  # pylint: disable=too-many-instance-attributes
    """This class mocks a http response object."""

    def __init__(self, **kwargs: Any) -> None:
        """
        Give the mock the response you expect.

        **kwargs:
            content: (Any, optional): Content of the response
            headers: (List, optional): List of headers
            json (Any, optional): JSON response. Defaults to ""
            ok (bool, optional):  The OK flag. Defaults to True
            reason(str, optional): The response reason. Defaults to ""
            status_code (int, optional): HTTP status code. Defaults to 444 (No Response)
            text (str, optional): Text response. Defaults to ""
        """
        self.content = kwargs.get("content", "")
        self.headers = kwargs.get("headers", [])
        self.json = MagicMock(return_value=kwargs.get("json", None))
        self.ok = kwargs.get("ok", True)
        self.raise_for_status = MagicMock()
        self.reason = kwargs.get("reason", "")
        self.status_code = kwargs.get("status_code", 444)
        self.text = kwargs.get("text", "")

        if self.status_code >= 300:
            self.raise_for_status = MagicMock(
                side_effect=HTTPError("mocked HTTPError", response=self)  # type: ignore
            )


def parse_help_output(  # pylint: disable=too-many-branches
    output: str,
) -> tuple[dict[str, str], set[str], dict[str, str]]:
    """
    Parse the output of the cli help and return the available arguments, options and commands

    Args:
        output: the help output from the cli

    Returns:
        Dicts and Sets of strings containing arguments, options and commands
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
