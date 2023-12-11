"""
The config helper is used to load and set basic configuration for fotoobo. Some configuration
options may be set by the global configuration file which by default points to fotoobo.yaml in the
local directory. Some configuration options may be set by command line parameters as described in
the cli help system.
If there are configuration options available in the global configuration file and also as a command
line option, the command line option takes precedence over the global configuration file option.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Union

from fotoobo.exceptions import GeneralError
from fotoobo.helpers.files import load_yaml_file


@dataclass(eq=False, order=False)
class Config:
    """
    This is the configuration dataclass for the global configuration options.
    First all the configuration options must be initialized.
    If an option is not defined here it is not guaranteed that it may be used later in the code.
    """

    # set default values
    inventory_file: Path = Path("inventory.yaml")
    logging: Union[Dict[str, Any], None] = None
    audit_logging: Union[Dict[str, Any], None] = None
    no_logo: bool = False
    cli_info: Dict[str, Any] = field(default_factory=dict)
    vault: Dict[str, str] = field(default_factory=dict)

    def load_configuration(self, config_file: Union[Path, None]) -> None:
        """
        Load the global fotoobo configuration file. If the configuration file is not present it just
        will be ignored and all the options remain as they are.
        If a file is present it looks for configuration options to set. Keep in mind that it is not
        mandatory to define every option in the configuration file. For that case make sure that an
        option not present in the configuration file is set with its default.

        Args:
            config_file (Path): fotoobo configuration file to load configuration from
        """

        # If no explicit config file has been given, search at the predefined places
        if config_file is None:
            fotoobo_yaml_in_dot_config = Path("~").expanduser() / ".config" / "fotoobo.yaml"

            # First we check whether there is a project fotoobo.yaml in the
            # current working directory
            if Path("fotoobo.yaml").is_file():
                config_file = Path("fotoobo.yaml")

            # Second we check whether there is a user wide fotoobo.yaml in the .config folder
            elif fotoobo_yaml_in_dot_config.is_file():
                config_file = fotoobo_yaml_in_dot_config

            # If no config file can be found we rest with the defaults
            else:
                return

        if config_file:
            if loaded_config := load_yaml_file(config_file):
                # We need a dict here
                loaded_config = dict(loaded_config)

                # then set the config options from file if set in file
                self.inventory_file = Path(
                    loaded_config.get("inventory", self.inventory_file)
                ).expanduser()

                if not self.inventory_file.is_absolute():
                    self.inventory_file = config_file.parent / self.inventory_file

                self.logging = loaded_config.get("logging", {})
                self.audit_logging = loaded_config.get("audit_logging", {})
                self.no_logo = loaded_config.get("no_logo", self.no_logo)

                self.vault = loaded_config.get("vault", {})
                if self.vault:
                    # role_id and secret_id may be stored in environment variables (they overwrite
                    # the ones configured in the fotoobo.yaml)
                    if os.getenv("FOTOOBO_VAULT_ROLE_ID"):
                        self.vault["role_id"] = os.getenv("FOTOOBO_VAULT_ROLE_ID", "")

                    if os.getenv("FOTOOBO_VAULT_SECRET_ID"):
                        self.vault["secret_id"] = os.getenv("FOTOOBO_VAULT_SECRET_ID", "")

                    # Check if all the mandatory settings in vault section are given by substracting
                    # the list of keys in vault config from list of mandatory keys.
                    if (
                        missing := [
                            "url",
                            "namespace",
                            "data_path",
                            "role_id",
                            "secret_id",
                        ]
                        - self.vault.keys()
                    ):
                        raise GeneralError(f"Missing vault configuration data: {missing}")


config = Config()
