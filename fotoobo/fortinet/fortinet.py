"""
This is the Fortinet abstract base class (ABC) which is used to define some global and generic
variables and methods.
"""

import logging
from abc import ABC, abstractmethod
from time import time
from typing import Any, Optional, Union

import requests
import urllib3

from fotoobo.exceptions import APIError, GeneralError

log = logging.getLogger("fotoobo")


class Fortinet(ABC):
    """
    This is the Fortinet abstract base class. All other Fortinet product classes should inherit
    from this class. If there are methods which have to be defined in every subclass it has to be
    defined here with the abstractmethod decorator.
    """

    # Use the ALLOWED_HTTP_METHODS class constant to define the supported HTTP methods. By default
    # we should support GET and POST but you may override this list of supported methods in every
    # subclass. Treat this setting as a constant which must not be redefined during runtime.
    ALLOWED_HTTP_METHODS = ["GET", "POST"]

    def __init__(self, hostname: str, **kwargs: Any) -> None:
        """
        Set some initial parameters for the Fortinet super class.

        It also initializes a requests session. If you're making several requests to the same host,
        the underlying TCP connection will be reused, which can result in a significant performance
        increase. (https://docs.python-requests.org/en/master/user/advanced/)

        Args:
            hostname: The hostname of the Fortinet device to connect to

        Keyword Args:
            https_port: The tcp port number to connect to the https api
                If you do not specify a port number it is set to 443 by default.
            proxy: The Proxy server to use to connect to the Fortinet device
                If you need to connect to your Fortinet device through a proxy server you can
                set it here as as string. If needed you may append the proxy server port with a
                column to the proxy server. e.g. "proxy.local:8000".
            ssl_verify: Enable or disable SSL certificate check
                When ssl_verify is enabled you have to install a trusted SSL certificate onto
                the device you wish to connect to. If you set ssl_verify to false it will also
                disable the warnings in urllib3. This prevents unwanted SSL warnings to be
                logged.
            timeout: Connection timeout in seconds
        """
        self.api_url: str = ""
        self.hostname: str = hostname
        self.https_port: int = kwargs.get("https_port", 443)
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.proxies: dict[str, Any] = {"http": None, "https": None}  # type: ignore

        if proxy := kwargs.get("proxy", ""):
            self.session.proxies = {"http": f"{proxy}", "https": f"{proxy}"}

        self.ssl_verify: Union[bool, str] = kwargs.get("ssl_verify", True)
        if not self.ssl_verify:
            urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

        self.timeout = kwargs.get("timeout", 3)
        self.type: str = ""

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
        API request to a Fortinet device.

        Args:
            method:     HTTP request method
            url:        Rest API URL to request data from
            headers:    Dictionary with headers (if needed)
            params:     Dictionary with parameters (if needed)
            payload:    JSON body for post requests (if needed)
            timeout:    The requests read timeout

        Returns:
            Response from the request
        """
        full_url = f"{self.api_url}/{url.strip('/')}".strip("/")
        timeout = timeout or self.timeout
        start = time()

        if method.upper() not in self.ALLOWED_HTTP_METHODS:
            error = f"HTTP method '{method.upper()}' is not implemented"
            log.error(error)
            raise NotImplementedError(error)

        try:
            response: requests.Response = getattr(self.session, method.lower())(
                full_url,
                headers=headers,
                json=payload,
                params=params,
                timeout=timeout,
                verify=self.ssl_verify,
            )

        except requests.exceptions.SSLError as err:
            log.debug(err)
            error = "Unknown SSL error"

            try:
                if (
                    err.args[0].reason.args[0].verify_message
                    == "unable to get local issuer certificate"
                ):
                    error = "Unable to get local issuer certificate"

            except (AttributeError, IndexError):
                pass

            raise GeneralError(f"{error} ({self.hostname})") from err

        except requests.exceptions.ConnectTimeout as err:
            log.debug(err)
            raise GeneralError(f"Connection timeout ({self.hostname})") from err

        except requests.exceptions.ConnectionError as err:
            log.debug(err)
            error = "Unknown connection error"

            try:
                if "Name or service not known" in err.args[0].reason.args[0]:
                    error = "Name or service not known"

                elif "Connection refused" in err.args[0].reason.args[0]:
                    error = "Connection refused"

            except (IndexError, AttributeError, TypeError):
                pass

            raise GeneralError(f"{error} ({self.hostname})") from err

        except requests.exceptions.ReadTimeout as err:
            log.error(err)
            raise GeneralError(f"Read timeout ({self.hostname})") from err

        log.debug(
            'Request time: [bold green]%2dms[/] "%s %s"',
            ((time() - start) * 1000),
            method.upper(),
            full_url,
        )

        try:
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            raise APIError(err) from err

        return response

    @staticmethod
    def get_vendor() -> str:
        """
        Returns the vendor of the product (which always is Fortinet).

        Returns:
            Always returns "Fortinet" (what a cool method ;-)
        """
        return "Fortinet"

    @abstractmethod
    def get_version(self) -> str:
        """
        Gets the version of the corresponding system(s)
        """
