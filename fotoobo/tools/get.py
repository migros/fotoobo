"""
The fotoobo get utility
"""
import importlib.metadata
import logging

from rich.text import Text
from rich.tree import Tree

from fotoobo import __version__
from fotoobo.helpers.cli import walk_cli_info
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def inventory() -> Result:
    """
    Get the fotoobo inventory
    """
    log.debug("Printing fotoobo inventory information")

    result = Result()
    _inventory = Inventory(config.inventory_file)

    data_table = []

    for host, data in _inventory.assets.items():
        data_table.append({"host": host, "hostname": data.hostname, "type": data.type})

    result.push_result("inventory", data_table)

    return result


def version(verbose: bool = False) -> Result:
    """
    Get the fotoobo version

    Args:
        verbose:    Whether we want verbose output
    """
    log.debug("printing fotoobo version information: %s", __version__)

    result = Result()
    versions = [{"module": "fotoobo", "version": __version__}]

    if verbose:
        modules = ["pysnmp", "jinja2", "PyYAML", "requests", "rich", "typer"]

        for module in modules:
            versions.append({"module": module, "version": importlib.metadata.version(module)})

    result.push_result("version", versions)

    return result


def commands() -> Result:
    """Get the fotoobo cli commands

    Walk through the typer cli app and return its commands as a beautiful rich tree. The commands
    are sorted in alphabetical order
    """
    result = Result()

    result.push_result(
        "commands",
        walk_cli_info(
            config.cli_info["command"],
            Tree(Text().append(config.cli_info["info_name"], style="bold cyan")),
        ),
    )

    return result
