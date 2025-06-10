"""
The FortiGate configuration class represents the whole or parts of a FortiGate configuration
"""

import logging
from pathlib import Path
from typing import IO, Any, Optional

from fotoobo.exceptions import GeneralWarning
from fotoobo.helpers.files import load_json_file, save_json_file

from .fortigate_info import FortiGateInfo

log = logging.getLogger("fotoobo")


class FortiGateConfig:
    """
    The FortiGateConfig class represents a FortiGate configuration (or parts of it)
    """

    _config_path: list[str] = []

    def __init__(
        self,
        global_config: Optional[dict[str, Any]] = None,
        vdom_config: Optional[dict[str, Any]] = None,
        info: Optional[dict[str, str]] = None,
    ) -> None:
        self.global_config = global_config or {}
        self.vdom_config = vdom_config or {}
        self.info = FortiGateInfo(**(info or {}))
        try:
            self.info.hostname = self.global_config["system"]["global"]["hostname"]

        except KeyError:
            self.info.hostname = "HOSTNAME UNKNOWN"

    def get_configuration(self, scope: str = "global", path: str = "/") -> Any:
        """
        Return a config snippet from the given configuration path.

        Args:
            scope: The configuration part to get the configuration from (global|vdom)
            path:  From where should the configuration come?
            Examples:
            /                           : The whole configuration (default)
            /system/global/...          : Sub-path in global configuration
            /system/global/admin-scp    : Exact configuration option
            /root/firewall/address/...  : Sub-path in root vdom

        Returns:
            FortiGateConfig configuration value or snippet from the given path.
            If the path or value does not exist None is returned.
        """
        log.debug("Getting configuration from scope: '%s'", scope)
        log.debug("Getting configuration from path: '%s'", path)
        # split the path by / and remove all empty parts
        path_list: list[str] = [p for p in path.strip("/").split("/") if p]
        config: Any = {}

        if scope == "global":
            config = self.global_config

        elif scope == "vdom":
            config = self.vdom_config

        if len(path_list) > 0:
            for key in path_list:
                if key in config:
                    config = config[key]

                else:
                    config = {}
                    break

        return config

    def get_vdoms(self) -> list[str]:
        """
        Get the list of configured VDOMs.
        If it is a single vdom configuration an empty list will be returned.

        Returns:
            List of VDOMs
        """
        vdoms: list[str] = []
        if self.info.vdom == "1":
            vdoms = list(self.vdom_config.keys())

        return vdoms

    def save_configuration_file(self, configuration_file: Path) -> None:
        """
        Save the configuration to a json configuration file.

        Args:
            configuration_file: The json file to load the FortiGate configuration from
        """
        save_json_file(
            configuration_file,
            {"global": self.global_config, "vdom": self.vdom_config, "info": self.info.__dict__},
        )

    @staticmethod
    def parse_configuration_file(configuration_file: Path) -> "FortiGateConfig":
        """
        Parse the FortiGate configuration from a file into a python object

        Args:
            configuration_file: The filename of the FortiGate configuration file

        Returns:
            The parsed FortiGate configuration object
        """
        log.debug("Start configuration parser with file '%s'", configuration_file)

        FortiGateConfig._config_path = []
        with configuration_file.open(encoding="UTF-8") as forti_file:
            parsed_config = FortiGateConfig._parse_to_dict(forti_file)

        global_config: dict[str, Any] = {}
        vdom_config: dict[str, Any] = {}

        if "info" not in parsed_config:
            raise GeneralWarning(f"There is no info in {configuration_file}")

        info = parsed_config["info"]
        parsed_config.pop("info")

        if info["vdom"] == "0":
            global_config["system"] = {}
            global_config["system"] = parsed_config["system"]
            parsed_config.pop("system")
            vdom_config["root"] = {}
            vdom_config["root"] = parsed_config

        else:
            global_config = parsed_config["global"]
            vdom_config = parsed_config["vdom"]

        return FortiGateConfig(global_config, vdom_config, info)

    @staticmethod
    def load_configuration_file(configuration_file: Path) -> "FortiGateConfig":
        """
        Create a FortiGateConfig object from a json configuration file.

        Args:
            configuration_file: The json file to load the FortiGate configuration from

        Returns:
            FortiGate configuration object
        """
        data = load_json_file(configuration_file)
        return FortiGateConfig(data["global"], data["vdom"], data["info"])  # type: ignore

    @staticmethod
    def _config_convert_dict_to_list(config: dict[str, Any]) -> list[Any]:
        """
        Convert a FortiGate configuration list like part to a configuration list.

        Args:
            config: A FortiGate configuration list like part from a dict

        Returns:
            Configuration list as list
        """
        configs: list[str] = []
        for key, value in config.items():
            new_config = value
            new_config["id"] = int(key)
            configs.append(new_config)

        return configs

    @staticmethod
    def _config_is_list(config: dict[str, Any]) -> bool:
        """
        Check if a FortiGate configuration part contains a list of elements.

        Args:
            config: The FortiGate configuration part to check

        Returns:
            Is it a list (True) or not (False)
        """
        is_list = True
        if len(config) == 0:
            is_list = False

        for key in config.keys():
            if not key.isnumeric():
                is_list = False

        return is_list

    @staticmethod
    def _get_nested_dict(configs: list[str], new_data: Any) -> dict[str, Any]:
        """
        Create a nested configuration dict from a list of strings and add new data to the last key.

        Args:
            configs:  Configuration leafs to process
            new_data: Data to add to the last key

        Returns:
            The nested configuration
        """
        out_dict = {}
        key = configs.pop(0)
        if len(configs) > 0:
            out_dict[key] = FortiGateConfig._get_nested_dict(configs, new_data)

        else:
            out_dict[key] = new_data

        return dict(out_dict)

    @staticmethod
    def _parse_config_comment(info: dict[str, Any], line: str) -> dict[str, str]:
        """
        Parses a comment line in a FortiGate configuration and extracts interesting values.
        The values are then written to an info dict as meta-information.

        Args:
            info: The meta information dict to add information to
            line: The FortiGate configuration comment line to parse

        Returns:
            The updated meta information dict
        """
        line = line.lstrip("#").strip()
        if line.startswith("config-version"):
            value = line.split("=", maxsplit=1)[1]
            info["model"], info["os_version"], info["type"] = value.split("-")[0:3]
            for part in line.split(":")[1:]:
                info[part.split("=")[0]] = part.split("=")[1]

        elif line.count("=") == 1:
            info[line.split("=")[0]] = line.split("=")[1]

        return info

    @staticmethod
    # pylint: disable=too-many-branches
    def _parse_to_dict(config_file: IO[str]) -> Any:
        # should be Union[dict[str, Any], list[Any]]
        """
        Fabric function to create a FortiGateConfig object from a backup configuration file
        This recursive method parses a FortiGate configuration from a file line by line

        Args:
            config_file: FortiGate configuration file object

        Returns:
            A dict which contains the parsed FortiGate configuration
        """
        config: Any = {}
        info: dict[str, str] = {}
        multiline: str = ""
        multiline_key: str = ""

        for line in config_file:
            line = line.strip()

            # handle empty lines
            if not line:
                continue

            # handle comment lines
            if line.startswith("#"):
                info = FortiGateConfig._parse_config_comment(info, line)

            # handle multiline strings (do that before all the other logic)
            if multiline:
                multiline += f"\n{line}"
                if line.endswith('"'):
                    config[multiline_key], multiline = multiline.strip('"'), ""

                continue

            # check if a multiline string starts. begin with "set" and uneven amount of quotes (")
            if line.startswith("set ") and line.count('"') % 2 == 1 and not line.endswith('"'):
                _, multiline_key, value = line.split(maxsplit=2)  # first part is always "set"
                multiline += value
                continue

            # handle configuration option
            if line.startswith("set "):
                _, key, value = line.split(maxsplit=2)  # first part ist always "set"
                config[key] = " ".join(value.replace('"', "").split())

            # handle recursion
            if line.startswith("config vdom") and len(FortiGateConfig._config_path) == 1:
                continue

            if line.startswith("config "):
                if len(line[7:].split(" ")) == 1:
                    FortiGateConfig._config_path.append(line[7:])
                    config[line[7:].strip('"')] = FortiGateConfig._parse_to_dict(config_file)

                else:
                    FortiGateConfig._config_path.append(line[7:])
                    config_path = [word.strip('"') for word in line[7:].split()]
                    temp_config = FortiGateConfig._get_nested_dict(
                        config_path[1:], FortiGateConfig._parse_to_dict(config_file)
                    )

                    if config_path[0] not in config:
                        config[config_path[0]] = {}

                    config[config_path[0]] = {**config[config_path[0]], **temp_config}

            if line.startswith("edit "):
                FortiGateConfig._config_path.append(line[5:])
                config[line[5:].strip('"')] = FortiGateConfig._parse_to_dict(config_file)

            # handle section ends
            if line == "end":
                FortiGateConfig._config_path.pop()
                if FortiGateConfig._config_is_list(config):
                    config = FortiGateConfig._config_convert_dict_to_list(config)

                return config

            if line == "next":
                FortiGateConfig._config_path.pop()
                return config

        # append info dict to config if it's set
        if len(info) > 0:
            config["info"] = info

        return config
