"""
FortiGate configuration check utility
"""

import logging
from pathlib import Path
from typing import List

import typer

from fotoobo.exceptions import GeneralError, GeneralWarning
from fotoobo.fortinet.fortigate_config import FortiGateConfig
from fotoobo.fortinet.fortigate_config_check import FortiGateConfigCheck
from fotoobo.fortinet.fortigate_info import FortiGateInfo
from fotoobo.helpers.files import load_yaml_file
from fotoobo.helpers.output import Output

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


def check(config: Path, bundles: Path) -> None:
    """
    The FortiGate configuration check

    Args:
        config:  The configuration to check (either a file or directory)
                 in case it's a directory all .conf files in it will be checked.
        bundles: The check bundle to check the configuration against

    Raises:
        GeneralWarning: GeneralWarning
        GeneralError: GeneralError
    """
    files: List[Path] = []
    config = Path(config)
    if config.is_file():
        files.append(config)

    elif config.is_dir():
        log.debug("Given config is a directory")
        files = [file for file in config.iterdir() if file.suffix == ".conf"]

    else:
        log.error("no valid configuration file")

    if not files:
        log.warning("there are no configuration files to check")
        raise GeneralWarning("there are no configuration files to check")

    bundles = Path(bundles)
    if bundles.is_file():
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
            file.name,
            len(conf_check.results),
        )
        total_results += len(conf_check.results)
        output.add(conf_check.results)

    log.info("all checks done with '%s' messages", total_results)
    if total_results == 0:
        output.add("There were no errors in the configuration file(s)")

    output.print_raw()


def info(config: Path) -> List[FortiGateInfo]:
    """
    The FortiGate configuration information utility.

    Args:
        config (Path):  The configuration to get the information from (either a file or directory)
                 in case it's a directory all .conf files in it will be checked.

    Returns:
        list: list of FortiGate configuration information

    Raises:
        GeneralWarning: GeneralWarning
    """
    files: List[Path] = []
    if config.is_file():
        files.append(config)

    elif config.is_dir():
        log.debug("Given config is a directory")
        files = [file for file in config.iterdir() if file.is_file() and file.suffix == ".conf"]

    if not files:
        log.warning("there are no configuration files")
        raise GeneralWarning("there are no configuration files")

    output = []
    for file in files:
        conf = FortiGateConfig.parse_configuration_file(file)
        output.append(conf.info)

    return output
