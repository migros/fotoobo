"""
The FortiGate configuration class represents the whole or parts of a FortiGate configuration
"""
import logging
from typing import IO, Any, Dict, List, Optional

from fotoobo.exceptions import GeneralWarning
from fotoobo.helpers.files import load_json_file, save_json_file

from .fortigate_info import FortiGateInfo

log = logging.getLogger("fotoobo")


class FortiGateConfig:
    """
    The FortiGateConfig class represents a FortiGate configuration (or parts of it)
    """

    _config_path: List[str] = []

    def __init__(
        self,
        global_config: Optional[Dict[str, Any]] = None,
        vdom_config: Optional[Dict[str, Any]] = None,
        info: Optional[Dict[str, str]] = None,
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
            scope (str) : the configuration part to get the configuration from (global|vdom)
            path (str)  : from where should the configuration come?
            Examples:
            /                           : the whole configuration (default)
            /system/global/...          : subpath in global configuration
            /system/global/admin-scp    : exact configuration option
            /root/firewall/address/...  : subpath in root vdom

        Returns:
            any: FortiGateConfig configuration value or snippet from the given path.
            If the path or value does not exist None is returned.
        """
        log.debug("getting configuration from scope: '%s'", scope)
        log.debug("getting configuration from path: '%s'", path)
        # split the path by / and remove all empty parts
        path_list: List[str] = [p for p in path.strip("/").split("/") if p]
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

    def get_vdoms(self) -> List[str]:
        """
        Get the list of configured VDOMs.
        If it is a standalone configuration an empty list will be returned.

        Returns:
            List: List of VDOMs
        """
        vdoms: List[str] = []
        if self.info.vdom == "1":
            vdoms = list(self.vdom_config.keys())
        return vdoms

    def save_configuration_file(self, filename: str) -> None:
        """
        Save the configuration to a json configuration file.

        Args:
            filename (str): The json file to load the FortiGate configuration from
        """
        save_json_file(
            filename,
            {"global": self.global_config, "vdom": self.vdom_config, "info": self.info.__dict__},
        )

    @staticmethod
    def parse_configuration_file(filename: str) -> "FortiGateConfig":
        """
        Parse the FortiGate configuration from a file into a python object

        Args:
            filename (str): the filename of the FortiGate configuration file

        Returns:
            FortiGateConfig: the parsed FortiGate configuration object
        """
        log.debug("start configuration parser with file '%s'", filename)
        FortiGateConfig._config_path = []
        with open(filename, "r", encoding="UTF-8") as forti_file:
            parsed_config = FortiGateConfig._parse_to_dict(forti_file)

        global_config: Dict[str, Any] = {}
        vdom_config: Dict[str, Any] = {}
        if not "info" in parsed_config:
            raise GeneralWarning(f"There is no info in {filename}")
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
    def load_configuration_file(filename: str) -> "FortiGateConfig":
        """
        Create a FortiGateConfig object from a json configuration file.

        Args:
            filename (str): The json file to load the FortiGate configuration from

        Returns:
            FortiGateConfig: FortiGate configuration object
        """
        data = load_json_file(filename)
        return FortiGateConfig(data["global"], data["vdom"], data["info"])  # type: ignore

    @staticmethod
    def _config_convert_dict_to_list(config: Dict[str, Any]) -> List[Any]:
        """
        Convert a FortiGate configuration list like part to a configuration list.

        Args:
            config (dict): a FortiGate configuration list like part from a dict

        Returns:
            list: configuration list as list
        """
        conflist: List[str] = []

        for key, value in config.items():
            newconf = value
            newconf["id"] = int(key)
            conflist.append(newconf)

        return conflist

    @staticmethod
    def _config_is_list(config: Dict[str, Any]) -> bool:
        """
        Check if a FortiGate configuration part contains a list of elements.

        Args:
            config (dict): the FortiGate configuration part to check

        Returns:
            bool: is it a list (True) or not (False)
        """
        is_list = True
        if len(config) == 0:
            is_list = False

        for key in config.keys():
            if not key.isnumeric():
                is_list = False

        return is_list

    @staticmethod
    def _get_nested_dict(configs: List[str], newdata: Any) -> Dict[str, Any]:
        """
        Create a nested configuration dict from a list of strings and add newdata to the last key.

        Args:
            configs (list): configuration leafs to process
            newdata (any): data to add to the last key

        Returns:
            dict: the nested configuration
        """
        newdict = {}
        key = configs.pop(0)
        if len(configs) > 0:
            newdict[key] = FortiGateConfig._get_nested_dict(configs, newdata)

        else:
            newdict[key] = newdata

        return dict(newdict)

    @staticmethod
    def _parse_config_comment(info: Dict[str, Any], line: str) -> Dict[str, str]:
        """
        Parses a comment line in a FortiGate configuration and extracts interesting values.
        The values are then written to an info dict as meta-information.

        Args:
            info (dict): the meta information dict to add information to
            line (str): the FortiGate configuration comment line to parse

        Returns:
            dict: the updated meta information dict
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
        # should be Union[Dict[str, Any], List[Any]]
        """
        Fabric function to create a FortiGateConfig object from a backup configuration file
        This recursive method parses a FortiGate configuration from a file line by line

        Args:
            config_file (IO[str]): FortiGate configuration file object

        Returns:
            dict: A dict which contains the parsed FortiGate configuration
        """
        config: Any = {}
        info: Dict[str, str] = {}
        multiline: str = ""

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
                multiline_key: str = ""
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
                    tempconfig = FortiGateConfig._get_nested_dict(
                        config_path[1:], FortiGateConfig._parse_to_dict(config_file)
                    )

                    if config_path[0] not in config:
                        config[config_path[0]] = {}
                    config[config_path[0]] = {**config[config_path[0]], **tempconfig}

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
