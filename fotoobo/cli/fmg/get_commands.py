"""
The FortiManager get commands
"""
import logging

import typer

from fotoobo.helpers import cli_path
from fotoobo.helpers.output import print_datatable, write_policy_to_html
from fotoobo.utils import fmg

app = typer.Typer()
log = logging.getLogger("fotoobo")


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
        help="The FortiManager hostname to access (must be defined in inventory)",
        metavar="[host]",
    )
) -> None:
    """
    Get the FortiManager ADOM list
    """
    data = fmg.get.adoms(host)
    print_datatable(data, title="FortiManager ADOMs", headers=["Name", "Version"])


@app.command()
def devices(
    host: str = typer.Argument(
        "fmg",
        help="The FortiManager hostname to access (must be defined in inventory)",
        metavar="[host]",
    )
) -> None:
    """
    Get the FortiManager logical devices list

    Be aware that if a device is a cluster only the cluster device is returned, not all its
    physical nodes.
    """
    data = fmg.get.devices(host)
    print_datatable(
        data,
        title="Fortinet devices",
        headers=["Device Name", "Version", "HA", "Platform", "Description"],
    )


@app.command()
def policy(
    host: str = typer.Argument(
        ...,
        help="The FortiManager hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
    adom: str = typer.Argument(
        ..., help="The FortiManager ADOM to get the firewall policy from", metavar="[adom]"
    ),
    policy_name: str = typer.Argument(
        ...,
        help="The policy name to get",
        metavar="[policy]",
    ),
    filename: str = typer.Argument(
        ...,
        help="the filename to write the policy to",
        metavar="[file]",
    ),
) -> None:
    """
    Get a FortiManager policy
    """
    data = fmg.get.policy(host, adom, policy_name)
    write_policy_to_html(data, filename)


@app.command()
def version(
    host: str = typer.Argument(
        "fmg",
        help="The FortiManager hostname to access (must be defined in inventory)",
        metavar="[host]",
    )
) -> None:
    """
    Get the FortiManager version
    """
    data = fmg.get.version(host)
    print_datatable(data, title="FortiManager Version", headers=["FortiManager", "Version"])
