"""
The FortiGate get commands
"""
import logging

import typer

from fotoobo.helpers.output import print_datatable, print_dicttable
from fotoobo.utils import fgt

app = typer.Typer()
log = logging.getLogger("fotoobo")


@app.command()
def check(
    configuration: str = typer.Argument(
        ..., help="The FortiGate configuration file or directory", metavar="[config]"
    ),
    bundles: str = typer.Argument(
        ..., help="Filename of the file containing the check bundles", metavar="[bundles]"
    ),
) -> None:
    """
    Check one or more FortiGate configuration files
    """
    fgt.config.check(configuration, bundles)


@app.command()
def info(
    configuration: str = typer.Argument(
        ..., help="The FortiGate configuration file or directory", metavar="[config]"
    ),
    as_list: bool = typer.Option(
        False, "--list", "-l", help="print it as a list instead of separate blocks"
    ),
) -> None:
    """
    Get the information from one or more FortiGate configuration files
    """
    infos = fgt.config.info(configuration)
    info_dicts = [data.__dict__ for data in infos]

    if as_list:
        print_datatable(info_dicts, auto_header=True)

    else:
        for data in info_dicts:
            print_dicttable(data, title=data.get("hostname", "unknown"))
