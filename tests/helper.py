"""
This module defines some helpers for the test package. These may be used by every test package.
"""
from typing import Any
from unittest.mock import MagicMock

from requests.exceptions import HTTPError


class ResponseMock:
    """This class mocks a http response object."""

    def __init__(self, text: str = "", json: Any = None, status: int = 444) -> None:
        """
        Give the mock the response you except.

        Args:
            text (str, optional): text response. Defaults to "".
            json (Any, optional): json response. Defaults to "".
            status (int, optional): http status code. Defaults to 444 (No Response)
        """
        self.text = text
        self.json = MagicMock(return_value=json)
        self.status_code = status
        self.raise_for_status = MagicMock()
        if self.status_code >= 300:
            self.raise_for_status = MagicMock(
                side_effect=HTTPError("mocked HTTPError", response=self)
            )
