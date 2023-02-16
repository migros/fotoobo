"""
FortiGate confcheck utility
"""

import logging
import os
from typing import List

import typer

from fotoobo.exceptions import GeneralError, GeneralWarning
from fotoobo.fortinet.fortigate_config import FortiGateConfig
from fotoobo.fortinet.fortigate_config_check import FortiGateConfigCheck
from fotoobo.helpers.files import load_yaml_file
from fotoobo.helpers.output import Output

app = typer.Typer()
log = logging.getLogger("fotoobo")


def fgt_confcheck(config: str, bundles: str) -> None:
    """
    The confcheck

    Args:
        config:  The configuration to check (either a file or directory)
                 in case it's a directory all .conf files in it will be checked.
        bundles: The check bundle to check the configuration against

    Raises:
        GeneralWarning: GeneralWarning
        GeneralError: GeneralError
    """
    files: List[str] = []
    if os.path.isfile(config):
        files.append(config)
    elif os.path.isdir(config):
        log.debug("Given config is a directory")
        files = [
            os.path.join(config, file) for file in os.listdir(config) if file.endswith(".conf")
        ]
    else:
        log.error("no valid configuration file")
    if not files:
        log.warning("there are not configuration files to check")
        raise GeneralWarning("there are not configuration files to check")
    if os.path.isfile(bundles):
        checks = load_yaml_file(bundles)
    else:
        log.error("no valid bundle file")
        raise GeneralError("no valid bundle file")
    total_results: int = 0
    output = Output()
    for file in files:
        try:
            conf_check = FortiGateConfigCheck(
                FortiGateConfig.parse_configuration_file(file), checks
            )
        except GeneralWarning as warn:
            log.warning(warn.message)
            continue

        conf_check.execute_checks()
        for result in conf_check.results:
            log.info(result)
        log.info(
            "all checks in '%s' done with '%s' messages",
            os.path.basename(file),
            len(conf_check.results),
        )
        total_results += len(conf_check.results)
        output.add(conf_check.results)

    log.info("all checks done with '%s' messages", total_results)
    if total_results == 0:
        output.add("There were no errors in the configuration file(s)")

    output.print_raw()
