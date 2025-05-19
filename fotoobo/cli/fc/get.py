"""
The FortiCloud get commands
"""

import logging
from pathlib import Path
from typing import Any, Union

import typer

from fotoobo.exceptions.exceptions import GeneralError
from fotoobo.helpers import cli_path
from fotoobo.helpers.files import save_json_file
from fotoobo.helpers.result import Result
from fotoobo.tools import fc

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


HELP_TEXT_OPTION_OUTPUT_FILE = "The file to write the output to."


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fc get subcommand callback

    Args:
        context: The context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("About to execute command: '%s'", context.invoked_subcommand)


@app.command()
def products(
    output_file: Union[None, Path] = typer.Option(
        None,
        "--output",
        "-o",
        help=HELP_TEXT_OPTION_OUTPUT_FILE,
        metavar="[output]",
    ),
    raw: bool = typer.Option(False, "-r", "--raw", help="Output raw data."),
) -> None:
    """
    Get the FortiCloud products from asset management.
    """
    result = fc.get.products("forticloud")
    messages = result.get_messages("forticloud")
    if messages:
        for message in messages:
            if message["level"] == "error":
                log.error(message["message"])

            else:
                log.info(message["message"])

        raise GeneralError("Error getting FortiCloud products")

    if output_file:
        log.debug("output_file is: '%s'", output_file)
        save_json_file(output_file, result.get_result("forticloud"))

    else:
        if raw:
            result.print_raw()

        else:
            data = Result[Any]()
            for asset in result.get_result("forticloud"):
                asset.pop("entitlements")
                asset.pop("contracts")
                asset.pop("productModelEoR")
                asset.pop("productModelEoS")
                asset.pop("accountId")
                asset.pop("folderId")
                asset.pop("assetGroups")
                data.push_result(asset["serialNumber"], asset)

            data.print_result_as_table(title="FortiCloud API products", auto_header=True)


@app.command()
def version() -> None:
    """
    Get the FortiCloud API version.
    """
    result = fc.get.version("forticloud")
    result.print_result_as_table(
        title="FortiCloud API Version",
        headers=["FortiCloud", "Version"],
    )
