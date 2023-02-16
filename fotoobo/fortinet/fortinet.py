"""
This is the Fortinet abstract base class (ABC) which is used to define some global and generic
variables and methods.
"""
import logging
from abc import ABC, abstractmethod
from time import time
from typing import Any, Dict, Optional

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

    def __init__(self, hostname: str, **kwargs: Any) -> None:
        """
        Set some initial parameters for the Fortinet super class.
        It also initializes a requests session. If you're making several requests to the same host,
        the underlying TCP connection will be reused, which can result in a significant performance
        increase. (https://docs.python-requests.org/en/master/user/advanced/)

        Args:
            hostname (str): the hostname of the Fortinet device to connect to
            **kwargs: additional arguments from the following list:
                proxy (str): proxy server to use to connect to the Fortinet device
                    If you need to connect to your Fortinet device through a proxy server you can
                    set it here as as string. If needed you may append the proxy server port with a
                    column to the proxy server. e.g. "proxy.local:8000"
                ssl_verify (bool): enable/disable SSL certificate check
                    When ssl_verify is enabled you have to install a trusted SSL certificate onto
                    the device you wish to connect to. If you set ssl_verify to false it will also
                    disable the warnings in urllib3. This prevents unwanted SSL warnings to be
                    logged.
                timeout (float): connection timeout in seconds
        """
        self.session = requests.Session()
        self.session.trust_env = False
        self.api_url: str = ""
        self.hostname: str = hostname.strip("/")
        self.session.proxies: Dict[str, Any] = {"http": None, "https": None}  # type: ignore
        if proxy := kwargs.get("proxy", ""):
            self.session.proxies = {"http": f"{proxy}", "https": f"{proxy}"}

        self.ssl_verify: bool = kwargs.get("ssl_verify", True)
        if not self.ssl_verify:
            urllib3.disable_warnings()

        self.timeout = kwargs.get("timeout", 3)
        self.type: str = ""

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
        API request to a Fortinet device.

        Args:
            method (str): request method from [get, post]
            url (str): rest API URL to request data from
            params (dict): dictionary with parameters (if needed)
            payload (dict): JSON body for post requests (if needed)
            timeout (float): the requests read timeout


        Returns:
            response: response from the request
        """
        full_url = f"{self.api_url}/{url.strip('/')}".strip("/")
        params = params or {}
        payload = payload or {}
        timeout = timeout or self.timeout
        start = time()

        try:
            if method.lower() == "get":
                response = self.session.get(
                    full_url,
                    params=params,
                    verify=self.ssl_verify,
                    timeout=timeout,
                )

            elif method.lower() == "post":
                response = self.session.post(
                    full_url,
                    headers=headers,
                    json=payload,
                    verify=self.ssl_verify,
                    timeout=timeout,
                )

            else:
                log.debug("unknown API method")
                raise GeneralError("unknown API method")

        except requests.exceptions.ConnectTimeout as err:
            log.debug(err)
            raise GeneralError(f"connection timeout ({self.hostname})") from err

        except requests.exceptions.ConnectionError as err:
            log.debug(err)
            error = "unknown connection error"
            try:
                if "Name or service not known" in err.args[0].reason.args[0]:
                    error = "name or service not known"

                elif "Connection refused" in err.args[0].reason.args[0]:
                    error = "connection refused"

            except (IndexError, AttributeError, TypeError):
                pass

            try:
                if (
                    err.args[0].reason.args[0].verify_message
                    == "unable to get local issuer certificate"
                ):
                    error = "unable to get local issuer certificate"
            except (IndexError, AttributeError, TypeError):
                pass

            raise GeneralError(f"{error} ({self.hostname})") from err

        except requests.exceptions.ReadTimeout as err:
            log.error(err)
            raise GeneralError(f"read timeout ({self.hostname})") from err

        log.debug(
            'request time: [bold green]%2dms[/] "%s %s"',
            ((time() - start) * 1000),
            method.upper(),
            full_url,
        )

        try:
            response.raise_for_status()
        except (requests.exceptions.HTTPError) as err:
            raise APIError(err) from err

        return response

    @staticmethod
    def get_vendor() -> str:
        """
        Returns the vendor of the product (which always is Fortinet).

        Returns:
            str: always returns "Fortinet" (what a cool method ;-)
        """
        return "Fortinet"

    @abstractmethod
    def get_version(self) -> str:
        """
        Gets the version of the corresponding system(s)
        """
