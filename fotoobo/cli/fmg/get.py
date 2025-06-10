"""
The FortiManager get commands
"""

import logging
from pathlib import Path
from typing import Union

import typer
from typing_extensions import Annotated

from fotoobo.helpers import cli_path
from fotoobo.helpers.output import write_policy_to_html
from fotoobo.helpers.result import Result
from fotoobo.tools import fmg

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")

HELP_TEXT_HOST = "The FortiManager to access (must be defined in the inventory)."


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fmg get subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)


@app.command()
def adoms(
    host: Annotated[
        str,
        typer.Argument(
            help=HELP_TEXT_HOST,
            metavar="[host]",
        ),
    ] = "fmg",
) -> None:
    """
    Get the FortiManager ADOM list.
    """
    result = fmg.get.adoms(host)
    result.print_result_as_table(title="FortiManager ADOMs", headers=["Name", "Version"])


@app.command()
def devices(
    host: Annotated[
        str,
        typer.Argument(
            help=HELP_TEXT_HOST,
            metavar="[host]",
        ),
    ] = "fmg",
    raw: Annotated[bool, typer.Option("-r", "--raw", help="Output raw data.")] = False,
) -> None:
    """
    Get the FortiManager devices list.

    In case of a cluster the 'Device Name' is the name of the cluster and the 'HA Nodes' holds the
    hostnames of the actual cluster nodes.
    """
    result = fmg.get.devices(host)
    if raw:
        result.print_raw()

    else:
        # Make a string from the list of ha nodes
        new_result = Result[dict[str, Union[str, list[str]]]]()
        for key, value in result.all_results().items():
            value["ha_nodes"] = ", ".join(value["ha_nodes"])
            new_result.push_result(key, value)

        new_result.print_result_as_table(
            title="Fortinet devices",
            headers=["Device Name", "Version", "HA", "Platform", "Description", "HA nodes"],
        )


@app.command(no_args_is_help=True)
def policy(
    adom: Annotated[
        str,
        typer.Argument(
            help="The FortiManager ADOM to get the firewall policy from.",
            metavar="[adom]",
            show_default=False,
        ),
    ],
    policy_name: Annotated[
        str,
        typer.Argument(
            help="The name of the policy to get.", metavar="[policy]", show_default=False
        ),
    ],
    filename: Annotated[
        Path,
        typer.Argument(
            help="The filename to write the policy to.", metavar="[file]", show_default=False
        ),
    ],
    host: Annotated[str, typer.Argument(help=HELP_TEXT_HOST, metavar="[host]")] = "fmg",
) -> None:
    """
    Get a FortiManager policy.
    """
    result = fmg.get.policy(host, adom, policy_name)
    write_policy_to_html(result.get_result(host), filename)


@app.command()
def version(
    host: Annotated[str, typer.Argument(help=HELP_TEXT_HOST, metavar="[host]")] = "fmg",
) -> None:
    """
    Get the FortiManager version.
    """
    result = fmg.get.version(host)
    result.print_result_as_table(title="FortiManager Version", headers=["FortiManager", "Version"])
