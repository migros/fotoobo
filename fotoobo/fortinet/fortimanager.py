"""
FortiManager Class
"""
import logging
import re
from pathlib import Path
from time import sleep
from typing import Any, Dict, List, Optional

import requests

from .fortinet import Fortinet

log = logging.getLogger("fotoobo")


class FortiManager(Fortinet):
    """
    Represents one FortiManager (digital twin)
    """

    def __init__(self, hostname: str, username: str, password: str, **kwargs: Any) -> None:
        """
        Set some initial parameters.

        Args:
            hostname:       The hostname of the FortiGate to connect to
            username:       The Username
            password:       The password

        Keyword Args:
            session_dir:    The path where to load/save the FortiManager session key
            **kwargs:       See Fortinet class for more available arguments
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

    def __del__(self) -> None:
        """The destructor"""
        if self.session_key and not self.session_path:
            self.logout()

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
        API request to a FortiManager device.

        It uses the super.api method but it has to enrich the payload in post requests with the
        needed session key.

        Args:
            method:     Request method from [get, post]
            url:        Rest API URL to request data from
            params:     Dictionary with parameters (if needed)
            payload:    JSON body for post requests (if needed)
            timeout:    The requests read timeout in seconds

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
            adoms (str): The ADOM to assign the global policy/objects to. If you specify an invalid
                ADOM name you'll get a permission error. You can specify multiple ADOMs by
                separating them with a comma (no spaces)

            policy (str): Specify the global policy to assign [Default: 'default'].

        Returns:
            int: The id of the FortiManager task created or 0 (zero) if unsuccessful

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
                log.debug("assign task created with id %s", task_id)
            else:
                log.debug(
                    "did not assign to '%s' with error '%s'",
                    adoms,
                    response.json()["result"][0]["status"]["message"],
                )
                task_id = 0

        return task_id

    def get_adoms(self, ignored_adoms: Optional[List[str]] = None) -> List[Any]:
        """
        Get FortiManager ADOM list

        Some of the ADOMs are ignored by default as the are not used in most cases

        Returns:
            list: list of FortiManager ADOMs
        """
        if not ignored_adoms:
            ignored_adoms = self.ignored_adoms
        fmg_adoms: List[Any] = []
        payload = {"method": "get", "params": [{"url": "/dvmdb/adom"}]}
        response = self.api("post", payload=payload)
        for adom in response.json()["result"][0]["data"]:
            if not adom["name"] in ignored_adoms:
                fmg_adoms.append(adom)

        return fmg_adoms

    def get_version(self) -> str:
        """
        Get FortiManager version.

        Returns:
            str: version
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
            int: status code from the FortiManager login
        """
        status: int = 401

        if self.session_path:
            session_file = Path(self.session_path).expanduser() / f"{self.hostname}.key"
            if session_file.exists():
                log.debug("loading session key from file '%s'", session_file)
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
                log.debug("session file '%s' does ot exist", session_file)

        if not self.session_key and self.username and self.password:
            log.debug("login to %s", self.hostname)
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
                    log.debug("store session key")
                    self.session_key = response.json()["session"]
                    if self.session_path:
                        log.debug("saving session key into file '%s'", session_file)
                        with session_file.open("w", encoding="UTF-8") as file:
                            file.write(self.session_key)

            status = response.status_code

        return status

    def logout(self) -> int:
        """
        Logout from FortiManager.

        Returns:
            int: status code from the FortiManager logout
        """
        payload: Dict[str, Any] = {
            "method": "exec",
            "params": [{"url": "/sys/logout"}],
            "session": self.session_key,
        }
        response = self.api("post", payload=payload)
        self.session_key = ""
        return response.status_code

    def post(self, adom: str, payloads: Any) -> List[str]:
        """
        POST method to FortiManager.

        You can pass a single payload (Dict) or a list of payloads (List of Dict).

        Args:
            adom (str): the ADOM name to issue the set commands to. If you wish to update the
                        Global ADOM specify 'global' as ADOM.

            payload(s) (Any): one payload (Dict) or a list of payloads (List of Dict)

        Returns:
            int: amount of errors ocurred during the set command
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

    def wait_for_task(self, task_id: int, timeout: int = 60) -> List[Any]:
        """
        Wait for a task with a given id for its end and returns the message(s).

        Args:
            id (int): Task id to wait for

            timeout (int): Timeout in seconds

        Returns:
            List: Message list
        """
        log.debug("waiting for task id %s", task_id)
        messages: List[Any] = []
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
