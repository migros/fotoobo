"""
FortiCloud Class
"""

import logging
from pathlib import Path
from typing import Any, Optional

import requests

from fotoobo.exceptions.exceptions import APIError, GeneralWarning

from .fortinet import Fortinet

log = logging.getLogger("fotoobo")


class FortiCloudAsset(Fortinet):
    """
    Represents the FortiCloud Asset Management (digital twin)

    Helpful documentation links:
    - https://fndn.fortinet.net/index.php?/fortiapi/55-asset-management-formerly-forticare-registration/4638/55/Folder/ # pylint: disable=line-too-long
    - https://docs.fortinet.com/document/forticloud/25.2.0/identity-access-management-iam/19322/accessing-fortiapis # pylint: disable=line-too-long
    """

    ALLOWED_HTTP_METHODS = ["POST"]

    def __init__(self, username: str, password: str, **kwargs: Any) -> None:
        """
        Set some initial parameters.

        Args:
            username: The username
            password: The password

        Keyword Args:
            token_path: The path where to load/save the access token
            **kwargs:  See Fortinet class for more available arguments
        """
        super().__init__("support.fortinet.com", **kwargs)
        self.api_url = f"https://{self.hostname}:{self.https_port}/ES/api/registration/v3"
        self.password = password
        self.username = username
        self.access_token: str = ""
        self.token_path: str = kwargs.get("token_path", "")
        self.type = "forticloudasset"

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
        API request to a FortiManager device.

        It uses the super.api method but it has to enrich the payload in post requests with the
        needed session key.

        Args:
            method:  Request method from [get, post]
            url:     Rest API URL to request data from
            headers: Dictionary with headers (if needed)
            params:  Dictionary with parameters (if needed)
            payload: JSON body for post requests (if needed)
            timeout: The requests read timeout in seconds

        Returns:
            Response: Response object from the request
        """
        if not self.access_token:
            self.login()

        payload = payload or {}
        headers = headers or {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        return super().api(
            method, url, headers=headers, payload=payload, params=params, timeout=timeout
        )

    def get_version(self) -> str:
        """
        Get FortiCloud API version.

        Returns:
            FortiCloud API version
        """
        fc_version: str = ""

        try:
            fc_version = self.post(url="/folders/list")["version"]

        except APIError as err:
            log.warning("'%s' returned: '%s'", self.hostname, err)
            raise GeneralWarning(f"{self.hostname} returned: {err}") from err

        return fc_version

    def login(self) -> int:
        """
        Login to the FortiCloud.

        If the login to the FortiCloud was successful it stores the access token in the object.
        We do not use requests.session as the access token is just a string which is saved directly.

        Returns:
            Status code from the FortiCloud login
        """
        status: int = 401

        if self.token_path:
            token_file = Path(self.token_path).expanduser() / f"{self.hostname}.token"
            if token_file.exists():
                log.debug("Loading access token from file '%s'", token_file)

                with token_file.open(encoding="UTF-8") as file:
                    self.access_token = file.read()

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.access_token}",
                }
                try:
                    response = requests.post(
                        url=f"{self.api_url}/folders/list",
                        headers=headers,
                        verify=self.ssl_verify,
                        timeout=10,
                    )
                    status = response.status_code

                    if response.status_code == 200:
                        log.debug("Access token is still valid")

                    else:
                        self.access_token = ""
                        log.debug("Access token is invalid")

                except ValueError:
                    self.access_token = ""
                    log.debug("Access token is invalid")

            else:
                log.debug("Token file '%s' does not exist", token_file)

        if not self.access_token and self.username and self.password:
            log.debug("Login to '%s'", self.hostname)
            url = "https://customerapiauth.fortinet.com/api/v1/oauth/token/"
            payload = {
                "username": self.username,
                "password": self.password,
                "client_id": "assetmanagement",
                "grant_type": "password",
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                url, headers=headers, json=payload, verify=self.ssl_verify, timeout=10
            )

            if response.status_code == 200:
                if "access_token" in response.json():
                    self.access_token = response.json()["access_token"]
                    if self.token_path:
                        log.debug("Saving access token into file '%s'", token_file)

                        with token_file.open("w", encoding="UTF-8") as file:
                            file.write(self.access_token)

            status = response.status_code

        return status

    def post(self, url: str, payload: Optional[dict[str, Any]] = None) -> Any:
        """
        POST method to FortiCloud.

        You can pass a single payload (dict) or a list of payloads (list of dict).

        Args:
            payload: The payload to send with the request

        Returns:
            The result of the request
        """
        payload = payload or {}
        response = self.api("post", url=url, payload=payload, timeout=10)

        return response.json()
