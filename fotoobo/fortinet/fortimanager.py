"""
FortiManager Class
"""

import logging
import re
from pathlib import Path
from time import sleep
from typing import Any, Optional

import requests

from .fortinet import Fortinet

log = logging.getLogger("fotoobo")


class FortiManager(Fortinet):  # pylint: disable=too-many-public-methods
    """
    Represents one FortiManager (digital twin)
    """

    def __del__(self) -> None:
        """The destructor"""
        if self.session_key and not self.session_path:
            self.logout()

    def __init__(self, hostname: str, username: str, password: str, **kwargs: Any) -> None:
        """
        Set some initial parameters.

        Args:
            hostname: The hostname of the FortiGate to connect to
            username: The username
            password: The password

        Keyword Args:
            session_path: The path where to load/save the FortiManager session key
            **kwargs:     See Fortinet class for more available arguments
        """
        super().__init__(hostname, **kwargs)
        self.api_url = f"https://{self.hostname}:{self.https_port}/jsonrpc"
        self.password = password
        self.username = username
        self.session_key: str = ""
        self.session_path: str = kwargs.get("session_path", "")
        self.type = "fortimanager"
        self.ignored_adoms = [
            "FortiAnalyzer",
            "FortiAuthenticator",
            "FortiCache",
            "FortiCarrier",
            "FortiClient",
            "FortiDDoS",
            "FortiDeceptor",
            "FortiFirewall",
            "FortiFirewallCarrier",
            "FortiMail",
            "FortiManager",
            "FortiNAC",
            "FortiProxy",
            "FortiSandbox",
            "FortiWeb",
            "Syslog",
            "Unmanaged_Devices",
            "others",
            "root",
            "rootp",
        ]

    def api_delete(self, url: str) -> requests.models.Response:
        """DELETE method for API requests

        Args:
            url: API endpoint to access

        Result:
            FortiManager result item
        """
        payload = {
            "method": "delete",
            "params": [{"url": f"{url}"}],
        }
        return self.api("post", payload=payload)

    def api_get(
        self, url: str, params: Optional[dict[str, Any]] = None, timeout: Optional[float] = None
    ) -> requests.models.Response:
        """GET method for API requests

        Args:
            url:     API endpoint to access
            params:  Additional query parameters if needed
            timeout: The requests read timeout in seconds

        Result:
            FortiManager result item
        """
        _params = {"url": f"{url}"}
        if params:
            _params = {**_params, **params}

        payload = {
            "method": "get",
            "params": [_params],
        }
        return self.api("post", payload=payload, timeout=timeout)

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
            Response from the request
        """
        if not self.session_key:
            self.login()

        payload = payload or {}
        if method.lower() == "post":
            payload["session"] = self.session_key

        return super().api(
            method, url, headers=headers, payload=payload, params=params, timeout=timeout
        )

    def assign_all_objects(self, adoms: str, policy: str) -> int:
        """
        Copies all objects from the global ADOM database to a given ADOM.

        Args:
            adoms:  The ADOM to assign the global policy/objects to. If you specify an invalid ADOM
                    name you'll get a permission error. You can specify multiple ADOMs by separating
                    them with a comma (no spaces)
            policy: Specify the global policy to assign [Default: 'default'].

        Returns:
            The id of the FortiManager task created or 0 (zero) if unsuccessful

        """
        task_id = 0
        adom_payload = []

        for adom in adoms.split(","):
            adom_payload.append({"adom": adom, "excluded": "disable"})

        payload = {
            "method": "exec",
            "params": [
                {
                    "data": {
                        "flags": ["cp_all_objs"],
                        "pkg": policy,
                        "target": adom_payload,
                    },
                    "url": "/securityconsole/assign/package",
                }
            ],
        }
        response = self.api("post", payload=payload)

        if response.status_code == 200:
            if response.json()["result"][0]["status"]["code"] == 0:
                task_id = response.json()["result"][0]["data"]["task"]
                log.debug("Assign task created with id '%s'", task_id)

            else:
                log.debug(
                    "Did not assign to '%s' with error '%s'",
                    adoms,
                    response.json()["result"][0]["status"]["message"],
                )
                task_id = 0

        return task_id

    def delete_adom_address(self, adom: str, address: str, dry: bool = False) -> dict[str, Any]:
        """
        Delete an address from an ADOM in FortiManager

        Args:
            adom:    The ADOM to delete the address from
            address: The address to delete
            dry:     Set to True to enable dry-run (no changes on FortiManager)

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}
        if not dry:
            url: str = f"/pm/config/adom/{adom}/obj/firewall/address/{address}"
            result = self.api_delete(url).json()["result"][0]

        else:
            log.info("DRY-RUN: Would remove address '%s' in ADOM '%s'", address, adom)

        return result

    def delete_adom_address_group(self, adom: str, group: str, dry: bool = False) -> dict[str, Any]:
        """
        Delete an address group from an ADOM in FortiManager

        Args:
            adom:  The ADOM to delete the address group from
            group: The address group to delete
            dry:   Set to True to enable dry-run (no changes on FortiManager)

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}
        if not dry:
            url: str = f"/pm/config/adom/{adom}/obj/firewall/addrgrp/{group}"
            result = self.api_delete(url).json()["result"][0]

        else:
            log.info("DRY-RUN: Would remove address group '%s' in ADOM '%s'", group, adom)

        return result

    def delete_adom_service(self, adom: str, service: str, dry: bool = False) -> dict[str, Any]:
        """
        Delete a service from an ADOM in FortiManager

        Args:
            adom:    The ADOM to delete the address from
            service: The service to delete
            dry:     Set to True to enable dry-run (no changes on FortiManager)

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}
        if not dry:
            url: str = f"/pm/config/adom/{adom}/obj/firewall/service/custom/{service}"
            result = self.api_delete(url).json()["result"][0]

        else:
            log.info("DRY-RUN: Would remove service '%s' in ADOM '%s'", service, adom)

        return result

    def delete_adom_service_group(self, adom: str, group: str, dry: bool = False) -> dict[str, Any]:
        """
        Delete a service group from an ADOM in FortiManager

        Args:
            adom:  The ADOM to delete the address group from
            group: The address group to delete
            dry:   Set to True to enable dry-run (no changes on FortiManager)

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}
        if not dry:
            url: str = f"/pm/config/adom/{adom}/obj/firewall/service/group/{group}"
            result = self.api_delete(url).json()["result"][0]

        else:
            log.info("DRY-RUN: Would remove service group '%s' in ADOM '%s'", group, adom)

        return result

    def delete_global_address(self, address: str, dry: bool = False) -> dict[str, Any]:
        """
        Delete a global address from FortiManager

        To be sure to not delete used objects we configure the FortiManager as follows:

            config system admin setting
                set objects-force-deletion disable

        Before deleting a global address object we have to check if it's in use in any ADOM. Only
        after we found that no ADOM uses the object we can safely delete it.

        Fortinet documentation links:\n
        https://docs.fortinet.com/document/fortimanager/7.0.12/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.2.7/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.4.3/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.6.0/administration-guide/322714

        Args:
            address: The global address to delete
            dry:     Set to True to enable dry-run (no changes on FortiManager)

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}

        # Get the address object with 'scope member' information
        address_object = self.get_global_address(address, scope_member=True)
        if address_object["status"]["code"] == 0:
            # Generate a list of ADOMs where the object is used. Therefore we get the address object
            # from FortiManager with the 'scope member' option. If the object is used in any ADOM it
            # is listed in the key 'scope member'. If the object is not used in any ADOM the
            # 'scope member' key is not present.
            if "scope member" in address_object["data"]:
                used_adoms = [_["name"] for _ in address_object["data"]["scope member"]]
                log.debug("'%s' is used in ADOM '%s'", address, ",".join(used_adoms))

            else:
                used_adoms = []

            if not dry:
                # Try to delete the address group object in every ADOM
                blocked_adoms = []
                for adom in used_adoms:
                    if self.delete_adom_address(adom, address)["status"]["code"] not in [
                        -3,
                        0,
                    ]:
                        blocked_adoms.append(adom)

                if blocked_adoms:
                    log.warning("'%s' blocked by ADOM '%s'", address, ",".join(blocked_adoms))
                    result = address_object
                    result["status"] = {
                        "code": 601,
                        "message": f"Used in ADOM {','.join(blocked_adoms)}",
                    }

                else:
                    # Try to delete the global address object
                    url: str = f"/pm/config/global/obj/firewall/address/{address}"
                    result = self.api_delete(url).json()["result"][0]

            else:
                log.info("DRY-RUN: Would remove global address '%s'", address)

        else:
            result = address_object

        return result

    def delete_global_address_group(self, group: str, dry: bool = False) -> dict[str, Any]:
        """
        Delete a global address group from FortiManager

        To be sure to not delete used objects we configure the FortiManager as follows:

            config system admin setting
                set objects-force-deletion disable

        Before deleting a global address group object we have to check if it's in use in any ADOM.
        Only after we found that no ADOM uses the object we can safely delete it.

        Fortinet documentation links:\n
        https://docs.fortinet.com/document/fortimanager/7.0.12/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.2.7/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.4.3/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.6.0/administration-guide/322714

        Args:
            group: The global address group to delete
            dry:   Set to True to enable dry-run (no changes on FortiManager)

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}

        # Get the address group object with 'scope member' information
        address_group_object = self.get_global_address_group(group, scope_member=True)
        if address_group_object["status"]["code"] == 0:

            # Generate a list of ADOMs where the object is used. Therefore we get the address group
            # object from FortiManager with the 'scope member' option. If the object is used in any
            # ADOM it is listed in the key 'scope member'. If the object is not used in any ADOM the
            # 'scope member' key is not present.
            if "scope member" in address_group_object["data"]:
                used_adoms = [_["name"] for _ in address_group_object["data"]["scope member"]]
                log.debug("'%s' is used in ADOM '%s'", group, ",".join(used_adoms))

            else:
                used_adoms = []

            if not dry:
                # Try to delete the address group object in every ADOM
                blocked_adoms = []
                for adom in used_adoms:
                    if not self.delete_adom_address_group(adom, group)["status"]["code"] in [-3, 0]:
                        blocked_adoms.append(adom)

                if blocked_adoms:
                    log.warning("'%s' blocked by ADOM '%s'", group, ",".join(blocked_adoms))
                    result = address_group_object
                    result["status"] = {
                        "code": 601,
                        "message": f"Used in ADOM {','.join(blocked_adoms)}",
                    }

                else:
                    # Try to delete the global address group object
                    url: str = f"/pm/config/global/obj/firewall/addrgrp/{group}"
                    result = self.api_delete(url).json()["result"][0]

            else:
                log.info("DRY-RUN: Would remove global address group '%s'", group)

        else:
            result = address_group_object

        return result

    def delete_global_service(self, service: str, dry: bool = False) -> dict[str, Any]:
        """
        Delete a global service from FortiManager

        To be sure to not delete used objects we configure the FortiManager as follows:

            config system admin setting
                set objects-force-deletion disable

        Before deleting a global service object we have to check if it's in use in any ADOM. Only
        after we found that no ADOM uses the object we can safely delete it.

        Fortinet documentation links:\n
        https://docs.fortinet.com/document/fortimanager/7.0.12/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.2.7/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.4.3/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.6.0/administration-guide/322714

        Args:
            service: The global service to delete
            dry:     Set to True to enable dry-run (no changes on FortiManager)

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}

        # Get the service object with 'scope member' information
        service_object = self.get_global_service(service, scope_member=True)
        if service_object["status"]["code"] == 0:

            # Generate a list of ADOMs where the object is used. Therefore we get the service object
            # from FortiManager with the 'scope member' option. If the object is used in any ADOM it
            # is listed in the key 'scope member'. If the object is not used in any ADOM the
            # 'scope member' key is not present.
            if "scope member" in service_object["data"]:
                used_adoms = [_["name"] for _ in service_object["data"]["scope member"]]
                log.debug("'%s' is used in ADOM '%s'", service, ",".join(used_adoms))

            else:
                used_adoms = []

            if not dry:
                # Try to delete the address group  object in every ADOM
                blocked_adoms = []
                for adom in used_adoms:
                    if not self.delete_adom_service(adom, service)["status"]["code"] in [-3, 0]:
                        blocked_adoms.append(adom)

                if blocked_adoms:
                    log.warning("'%s' blocked by ADOM '%s'", service, ",".join(blocked_adoms))
                    result = service_object
                    result["status"] = {
                        "code": 601,
                        "message": f"Used in ADOM {','.join(blocked_adoms)}",
                    }

                else:
                    # Try to delete the global service object
                    url: str = f"/pm/config/global/obj/firewall/service/custom/{service}"
                    result = self.api_delete(url).json()["result"][0]

            else:
                log.info("DRY-RUN: Would remove global service '%s'", service)

        else:
            result = service_object

        return result

    def delete_global_service_group(self, group: str, dry: bool = False) -> dict[str, Any]:
        """
        Delete a global service group from FortiManager

        To be sure to not delete used objects we configure the FortiManager as follows:

            config system admin setting
                set objects-force-deletion disable

        Before deleting a global service group object we have to check if it's in use in any ADOM.
        Only after we found that no ADOM uses the object we can safely delete it.

        Fortinet documentation links:\n
        https://docs.fortinet.com/document/fortimanager/7.0.12/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.2.7/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.4.3/administration-guide/322714
        https://docs.fortinet.com/document/fortimanager/7.6.0/administration-guide/322714

        Args:
            group: The global service group to delete
            dry:   Set to True to enable dry-run (no changes on FortiManager)

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}

        # Get the service group object with 'scope member' information
        service_group_object = self.get_global_service_group(group, scope_member=True)
        if service_group_object["status"]["code"] == 0:

            # Generate a list of ADOMs where the object is used. Therefore we get the service group
            # object from FortiManager with the 'scope member' option. If the object is used in any
            # ADOM it is listed in the key 'scope member'. If the object is not used in any ADOM the
            # 'scope member' key is not present.
            if "scope member" in service_group_object["data"]:
                used_adoms = [_["name"] for _ in service_group_object["data"]["scope member"]]
                log.debug("'%s' is used in ADOM '%s'", group, ",".join(used_adoms))

            else:
                used_adoms = []

            if not dry:
                # Try to delete the service group object in every ADOM
                blocked_adoms = []
                for adom in used_adoms:
                    if not self.delete_adom_service_group(adom, group)["status"]["code"] in [-3, 0]:
                        blocked_adoms.append(adom)

                if blocked_adoms:
                    log.warning("'%s' blocked by ADOM '%s'", group, ",".join(blocked_adoms))
                    result = service_group_object
                    result["status"] = {
                        "code": 601,
                        "message": f"Used in ADOM {','.join(blocked_adoms)}",
                    }

                else:
                    # Try to delete the global service group object
                    url: str = f"/pm/config/global/obj/firewall/service/group/{group}"
                    result = self.api_delete(url).json()["result"][0]

            else:
                log.info("DRY-RUN: Would remove global service group '%s'", group)

        else:
            result = service_group_object

        return result

    def get_adoms(self, ignored_adoms: Optional[list[str]] = None) -> list[Any]:
        """
        Get FortiManager ADOM list

        Some of the ADOMs are ignored by default as the are not used in most cases

        Returns:
            List of FortiManager ADOMs
        """
        if not ignored_adoms:
            ignored_adoms = self.ignored_adoms

        fmg_adoms: list[Any] = []
        payload = {"method": "get", "params": [{"url": "/dvmdb/adom"}]}
        response = self.api("post", payload=payload)

        for adom in response.json()["result"][0]["data"]:
            if not adom["name"] in ignored_adoms:
                fmg_adoms.append(adom)

        return fmg_adoms

    def get_global_address(self, address: str, scope_member: bool = False) -> dict[str, Any]:
        """
        Get an address object from global ADOM

        Args:
            address:      The address to get
            scope_member: Whether the scope member attribute should be included in the response

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}
        url: str = f"/pm/config/global/obj/firewall/address/{address}"

        if scope_member:
            params = {"option": ["scope member"]}
            response = self.api_get(url, params)

        else:
            response = self.api_get(url)

        result = response.json()["result"][0]

        return result

    def get_global_addresses(self) -> dict[str, Any]:
        """
        Get the global address database

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = self.api_get(
            "/pm/config/global/obj/firewall/address",
            timeout=10,
        ).json()["result"][0]

        return result

    def get_global_address_group(self, group: str, scope_member: bool = False) -> dict[str, Any]:
        """
        Get an address group object from the global ADOM

        Args:
            group:        The address group to get
            scope_member: Whether the scope member attribute should be included in the response

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}
        url: str = f"/pm/config/global/obj/firewall/addrgrp/{group}"

        if scope_member:
            params = {"option": ["scope member"]}
            response = self.api_get(url, params)

        else:
            response = self.api_get(url)

        result = response.json()["result"][0]

        return result

    def get_global_address_groups(self) -> dict[str, Any]:
        """
        Get the global address group database

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = self.api_get(
            "/pm/config/global/obj/firewall/addrgrp",
            timeout=10,
        ).json()["result"][0]

        return result

    def get_global_service(self, service: str, scope_member: bool = False) -> dict[str, Any]:
        """
        Get a service object from global ADOM

        Args:
            service:      The service to get
            scope_member: Whether the scope member attribute should be included in the response

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}
        url: str = f"/pm/config/global/obj/firewall/service/custom/{service}"

        if scope_member:
            params = {"option": ["scope member"]}
            response = self.api_get(url, params)

        else:
            response = self.api_get(url)

        result = response.json()["result"][0]

        return result

    def get_global_services(self) -> dict[str, Any]:
        """
        Get the global services database

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = self.api_get(
            "/pm/config/global/obj/firewall/service/custom",
            timeout=10,
        ).json()["result"][0]

        return result

    def get_global_service_group(self, group: str, scope_member: bool = False) -> dict[str, Any]:
        """
        Get a service group object from the global ADOM

        Args:
            group:        The address group to get
            scope_member: Whether the scope member attribute should be included in the response

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = {}
        url: str = f"/pm/config/global/obj/firewall/service/group/{group}"

        if scope_member:
            params = {"option": ["scope member"]}
            response = self.api_get(url, params)

        else:
            response = self.api_get(url)

        result = response.json()["result"][0]

        return result

    def get_global_service_groups(self) -> dict[str, Any]:
        """
        Get the global network service group database

        Returns:
            FortiManager result item
        """
        result: dict[str, Any] = self.api_get(
            "/pm/config/global/obj/firewall/service/group",
            timeout=10,
        ).json()["result"][0]

        return result

    def get_version(self) -> str:
        """
        Get FortiManager version.

        Returns:
            FortiManager version
        """
        fmg_version: str = ""
        payload = {"method": "get", "params": [{"url": "/sys/status"}]}
        response = self.api("post", payload=payload)

        if response.status_code == 200:
            try:
                match: Optional[re.Match[Any]] = re.search(
                    r"(v\d+\.\d+\.\d+)-", response.json()["result"][0]["data"]["Version"]
                )
                fmg_version = str(match.group(1))  # type: ignore

            except (KeyError, IndexError, AttributeError):
                log.debug("did not find any FortiManager version number in response")

        return fmg_version

    def login(self) -> int:
        """
        Login to the FortiManager.

        If the login to the FortiManager was successful it stores the session key in the object.
        We do not use requests.session as the session key is just a string which is saved directly.

        Returns:
            Status code from the FortiManager login
        """
        status: int = 401

        if self.session_path:
            session_file = Path(self.session_path).expanduser() / f"{self.hostname}.key"
            if session_file.exists():
                log.debug("Loading session key from file '%s'", session_file)

                with session_file.open(encoding="UTF-8") as file:
                    self.session_key = file.read()
                    payload = {
                        "method": "get",
                        "params": [{"url": "/sys/status"}],
                        "session": self.session_key,
                    }
                    response = super().api("post", payload=payload)
                    status = response.status_code

                    if (
                        response.status_code == 200
                        and response.json()["result"][0]["status"]["code"] == 0
                    ):
                        log.debug("Session key is still valid")

                    else:
                        log.debug("Session key is invalid")
                        self.session_key = ""

            else:
                log.debug("Session file '%s' does not exist", session_file)

        if not self.session_key and self.username and self.password:
            log.debug("Login to '%s'", self.hostname)
            payload = {
                "method": "exec",
                "params": [
                    {
                        "data": {"passwd": self.password, "user": self.username},
                        "url": "/sys/login/user",
                    }
                ],
            }
            response = super().api("post", payload=payload)
            if response.status_code == 200:
                if "session" in response.json():
                    log.debug("Storing session key")
                    self.session_key = response.json()["session"]

                    if self.session_path:
                        log.debug("Saving session key into file '%s'", session_file)

                        with session_file.open("w", encoding="UTF-8") as file:
                            file.write(self.session_key)

            status = response.status_code

        return status

    def logout(self) -> int:
        """
        Logout from FortiManager.

        Returns:
            Status code from the FortiManager logout
        """
        payload: dict[str, Any] = {
            "method": "exec",
            "params": [{"url": "/sys/logout"}],
            "session": self.session_key,
        }
        response = self.api("post", payload=payload)
        self.session_key = ""
        return response.status_code

    def post(self, adom: str, payloads: Any) -> list[str]:
        """
        POST method to FortiManager.

        You can pass a single payload (Dict) or a list of payloads (List of Dict).

        Args:
            adom:     The ADOM name to issue the set commands to. If you wish to update the
                      Global ADOM specify 'global' as ADOM.
            payloads: One payload (Dict) or a list of payloads (List of Dict)

        Returns:
            Amount of errors occurred during the set command
        """
        # if payload is a dict convert it to a list with one dict in it.
        if isinstance(payloads, dict):
            payloads = [payloads]

        results = []

        for payload in payloads:
            for i, _ in enumerate(payload["params"]):
                # Here we have to replace the {adom} in the URL entry:
                #    for Global: /pm/config/ global      /obj/firewall/address/{address}
                #    for ADOM:   /pm/config/ adom/{adom} /obj/firewall/address/{address}
                #                            \_________/ --> this is the {adom} part in the payload
                adom_str = "global" if adom.lower() == "global" else f"adom/{adom}"
                payload["params"][i]["url"] = payload["params"][i]["url"].replace(
                    "{adom}", adom_str
                )

            response = self.api("post", payload=payload, timeout=10)
            for result in response.json()["result"]:
                if result["status"]["code"] != 0:
                    log.error("%s: %s", result["status"]["message"], result["url"])
                    results.append(
                        f"{result['status']['message']}: "
                        f"{result['url']} "
                        f"(code: {result['status']['code']})"
                    )

        return results

    def wait_for_task(self, task_id: int, timeout: int = 60) -> list[Any]:
        """
        Wait for a task with a given id for its end and returns the message(s).

        Args:
            id:      Task id to wait for
            timeout: Timeout in seconds

        Returns:
            Message list
        """
        log.debug("Waiting for task id '%s'", task_id)
        messages: list[Any] = []
        payload = {
            "method": "get",
            "params": [{"url": f"/task/task/{task_id}"}],
        }
        percent_cache = -1

        while timeout:
            response = self.api("post", payload=payload)
            percent = response.json()["result"][0]["data"]["percent"]
            if percent > percent_cache:
                log.debug("FortiManager task progress: '%s%%'", percent)
                percent_cache = percent

            if response.status_code == 200:
                if percent >= 100:
                    break

            sleep(1)
            timeout -= 1

        payload = {
            "method": "get",
            "params": [{"url": f"/task/task/{task_id}/line"}],
        }
        response = self.api("post", payload=payload)

        if response.status_code == 200:
            messages = response.json()["result"][0]["data"]
            # enrich the message(s) with the task_id (otherwise it will be lost)
            for i, _ in enumerate(messages):
                messages[i]["task_id"] = task_id

        return messages
