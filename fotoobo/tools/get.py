"""
The fotoobo get utility
"""
import importlib.metadata
import logging
from typing import Dict, List

from rich.text import Text
from rich.tree import Tree

from fotoobo import __version__
from fotoobo.helpers.cli import walk_cli_info
from fotoobo.helpers.config import config
from fotoobo.helpers.result import Result
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def inventory() -> Result[Dict[str, str]]:
    """
    Get the fotoobo inventory
    """
    log.debug("Printing fotoobo inventory information")

    result = Result[Dict[str, str]]()
    _inventory = Inventory(config.inventory_file)

    for host, data in _inventory.assets.items():
        result.push_result(host, {"hostname": data.hostname, "type": data.type})

    return result


def version(verbose: bool = False) -> Result[List[Dict[str, str]]]:
    """
    Get the fotoobo version

    Args:
        verbose:    Whether we want verbose output
    """
    log.debug("printing fotoobo version information: %s", __version__)

    result = Result[List[Dict[str, str]]]()
    versions = [{"module": "fotoobo", "version": __version__}]

    if verbose:
        modules = ["jinja2", "PyYAML", "requests", "rich", "typer"]

        for module in modules:
            versions.append({"module": module, "version": importlib.metadata.version(module)})

    result.push_result("version", versions)

    return result


def commands() -> Result[Tree]:
    """Get the fotoobo cli commands

    Walk through the typer cli app and return its commands as a beautiful rich tree. The commands
    are sorted in alphabetical order
    """
    result = Result[Tree]()

    result.push_result(
        "commands",
        walk_cli_info(
            config.cli_info["command"],
            Tree(Text().append(config.cli_info["info_name"], style="bold cyan")),
        ),
    )

    return result
