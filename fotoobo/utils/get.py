"""
The fotoobo get utility
"""
import importlib.metadata
import logging

from rich import print as rprint
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from fotoobo import __version__
from fotoobo.helpers.cli import walk_cli_info
from fotoobo.helpers.config import config
from fotoobo.helpers.output import print_datatable
from fotoobo.inventory import Inventory

log = logging.getLogger("fotoobo")


def commands() -> None:
    """Get the fotoobo cli commands

    Walk through the typer cli app and return its commands as a beautiful rich tree. The commands
    are sorted in alphabetical order
    """
    # from fotoobo.cli.main import app

    # tree = walk_cli_tree(app, Tree(Text().append("fotoobo", style="bold cyan")))
    # rprint(Panel(tree, border_style="#FF33BB", title="cli commands", title_align="right"))
    # rprint(config.cli_info)
    tree = walk_cli_info(
        config.cli_info["command"],
        Tree(Text().append(config.cli_info["info_name"], style="bold cyan")),
    )
    rprint(Panel(tree, border_style="#FF33BB", title="cli commands structure", title_align="right"))


def inventory() -> None:
    """Get the fotoobo inventory"""
    log.debug("printing fotoobo inventory information")
    inv = Inventory(config.inventory_file)
    data_table = []
    for host, data in inv.assets.items():
        data_table.append({"host": host, "hostname": data.hostname, "type": data.type})
    print_datatable(data_table, title="fotoobo inventory", headers=["Device", "Hostname", "Type"])


def version(verbose: bool = False) -> None:
    """Get the fotoobo version"""
    log.debug("printing fotoobo version information: %s", __version__)
    versions = [{"module": "fotoobo", "version": __version__}]

    modules = ["easysnmp", "jinja2", "PyYAML", "requests", "rich", "typer"]
    if verbose:
        for module in modules:
            versions.append({"module": module, "version": importlib.metadata.version(module)})

    print_datatable(versions, title="fotoobo version")
