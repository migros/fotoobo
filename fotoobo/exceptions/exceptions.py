"""
This is the fotoobo exception module.
"""


from typing import Any

from requests.exceptions import HTTPError


class GeneralException(Exception):
    """
    This is the generic fotoobo exception which can be used by any sub exception.
    """

    def __init__(self, message: str) -> None:
        """init"""
        self.message = message
        super().__init__(self.message)


class APIError(GeneralException):
    """Exception for errors with the network API"""

    def __init__(self, err: Any) -> None:
        """init"""
        self.http_status_codes = {
            200: "OK",
            400: "Bad Request",
            401: "Not Authorized",
            403: "Forbidden",
            404: "Resource Not Found",
            405: "Method Not Allowed",
            413: "Request Entity Too Large",
            424: "Failed Dependency",
            429: "Access temporarily blocked",
            500: "Internal Server Error",
        }
        # self.message = "general API Error"
        self.code = 999
        self.message = "unknown"
        if isinstance(err, HTTPError):
            self.code = err.response.status_code
            message = self.http_status_codes.get(self.code, "general API Error")
            self.message = f"HTTP/{str(self.code)} {message}"

        super().__init__(self.message)


class GeneralError(GeneralException):
    """
    The exception to raise if a general error occurred.
    The class does not have any methods as the only one (__init__) is inherited from it's parent.
    Raise a GeneralError when it does not make sense to do further processing and the program should
    stop and exit.
    """


class GeneralWarning(GeneralException):
    """
    The exception to raise if a general warning occurred.
    The class does not have any methods as the only one (__init__) is inherited from it's parent.
    Raise a GeneralWarning if a part of the program fails but it is safe to du further processing.
    """
