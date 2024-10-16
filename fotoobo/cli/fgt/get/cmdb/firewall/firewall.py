"""
The FortiGate commands
"""

# pylint: disable=anomalous-backslash-in-string
import logging
from pathlib import Path

import typer

from fotoobo.exceptions import GeneralError
from fotoobo.helpers import cli_path
from fotoobo.tools.fgt.get import api

from .service import service

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


app.add_typer(service.app, name="service", help="FortiGate get cmdb firewall service commands.")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fgt get cmdb get firewall subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)


@app.command()
def address(  # pylint: disable=too-many-branches
    host: str = typer.Argument(
        "",
        help="The FortiGate hostname to access (must be defined in the inventory). "
        "\[default: <all>]",
        show_default=False,
        metavar="[host]",
    ),
    name: str = typer.Argument(
        "",
        help="The firewall address object to get \[default: <all>]",
        show_default=False,
        metavar="[name]",
    ),
    vdom: str = typer.Option(
        "*",
        "--vdom",
        help="The vdom to query ('vdom1' or 'vdom1,vdom2') \[default: <all>]",
        show_default=False,
        metavar="[vdom]",
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
    Get FortiGate cmdb firewall address.

    The FortiGate api endpoint is: /cmdb/firewall/address
    """
    if name and ("*" in vdom or "," in vdom):
        raise GeneralError("With name argument you have to specify one single VDOM (with --vdom)")

    result = api(host=host, vdom=vdom, url=f"/cmdb/firewall/address/{name}")

    if output_file:
        result.save_raw(file=Path(output_file), key=host)

    else:
        assets = []
        if result.get_result(host):
            for vd in result.get_result(host):
                for asset in vd["results"]:

                    data: dict[str, str] = {
                        "name": asset["name"],
                        "vdom": vd["vdom"],
                        "type": asset["type"],
                    }

                    if asset["type"] == "fqdn":
                        data["content"] = asset["fqdn"]

                    elif asset["type"] == "geography":
                        data["content"] = asset["country"]

                    elif asset["type"] == "ipmask":
                        data["content"] = "/".join(
                            [asset["subnet"].split(" ")[0], asset["subnet"].split(" ")[1]]
                        )

                    elif asset["type"] == "iprange":
                        data["content"] = " - ".join([asset["start-ip"], asset["end-ip"]])

                    else:
                        data["content"] = ""

                    assets.append(data)

        result.push_result(host, assets)

        if result.results[host]:
            result.print_table_raw(
                result.results[host], headers=["name", "vdom", "type", "content"], title=host
            )

        else:
            print("No data found")


@app.command()
def addrgrp(
    host: str = typer.Argument(
        "",
        help="The FortiGate hostname to access (must be defined in the inventory). "
        "\[default: <all>]",
        show_default=False,
        metavar="[host]",
    ),
    name: str = typer.Argument(
        "",
        help="The firewall address group object to get \[default: <all>]",
        show_default=False,
        metavar="[name]",
    ),
    vdom: str = typer.Option(
        "*",
        "--vdom",
        help="The vdom to query ('vdom1' or 'vdom1,vdom2') \[default: <all>]",
        show_default=False,
        metavar="[vdom]",
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
    Get FortiGate cmdb firewall address group.

    The FortiGate api endpoint is: /cmdb/firewall/addrgrp
    """
    if name and ("*" in vdom or "," in vdom):
        raise GeneralError("With name argument you have to specify one single VDOM (with --vdom)")

    result = api(host=host, vdom=vdom, url=f"/cmdb/firewall/addrgrp/{name}")

    if output_file:
        result.save_raw(file=Path(output_file), key=host)

    else:
        assets = []
        if result.get_result(host):
            for vd in result.get_result(host):
                for asset in vd["results"]:
                    # print(asset)
                    data: dict[str, str] = {
                        "name": asset["name"],
                        "vdom": vd["vdom"],
                        "content": "\n".join(_["name"] for _ in asset["member"]),
                    }

                    assets.append(data)

        result.push_result(host, assets)

        if result.results[host]:
            result.print_table_raw(
                result.results[host], headers=["name", "vdom", "content"], title=host
            )

        else:
            print("No data found")
