"""
The FortiGate get commands
"""
import logging

import typer

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
