"""
The FortiManager get commands
"""
import logging
from pathlib import Path

import typer

from fotoobo.helpers import cli_path
from fotoobo.helpers.output import write_policy_to_html
from fotoobo.tools import fmg

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")

HELP_TEXT_HOST = "The FortiManager to access (must be defined in the inventory)."


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fmg get subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command()
def adoms(
    host: str = typer.Argument(
        "fmg",
        help=HELP_TEXT_HOST,
        metavar="[host]",
    )
) -> None:
    """
    Get the FortiManager ADOM list.
    """
    result = fmg.get.adoms(host)
    result.print_result_as_table(title="FortiManager ADOMs", headers=["Name", "Version"])


@app.command()
def devices(
    host: str = typer.Argument(
        "fmg",
        help=HELP_TEXT_HOST,
        metavar="[host]",
    )
) -> None:
    """
    Get the FortiManager logical devices list.

    Be aware that if a device is a cluster only the cluster
    device is returned, not all its physical nodes.
    """
    result = fmg.get.devices(host)
    result.print_result_as_table(
        title="Fortinet devices",
        headers=["Device Name", "Version", "HA", "Platform", "Description"],
    )


@app.command(no_args_is_help=True)
def policy(
    adom: str = typer.Argument(
        ...,
        help="The FortiManager ADOM to get the firewall policy from.",
        metavar="[adom]",
        show_default=False,
    ),
    policy_name: str = typer.Argument(
        ..., help="The name of the policy to get.", metavar="[policy]", show_default=False
    ),
    filename: Path = typer.Argument(
        ..., help="The filename to write the policy to.", metavar="[file]", show_default=False
    ),
    host: str = typer.Argument(
        "fmg",
        help=HELP_TEXT_HOST,
        metavar="[host]",
    ),
) -> None:
    """
    Get a FortiManager policy.
    """
    result = fmg.get.policy(host, adom, policy_name)
    write_policy_to_html(result.get_result(host), filename)


@app.command()
def version(host: str = typer.Argument("fmg", help=HELP_TEXT_HOST, metavar="[host]")) -> None:
    """
    Get the FortiManager version.
    """
    result = fmg.get.version(host)
    result.print_result_as_table(title="FortiManager Version", headers=["FortiManager", "Version"])
