"""The Hashicorp Vault helper module for approle

The official API documentation is here: https://developer.hashicorp.com/vault/api-docs

We intend to use direct https requests without the dependency to another module (like hvac). This
makes this module very independent.
"""

import logging
from pathlib import Path
from typing import Any, Optional, Union

import requests
import urllib3

from fotoobo.exceptions.exceptions import GeneralError

log = logging.getLogger("fotoobo")


class Client:  # pylint: disable=too-many-instance-attributes
    """The approle helper class for the Hashicorp Vault

    This vault client gives you methods for your login with approle and maintaining token and data
    requests.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        url: str,
        namespace: str,
        data_path: str,
        role_id: str,
        secret_id: str,
        ssl_verify: Union[bool, str] = True,
        token_file: Optional[str] = None,
        token_ttl_limit: int = 0,
    ) -> None:
        """Initialize the vault client

        Args:
            url:                The URL of your vault service (eg. https://vault.local:443)
            namespace:          The namespace of your vault
            data_path:          The path where the vault data for fotoobo is stored
            role_id:            The approle role_id
            secret_id:          The approle secret_id
            ssl_verify:         Enable/disable SSL certificate check
                When ssl_verify is enabled you have to install a trusted SSL certificate onto
                the device you wish to connect to. If you set ssl_verify to false it will also
                disable the warnings in urllib3. This prevents unwanted SSL warnings to be
                logged.
            token_file:         The file to store the access token to. If no file is given the token
                                is not loaded or stored to a file and every execution will issue a
                                new token.
            token_ttl_limit:    Set a token limit. If the ttl of a token falls below this limit we
                                will automatically issue a new token. Default: 0
        """
        log.debug("Initialize the vault client")
        self.namespace: str = namespace
        self.data_path: str = data_path
        self.role_id: str = role_id
        self.secret_id: str = secret_id
        self.token: str = ""
        self.token_file: Optional[Path] = None
        self.token_ttl_limit: int = token_ttl_limit
        self.url: str = url.strip("/")
        self.ssl_verify: Union[bool, str] = ssl_verify
        if not self.ssl_verify:
            log.warning("SSL verify for vault service is disabled which may be a security issue")
            urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

        log.debug("vault_client_url: '%s'", self.url)
        log.debug("vault_client_ssl_verify: '%s'", self.ssl_verify)
        log.debug("vault_client_namespace: '%s'", self.namespace)
        log.debug("vault_client_data_path: '%s'", self.data_path)
        log.debug("vault_client_role_id: '%s...%s'", self.role_id[:4], self.role_id[-5:-1])
        log.debug("vault_client_secret_id: '%s...%s'", self.secret_id[:4], self.secret_id[-5:-1])
        log.debug("vault_client_token_ttl_limit: '%s'", self.token_ttl_limit)

        if token_file:
            self.token_file = Path(token_file).expanduser()
            log.debug("vault_client_token_file: '%s'", self.token_file)
            self.load_token()

    def get_data(self, timeout: int = 3) -> Any:
        """Get data from the key/value store

        Args:
            timeout:    The time before a request to the vault is cancelled

        Returns:
            The date from the vault or the error that occured

        Raises:
            GeneralError: If no token could be retreived
        """
        if not self.token and not self.get_token():
            error_message = "Unable to get vault token"
            log.error(error_message)
            raise GeneralError(error_message)

        url = f"{self.url}/{self.data_path.strip('/')}"
        log.debug("Get data from '%s'", url)
        headers = {
            "X-Vault-Token": self.token,
            "X-Vault-Namespace": self.namespace,
        }
        response = requests.get(url=url, headers=headers, timeout=timeout, verify=self.ssl_verify)

        if response.ok:
            log.debug("Response status_code is '%s'", response.status_code)
            return {"ok": response.json()}

        log.warning("Resonse is '%s %s'", response.status_code, response.reason)
        return {
            "error": {
                "status_code": response.status_code,
                "reason": response.reason,
                "content": response.content,
            }
        }

    def get_token(self, timeout: int = 3) -> bool:
        """Get a new token from the vault service by providing role_id and secret_id

        Args:
            timeout: The time before a request to the vault is cancelled
        """
        url = f"{self.url}/v1/auth/approle/login"
        log.debug("Get new token from '%s'", url)
        data = {"role_id": self.role_id, "secret_id": self.secret_id}
        self.token = ""
        try:
            response = requests.post(url, data=data, timeout=timeout, verify=self.ssl_verify)
            log.debug("Response status_code is '%s'", response.status_code)
            if response.ok:
                self.token = response.json()["auth"]["client_token"]
                if self.token_file:
                    self.save_token()

        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as err:
            log.error("Request Error: %s", str(err))

        return bool(self.token)

    def load_token(self) -> bool:
        """Load the token from a file

        Open a text file with a vault token and validate the token against the vault.

        Returns:
            True if the token is valid, otherwise False
        """
        try:
            log.debug("Load token from file '%s'", str(self.token_file))
            self.token = self.token_file.read_text(encoding="utf-8")  # type: ignore
            self.validate_token()

        except FileNotFoundError:
            log.warning("Token file '%s' not found", str(self.token_file))

        return bool(self.token)

    def save_token(self) -> bool:
        """Save the vault token to a text file

        Returns:
            True if a token is set, otherwise False
        """
        if self.token:
            log.debug("Save token to file '%s'", str(self.token_file))
            self.token_file.write_text(self.token, encoding="utf-8")  # type: ignore

        return bool(self.token)

    def validate_token(self, timeout: int = 3) -> bool:
        """Check if the token still is valid

        Validate the Vault token against the Vault service. If the token ttl is lower then the
        token_ttl_limit the token is cleared. This prevents a token with ttl short before 0 to be
        used in future calls. Instead a new token should be requestsed.

        Args:
            timeout: The time before a request to the Vault service is cancelled

        Returns:
            True if the token is valid, otherwise False
        """
        url = f"{self.url}/v1/auth/token/lookup-self"
        log.debug("Check if vault token still is valid")
        headers = {"X-Vault-Token": self.token}
        try:
            response = requests.get(
                url=url, headers=headers, timeout=timeout, verify=self.ssl_verify
            )
            log.debug("Response status_code is '%s'", response.status_code)
            if response.ok:
                log.debug("Vault token is valid for '%s' seconds", response.json()["data"]["ttl"])
                log.debug("vault_client_token: '%s...%s'", self.token[:8], self.token[-5:-1])
                if response.json()["data"]["ttl"] < self.token_ttl_limit:
                    log.debug("Invalidate token due to ttl limit")
                    self.token = ""

            else:
                log.debug("Token is not valid")
                self.token = ""

        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as err:
            self.token = ""
            log.error("Request Error: %s", str(err))

        return bool(self.token)
