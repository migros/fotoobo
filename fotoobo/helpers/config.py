"""
The config helper is used to load and set basic configuration for fotoobo. Some configuration
options may be set by the global configuration file which by default points to fotoobo.yaml in the
local directory. Some configuration options may be set by command line parameters regarding to the
cli help system.
If there are configuration options available in the global configuration file and also as a command
line option, the command line option takes precedence over the global configuration file option.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Union

from fotoobo.helpers.files import load_yaml_file


@dataclass(eq=False, order=False)
class Config:  # pylint: disable=too-many-instance-attributes
    """
    This is the configuration dataclass for the global configuration options.
    First all the configuration options must be initialized.
    If an option is not defined here it is not guaranteed that it may be used later in the code.
    """

    # set default values
    backup_dir: str = ""
    inventory_file: str = "inventory.yaml"
    logging: Union[Dict[str, Any], None] = None
    audit_logging: Union[Dict[str, Any], None] = None
    log_file: str = ""
    log_level: str = "INFO"
    no_logo: bool = False
    snmp_community: str = ""
    cli_info: Dict[str, Any] = field(default_factory=dict)

    def load_configuration(self, config_file: str) -> None:
        """
        Load the global fotoobo configuration file. If the configuration file is not present it just
        will be ignored and all the options remain as they are.
        If a file is present it looks for configuration options to set. Keep in mind that it is not
        mandatory to define every option in the configuration file. For that case make sure that an
        option not present in the configuration file is set with it's default.

        Args:
            config_file (str): fotoobo configuration file to load configuration from
        """
        if loaded_config := load_yaml_file(config_file):
            # We need a dict here
            loaded_config = dict(loaded_config)

            # then set the config options from file if set in file
            self.backup_dir = loaded_config.get("backup_dir", self.backup_dir)
            self.inventory_file = loaded_config.get("inventory", self.inventory_file)

            if loaded_config.get("logging"):
                self.logging = loaded_config["logging"]

            if loaded_config.get("audit_logging"):
                self.audit_logging = loaded_config["audit_logging"]

            self.no_logo = loaded_config.get("no_logo", self.no_logo)
            self.snmp_community = loaded_config.get("snmp_community", self.snmp_community)


config = Config()
