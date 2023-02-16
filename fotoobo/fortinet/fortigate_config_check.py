"""
FortiGate configuration checker
"""
import logging
from typing import Any, Dict, List

from fotoobo.exceptions import GeneralError
from fotoobo.fortinet.fortigate_config import FortiGateConfig

log = logging.getLogger("fotoobo")


class FortiGateConfigCheck:
    """The FortiGate configuration check class"""

    def __init__(self, config: FortiGateConfig, checks: Any) -> None:
        """
        Initialize the configuration checker.

        Args:
            config (FortiGateConfig): the FortiGate configuration
            checks (dict): the checks to do against the FortiGate configuration
        """
        self.allowed_checks: List[str] = ["count", "exist", "value", "value_in_list"]
        self.config = config
        self.checks = checks
        self.results: List[str] = []

    def add_message(self, chk: Dict[str, Any], msg: str) -> None:
        """
        Generates a styled message and appends it to the results.

        Args:
            chk (Dict[str, any]): the check which generated the message
            msg (str): the message to sent to the messages list
        """
        check_name = f" (check_name: [var]{chk['name']}[/])" if "name" in chk else ""
        message = f"[chk]{chk['type']}[/]: {msg}{check_name}"
        self.results.append(message)

    def execute_checks(self) -> None:  # pylint: disable=too-many-branches
        """
        Execute the FortiGate configuration checks.

        After initializing a FortiGateConfigCheck object you can run this method to actually run
        the checks and write the results into the results object.
        """
        if not self.checks:
            log.error("there are no checks defined")
            raise GeneralError("there are no checks defined")

        for check in self.checks:

            # applying info filter
            skip = False
            for info_filter in check.get("filter-info", []):
                if str(check["filter-info"]).startswith("<"):
                    if not getattr(self.config.info, info_filter) < str(
                        check["filter-info"][info_filter][1:]
                    ):
                        log.debug("skipping check due to filter-info '%s'", info_filter)
                        skip = True
                elif str(check["filter-info"]).startswith(">"):
                    if not getattr(self.config.info, info_filter) > str(
                        check["filter-info"][info_filter][1:]
                    ):
                        log.debug("skipping check due to filter-info '%s'", info_filter)
                        skip = True
                else:
                    if not getattr(self.config.info, info_filter) == str(
                        check["filter-info"][info_filter]
                    ):
                        log.debug("skipping check due to filter-info '%s'", info_filter)
                        skip = True

            # applying config_filter
            for conf_filter in check.get("filter-config", []):
                config = self.config.get_configuration(check["scope"], conf_filter)
                if not config == check["filter-config"][conf_filter]:
                    log.debug("skipping check due to filter-config '%s'", conf_filter)
                    skip = True

            if skip:
                continue

            # check if needed check keys are present
            if miss := ("type", "scope", "path", "checks") - check.keys():
                log.error("key(s) %s missing in %s", miss, check.get("name", "unnamed check"))
                continue

            # check if checks are defined
            if not check["checks"]:
                log.error("no checks defined in %s", check.get("name", "unnamed check"))
                continue

            if not check["type"] in self.allowed_checks:
                log.error(
                    "check type %s not available in %s",
                    check.get("type"),
                    check.get("name", "unnamed check"),
                )
                continue

            if check["scope"] == "global":
                config = self.config.get_configuration(check["scope"], check["path"])
                getattr(self, "_check_" + check["type"])(config, check)

            if check["scope"] == "vdom":
                if self.config.info.vdom == "0":
                    if check["path"].startswith("/system/"):
                        config = self.config.get_configuration("global", check["path"])

                    else:
                        config = self.config.get_configuration("vdom", "/root" + check["path"])
                    getattr(self, "_check_" + check["type"])(config, check)

                elif self.config.info.vdom == "1":
                    for vdom in self.config.get_vdoms():
                        config = self.config.get_configuration(
                            check["scope"], vdom + "/" + check["path"]
                        )
                        getattr(self, "_check_" + check["type"])(config, check)

        self.results = [f"[hst]{self.config.info.hostname}[/]: {result}" for result in self.results]

    def _check_count(self, config: Any, chk: Dict[str, Any]) -> None:
        """
        Check the configuration list count.

        Args:
            config: FortiGate configuration part to check
            chk (dict): the check dict to process
        """
        if isinstance(config, list):
            conf_len = len(config)
            for key, value in chk["checks"].items():
                # pylint: disable=too-many-boolean-expressions
                if (
                    (key == "eq" and not conf_len == int(value))
                    or (key == "gt" and not conf_len > int(value))
                    or (key == "lt" and not conf_len < int(value))
                ):
                    self.add_message(
                        chk,
                        f"count of [var]{chk['path']}[/] is not [var]{key}[/] [var]{value}[/]",
                    )

        else:
            log.warning("%s is not a configuration list", chk["path"])

    def _check_exist(self, config: Any, chk: Dict[str, Any]) -> None:
        """
        Check if a configuration option is present (or not) regardless of it's value.

        Args:
            config: FortiGate configuration part to check
            chk (dict): the check dict to process
        """
        for key, value in chk["checks"].items():
            if bool(key in config) != value:
                self.add_message(
                    chk,
                    f"key [var]{key}[/] in [var]{chk['path']}[/] is not [var]{value}[/]",
                )

    def _check_value(self, config: Any, chk: Dict[str, Any]) -> None:
        """
        Do the checks for a configuration value. It checks if the configuration option is present
        and if the value is set as given in the check bundle.

        Args:
            config: FortiGate configuration part to check
            chk (dict): the check dict to process
        """
        for key, value in chk["checks"].items():
            msg_key = f"[var]{key}[/]"
            msg_path = f"[var]{chk['path']}[/]"
            if key in config:
                log.debug("key '%s' in '%s' is '%s'", msg_key, msg_path, config[key])
                if str(value) != config[key]:
                    self.add_message(
                        chk,
                        f"key {msg_key} in {msg_path} is not [var]{value}[/]",
                    )

            else:
                if not chk.get("ignore_missing", False):
                    self.add_message(chk, f"key {msg_key} does not exist in config")

    def _check_value_in_list(self, config: Any, chk: Dict[str, Any]) -> None:
        """
        Do the checks for set configuration. It checks if the configuration option is present in a
        and configuration list and if the value is set as given in the check bundle.

        Args:
            config: FortiGate configuration part to check
            chk (dict): the check dict to process
        """
        inverse: bool = chk.get("inverse", False)
        msg_not = "" if inverse else "not "
        for key, val in chk["checks"].items():
            msg_key = f"[var]{key}[/]"
            msg_val = f"[var]{val}[/]"
            msg_path = f"[var]{chk['path']}[/]"
            exist = False
            for conf in config:
                if key in conf and val == conf[key]:
                    exist = True

            if not exist ^ inverse:
                self.add_message(
                    chk,
                    f"{msg_key}: {msg_val} {msg_not}in {msg_path}",
                )
