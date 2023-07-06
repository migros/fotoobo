"""
The FortiGate check commands
"""
# pylint: disable=anomalous-backslash-in-string

import logging
from pathlib import Path
from typing import Dict, Union

import typer
from rich.pretty import pprint

from fotoobo.helpers import cli_path
from fotoobo.helpers.config import config
from fotoobo.helpers.files import save_json_file
from fotoobo.helpers.result import Result
from fotoobo.inventory.inventory import Inventory
from fotoobo.tools import fgt

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


HELP_TEXT_OPTION_OUTPUT_FILE = "The file to write the output to."
HELP_TEXT_OPTION_TEMPLATE = "The jinja2 template to use (use with -o)."
HELP_TEXT_TEMPLATE = (
    "If you add a template with the -t option you may render the output with any Jinja2 template "
    "file. You may use any of the given data returned from the FortiClient EMS. Additionally there "
    "are enriched variables under 'fotoobo' which you may also use in your template."
)


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fgt check subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command()
def hamaster(
    host: str = typer.Argument(
        "fmg",
        help="The FortiManager hostname to access (must be defined in the inventory).",
        metavar="[host]",
    ),
    output_file: Union[None, Path] = typer.Option(
        None,
        "--output",
        "-o",
        help=HELP_TEXT_OPTION_OUTPUT_FILE,
        metavar="[output]",
    ),
    raw: bool = typer.Option(False, "-r", "--raw", help="Output raw data."),
    smtp_server: str = typer.Option(
        None,
        "--smtp",
        help="The smtp configuration from the inventory.",
        metavar="[server]",
        show_default=False,
    ),
    template_file: Union[None, Path] = typer.Option(
        None,
        "--template",
        "-t",
        help=HELP_TEXT_OPTION_TEMPLATE,
        metavar="[template]",
    ),
) -> None:
    """
    Check the FortiGate HA master.

    Although this command checks the HA master status of FortiGates you have to specify a
    FortiManager to access. The command searches for all FortiGate clusters in the FortiManager
    and checks if the designated primary node really is the HA master node.

    The optional argument \[host] makes this command somewhat magic. If you omit \[host] it searches
    for all devices in the default FortiManager (fmg) in the inventory.
    """
    inventory = Inventory(config.inventory_file)
    result = fgt.monitor.hamaster(host)
    data = {"fotoobo": result.all_results()}

    if smtp_server:
        if smtp_server in inventory.assets:
            result.send_messages_as_mail(
                inventory.assets[smtp_server],
                ["warning", "error"],
                count=True,
                command=True,
            )

        else:
            log.warning("SMTP server %s not in found in inventory.", smtp_server)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            log.debug("template_file is: %s", template_file)
            output: Result[Dict[str, Dict[str, str]]] = Result()
            output.push_result("_hamaster", data)
            output.save_with_template("_hamaster", template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just pretty print the output to the console
        if raw:
            pprint(data, expand_all=True)

        else:
            result.print_result_as_table(
                headers=["FortiGate Cluster", "Status"],
                title="FortiGate HA master status",
            )
