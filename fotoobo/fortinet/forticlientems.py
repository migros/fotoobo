"""
FortiClient EMS Class
"""

import logging
import pickle
import re
from pathlib import Path
from typing import Any, Optional

import requests

from fotoobo.exceptions import APIError, GeneralWarning

from .fortinet import Fortinet

log = logging.getLogger("fotoobo")


class FortiClientEMS(Fortinet):
    """
    Represents one FortiClient EMS (digital twin)
    """

    ALLOWED_HTTP_METHODS = ["DELETE", "GET", "PATCH", "POST"]

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        cookie_path: str = "",
        **kwargs: Any,
    ) -> None:
        """
        Set some initial parameters.

        Args:
            hostname:    The hostname of the FortiClient EMS to connect to
            username:    Username
            password:    Password
            cookie_path: Path to write the cookie files (no cookie if empty)
            **kwargs:    See Fortinet class for available arguments
        """
        super().__init__(hostname, **kwargs)
        self.api_url = f"https://{self.hostname}:{self.https_port}/api/v1"
        self.cookie_path = cookie_path
        self.password: str = password
        self.username: str = username
        self.type: str = "forticlientems"

    def api(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        method: str,
        url: str = "",
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, str]] = None,
        payload: Optional[dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> requests.models.Response:
        """
        API request to a FortiClientEMS device.

        Args:
            method:  Request method from [get, post]
            url:     Rest API URL to request data from
            headers: Additional headers (if needed)
            params:  Dictionary with parameters (if needed)
            payload: JSON body for post requests (if needed)
            timeout: The requests read timeout

        Returns:
            Response from the request
        """
        if not headers:
            headers = self.session.headers  # type: ignore

        return super().api(
            method, url, payload=payload, params=params, timeout=timeout, headers=headers
        )

    def get_version(self) -> str:
        """
        Get the FortiClient EMS version.
        According to Fortinet support the FortiClient EMS version may be read out of the endpoint
        /system/consts/get?system_update_time=1. This endpoint is not (yet) documented. Let's hope
        they support it in case of any issue.

        Returns:
            FortiClient EMS version
        """
        try:
            response = self.api("get", "/system/consts/get?system_update_time=1")

        except APIError as err:
            log.warning("'%s' returned: '%s'", self.hostname, err.message)
            raise GeneralWarning(f"{self.hostname} returned: {err.message}") from err

        try:
            ems_version: str = response.json()["data"]["System"]["VERSION"]

        except KeyError as err:
            log.warning("Did not find any FortiClient EMS version number in response")
            raise GeneralWarning(
                "Did not find any FortiClient EMS version number in response"
            ) from err

        return ems_version

    def login(self) -> int:
        """
        Login to the FortiClientEMS.

        Returns:
            Status code from the FortiClient EMS logon
        """
        status = 401
        cookie = Path(self.cookie_path).expanduser() / f"{self.hostname}.cookie"
        csrf = Path(self.cookie_path).expanduser() / f"{self.hostname}.csrf"

        if self.cookie_path:
            log.debug("Searching cookie and csrf token in '%s'", cookie.parents[0])

            if cookie.is_file() and csrf.is_file():
                log.debug("Cookie and csrf token both exist")
                with cookie.open("rb") as cookie_file:
                    self.session.cookies.update(pickle.load(cookie_file))

                self.session.headers["Referer"] = f"https://{self.hostname}"
                self.session.headers["X-CSRFToken"] = csrf.read_text()

                try:
                    response = self.api("get", "/system/serial_number")
                    if (
                        "retval" in response.json()["result"]
                        and int(response.json()["result"]["retval"]) == 1
                    ):
                        log.debug(
                            "Session with given cookie is valid (status: '%s')",
                            response.status_code,
                        )
                        status = response.status_code

                except APIError as err:
                    log.debug("Session with given cookie is invalid (status: '%s')", err.code)
                    status = err.code

            else:
                log.debug("No cookie or csrf token found for '%s'", self.hostname)

        if status == 401:
            log.debug("Login to '%s'", self.hostname)
            payload = {"name": self.username, "password": self.password}
            response = self.api("post", "/auth/signin", payload=payload)

            if response.status_code == 200:
                self.session.headers["Referer"] = f"https://{self.hostname}"
                if match := re.match(r"csrftoken=(\S+);", response.headers["Set-Cookie"]):
                    csrf_token = match.group(1)
                    self.session.headers["X-CSRFToken"] = csrf_token

                if self.cookie_path:
                    log.debug("Saving cookie for '%s'", self.hostname)
                    try:
                        with cookie.open("wb") as cookie_file:
                            pickle.dump(self.session.cookies, cookie_file)

                    except FileNotFoundError as exc:
                        log.debug(exc)
                        log.warning("Unable to save cookie file '%s'", str(cookie.resolve()))

                    log.debug("Saving csrf token for '%s'", self.hostname)
                    try:
                        csrf.write_text(csrf_token)

                    except NameError as exc:
                        log.debug(exc)
                        log.warning("Unable to save csrf token file '%s'", str(csrf.resolve()))

            status = response.status_code

        return status

    def logout(self) -> int:
        """
        Logout from FortiClient EMS.

        Returns:
            Status code from the FortiClient EMS logout
        """
        response = self.api("get", "/auth/signout")
        log.debug("Logged out from '%s' (status: '%s')", self.hostname, response.status_code)
        return response.status_code
