"""
The FortiClient EMS monitor commands
"""

import logging
from pathlib import Path
from typing import Union

import typer

from fotoobo.helpers import cli_path
from fotoobo.helpers.files import save_json_file
from fotoobo.tools.ems import monitor

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


HELP_TEXT_ARGUMENT_EMS = (
    "The FortiClient EMS hostname to access (must be defined in the inventory)."
)
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
    The ems get subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command(help="Monitor the FortiClient EMS connections.\n\n" + HELP_TEXT_TEMPLATE)
def connections(
    host: str = typer.Argument(
        "ems",
        help=HELP_TEXT_ARGUMENT_EMS,
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
    template_file: Union[None, Path] = typer.Option(
        None,
        "--template",
        "-t",
        help=HELP_TEXT_OPTION_TEMPLATE,
        metavar="[template]",
    ),
) -> None:
    """
    Monitor the FortiClient EMS connections.
    """
    result = monitor.connections(host)

    data = result.get_result(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            log.debug("template_file is: %s", template_file)
            result.save_with_template(host, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just pretty print the output to the console
        if raw:
            result.print_raw()

        else:
            conns = []
            for connection in result.get_result(host)["data"]:
                conns.append(
                    {
                        "token": connection["token"]
                        .replace("offline", "Offline ")
                        .replace("online", "Online"),
                        "value": connection["value"],
                        "name": connection["name"],
                    }
                )
            result.print_table_raw(
                conns, ["Token", "Count", "Description"], title="FortiClient connection status"
            )


@app.command(
    help="Monitor the endpoint management status in FortiClient EMS.\n\n" + HELP_TEXT_TEMPLATE
)
def endpoint_management_status(
    host: str = typer.Argument(
        "ems",
        help=HELP_TEXT_ARGUMENT_EMS,
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
    template_file: Union[None, Path] = typer.Option(
        None,
        "--template",
        "-t",
        help=HELP_TEXT_OPTION_TEMPLATE,
        metavar="[template]",
    ),
) -> None:
    """
    Monitor the endpoint management status in FortiClient EMS.
    """
    result = monitor.endpoint_management_status(host)

    data = result.get_result(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            result.save_with_template(host, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just pretty print the output to the console
        if raw:
            result.print_raw()

        else:
            endpoints = []
            for endpoint in result.get_result(host)["data"]:
                endpoints.append(
                    {
                        "name": endpoint["name"],
                        "value": endpoint["value"],
                    }
                )
            result.print_table_raw(
                endpoints, ["Status", "Count"], title="FortiClient management status"
            )


@app.command(help="Monitor the endpoint OS versions in FortiClient EMS.\n\n" + HELP_TEXT_TEMPLATE)
def endpoint_os_versions(
    host: str = typer.Argument(
        "ems",
        help=HELP_TEXT_ARGUMENT_EMS,
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
    template_file: Union[None, Path] = typer.Option(
        None,
        "--template",
        "-t",
        help=HELP_TEXT_OPTION_TEMPLATE,
        metavar="[template]",
    ),
) -> None:
    """
    Monitor the endpoint os versions in FortiClient EMS.
    """
    result = monitor.endpoint_os_versions(host)

    data = result.get_result(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            result.save_with_template(host, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just pretty print the output to the console
        if raw:
            result.print_raw()

        else:
            versions = []
            for _os, os_versions in result.get_result(host)["data"].items():
                for line in os_versions:
                    versions.append(
                        {"os": _os[10:], "fc_version": line["name"], "count": line["value"]}
                    )
            result.print_table_raw(versions, ["OS", "FC Version", "Count"])

            totals = []
            for _os, count in result.get_result(host)["fotoobo"].items():
                totals.append({"os": _os[10:], "count": count})
            result.print_table_raw(totals, ["OS", "Total"], title="Summary")


@app.command(
    help="Get the amount of FortiClient EMS devices which are online but policy is not in sync.\n\n"
    + HELP_TEXT_TEMPLATE
)
def endpoint_outofsync(
    host: str = typer.Argument(
        "ems",
        help=HELP_TEXT_ARGUMENT_EMS,
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
    template_file: Union[None, Path] = typer.Option(
        None,
        "--template",
        "-t",
        help=HELP_TEXT_OPTION_TEMPLATE,
        metavar="[template]",
    ),
) -> None:
    """
    Get amount of FortiClient EMS devices which are online but policy not in sync.
    """
    result = monitor.endpoint_online_outofsync(host)
    data = result.get_result(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            result.save_with_template(host, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just pretty print the output to the console
        if raw:
            result.print_raw()

        else:
            result.print_table_raw(
                [{"name": "out of sync", "count": result.get_result(host)["fotoobo"]["outofsync"]}],
                [],
                title="FortiClients not in synch",
            )


@app.command(help="Monitor the FortiClient EMS license.\n\n" + HELP_TEXT_TEMPLATE)
def license(  # pylint: disable=redefined-builtin
    host: str = typer.Argument(
        "ems",
        help=HELP_TEXT_ARGUMENT_EMS,
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
    template_file: Union[None, Path] = typer.Option(
        None,
        "--template",
        "-t",
        help=HELP_TEXT_OPTION_TEMPLATE,
        metavar="[template]",
    ),
) -> None:
    """
    Monitor the FortiClient EMS license.
    """
    result = monitor.license(host)
    data = result.get_result(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            result.save_with_template(host, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just pretty print the output to the console
        if raw:
            result.print_raw()
        else:
            licenses = []
            for key, value in result.get_result(host)["data"].items():
                licenses.append({"key": key, "value": value})
            result.print_table_raw(
                licenses, ["Key", "Value"], title="FortiClient EMS license information"
            )

            licenses = []
            for key, value in result.get_result(host)["fotoobo"].items():
                licenses.append({"key": key, "value": value})
            result.print_table_raw(
                licenses, ["Key", "Value"], title="FortiClient EMS license summary"
            )


@app.command()
def system(
    host: str = typer.Argument(
        "ems",
        help=HELP_TEXT_ARGUMENT_EMS,
        metavar="[host]",
    ),
    raw: bool = typer.Option(False, "-r", "--raw", help="Output raw data."),
) -> None:
    """
    Monitor the FortiClient EMS system information.
    """
    result = monitor.system(host)
    data = result.get_result(host)

    if raw:
        result.print_raw()

    else:
        _ = data.pop("license", {})  # pop "license" key as ist is not used (it's another command)

        result.print_table_raw(
            [
                {"key": "hostname", "hostname": data["name"]},
                {"key": "system_time", "system_time": data["system_time"]},
            ],
            ["Key", "Value"],
            title="FortiClient EMS status",
        )
