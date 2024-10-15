"""
The FortiGate commands
"""

# pylint: disable=anomalous-backslash-in-string
import logging

import typer

from fotoobo.helpers import cli_path

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fgt get cmdb get firewall service subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)


@app.command()
def custom(
    name: str = typer.Argument(
        "",
        help="The firewall address object to get \[default: <all>]",
        show_default=False,
        metavar="[name]",
    ),
    output_file: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (format is specified by extension)",
        metavar="[file]",
        show_default=False,
    ),
) -> None:
    """
    Get FortiGate cmdb firewall service custom.

    The FortiGate api endpoint is: /cmdb/firewall.service/custom
    """
    # TODO: Here to add the service custom cli code
    print("SERVICE CUSTOM")


@app.command()
def group(
    name: str = typer.Argument(
        "",
        help="The firewall address object to get \[default: <all>]",
        show_default=False,
        metavar="[name]",
    ),
    output_file: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (format is specified by extension)",
        metavar="[file]",
        show_default=False,
    ),
) -> None:
    """
    Get FortiGate cmdb firewall service group.

    The FortiGate api endpoint is: /cmdb/firewall.service/group
    """
    # TODO: Here to add the service group cli code
    print("SERVICE GROUP")
