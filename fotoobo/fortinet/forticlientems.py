"""
FortiClient EMS Class
"""
import logging
import os
import pickle
from typing import Any, Dict, Optional

import requests

from fotoobo.exceptions import APIError, GeneralWarning

from .fortinet import Fortinet

log = logging.getLogger("fotoobo")


class FortiClientEMS(Fortinet):
    """
    Represents one FortiClient EMS (digital twin)
    """

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
            hostname (str): the hostname of the FortiClient EMS to connect to
            username (str): username
            password (str): password
            cookie_path (str): path to write the cookie files (no cookie if empty)
            **kwargs (dict): see Fortinet class for available arguments
        """
        super().__init__(hostname, **kwargs)
        self.api_url = f"https://{self.hostname}/api/v1"
        self.cookie_path = cookie_path
        self.password = password
        self.username = username
        self.type = "forticlientems"

    def api(  # pylint: disable=too-many-arguments
        self,
        method: str,
        url: str = "",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> requests.models.Response:
        """
        API request to a FortiClientEMS device.

        Args:
            method (str): request method from [get, post]
            url (str): rest API URL to request data from
            params (dict): dictionary with parameters (if needed)
            payload (dict): JSON body for post requests (if needed)
            timeout (float): the requests read timeout

        Returns:
            response: response from the request
        """
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
            str: version
        """
        ems_version: str = ""
        try:
            response = self.api("get", "/system/consts/get?system_update_time=1")

        except APIError as err:
            log.warning("%s returned: %s", self.hostname, err.message)
            raise GeneralWarning(f"{self.hostname} returned: {err.message}") from err

        try:
            ems_version = response.json()["data"]["System"]["VERSION"]

        except KeyError as err:
            log.warning("did not find any FortiClient EMS version number in response")
            raise GeneralWarning(
                "did not find any FortiClient EMS version number in response"
            ) from err

        return ems_version

    def login(self) -> int:
        """
        Login to the FortiClientEMS.

        Returns:
            int: status code from the FortiClient EMS logon
        """
        status = 401
        cookie_file = os.path.abspath(os.path.join(self.cookie_path, f"{self.hostname}.cookie"))
        if self.cookie_path:
            log.debug("searching cookie in %s", cookie_file)
            if os.path.isfile(cookie_file):
                log.debug("cookie exists. skipping login")
                with open(cookie_file, "rb") as cookiefile:
                    self.session.cookies.update(pickle.load(cookiefile))  # type: ignore

                try:
                    response = self.api("get", "/system/serial_number")
                    if (
                        "retval" in response.json()["result"]
                        and int(response.json()["result"]["retval"]) == 1
                    ):
                        log.debug(
                            "session with given cookie is valid (status: %s)", response.status_code
                        )
                        status = response.status_code

                except APIError as err:
                    log.debug("session with given cookie is invalid (status: %s)", err.code)
                    status = err.code

            else:
                log.debug("no cookie found for : %s", self.hostname)

        if status == 401:
            log.debug("login to %s", self.hostname)
            payload = {"name": self.username, "password": self.password}
            response = self.api("post", "/auth/signin", payload=payload)
            if response.status_code == 200 and self.cookie_path:
                log.debug("saving cookie for %s", self.hostname)
                with open(cookie_file, "wb") as cookiefile:
                    pickle.dump(self.session.cookies, cookiefile)

            status = response.status_code

        return status

    def logout(self) -> int:
        """
        Logout from FortiClient EMS.

        Returns:
            int: status code from the FortiClient EMS logout
        """
        response = self.api("get", "/auth/signout")
        log.debug("logged out from %s (status: %s)", self.hostname, response.status_code)
        return response.status_code
