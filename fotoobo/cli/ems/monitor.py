"""
The FortiClient EMS monitor commands
"""

import logging

import typer

from fotoobo.helpers import cli_path
from fotoobo.helpers.files import save_json_file, save_with_template
from fotoobo.helpers.output import print_dicttable
from fotoobo.utils.ems import monitor

app = typer.Typer()
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The ems get subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command()
def connections(
    host: str = typer.Argument(
        "ems",
        help="The FortiClient EMS hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
    output_file: str = typer.Option(
        "",
        "--output",
        "-o",
        help="The file to write the output to",
        metavar="[output]",
    ),
    template_file: str = typer.Option(
        "",
        "--template",
        "-t",
        help="The jinja2 template to use (use with -o)",
        metavar="[template]",
    ),
) -> None:
    """
    Monitoring the FortiClient EMS connections.

    If you add a template with the -t option you may render the output with any Jinja2 template
    file. You may use any of the given data returned from the license endpoint. Additionally there
    are enriched variables under 'fotoobo' which you also may use in your template.
    """
    data = monitor.connections(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            save_with_template(data, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        print_dicttable(data, title="FortiClient EMS connections")


@app.command()
def endpoint_management_status(
    host: str = typer.Argument(
        "ems",
        help="The FortiClient EMS hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
    output_file: str = typer.Option(
        "",
        "--output",
        "-o",
        help="The file to write the output to",
        metavar="[output]",
    ),
    template_file: str = typer.Option(
        "",
        "--template",
        "-t",
        help="The jinja2 template to use (use with -o)",
        metavar="[template]",
    ),
) -> None:
    """
    Monitoring the endpoint management status in FortiClient EMS.

    If you add a template with the -t option you may render the output with any Jinja2 template
    file.
    """
    data = monitor.endpoint_management_status(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            save_with_template(data, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just print the output to the console
        print_dicttable(data, title="FortiClient EMS endpoints")


@app.command()
def endpoint_outofsync(
    host: str = typer.Argument(
        "ems",
        help="The FortiClient EMS hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
    output_file: str = typer.Option(
        "",
        "--output",
        "-o",
        help="The file to write the output to",
        metavar="[output]",
    ),
    template_file: str = typer.Option(
        "",
        "--template",
        "-t",
        help="The jinja2 template to use (use with -o)",
        metavar="[template]",
    ),
) -> None:
    """
    Get amount of FortiClient EMS devices which are online but policy not in sync.

    If you add a template with the -t option you may render the output with any Jinja2 template
    file.
    """
    data = monitor.endpoint_online_outofsync(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            save_with_template(data, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just print the output to the console
        print_dicttable(data, title="FortiClient EMS endpoints")


@app.command()
def endpoint_os_versions(
    host: str = typer.Argument(
        "ems",
        help="The FortiClient EMS hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
    output_file: str = typer.Option(
        "",
        "--output",
        "-o",
        help="The file to write the output to",
        metavar="[output]",
    ),
    template_file: str = typer.Option(
        "",
        "--template",
        "-t",
        help="The jinja2 template to use (use with -o)",
        metavar="[template]",
    ),
) -> None:
    """
    Monitoring the endpoint os versions in FortiClient EMS.

    If you add a template with the -t option you may render the output with any Jinja2 template
    file.
    """
    data = monitor.endpoint_os_versions(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            save_with_template(data, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just print the output to the console
        print_dicttable(data, title="FortiClient EMS endpoints")


@app.command()
def license(  # pylint: disable=redefined-builtin
    host: str = typer.Argument(
        "ems",
        help="The FortiClient EMS hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
    output_file: str = typer.Option(
        "",
        "--output",
        "-o",
        help="The file to write the output to",
        metavar="[output]",
    ),
    template_file: str = typer.Option(
        "",
        "--template",
        "-t",
        help="The jinja2 template to use (use with -o)",
        metavar="[template]",
    ),
) -> None:
    """
    Monitoring the FortiClient EMS license.

    If you add a template with the -t option you may render the output with any Jinja2 template
    file. You may use any of the given data returned from the license endpoint. Additionally there
    are enriched variables under 'fotoobo' which you also may use in your template.
    """
    data = monitor.license(host)

    if output_file:
        log.debug("output_file is: %s", output_file)

        if template_file:
            save_with_template(data, template_file, output_file)

        else:
            # write to file without a template (raw output)
            save_json_file(output_file, data)

    else:
        # if no output file is given just print the output to the console
        print_dicttable(data, title="FortiClient EMS license information")


@app.command()
def system(
    host: str = typer.Argument(
        "ems",
        help="The FortiClient EMS hostname to access (must be defined in inventory)",
        metavar="[host]",
    ),
) -> None:
    """
    Monitoring the FortiClient EMS system information.
    """
    data = monitor.system(host)

    license_data = data.pop("license", {})  # pop "license" key to print that in another table
    print_dicttable(data, title="FortiClient EMS system information")
    print_dicttable(license_data, title="FortiClient EMS system.license information")
