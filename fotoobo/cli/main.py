"""
This is the main cli module. If fotoobo is started from the command line the main script starts
app() from within here. Every level of the command line tool is represented by a subdirectory.
If you extend the cli make sure you are in the correct directory or create a new one if there are
more than a few subcommands.

Caution: Use docstrings with care as they are used to print help texts on any command.
"""
import logging
import sys
from typing import Optional

import typer

from fotoobo import utils
from fotoobo.cli import convert, get
from fotoobo.cli.ems import main as ems
from fotoobo.cli.faz import main as faz
from fotoobo.cli.fgt import main as fgt
from fotoobo.cli.fmg import main as fmg
from fotoobo.helpers import cli_path
from fotoobo.helpers.config import config
from fotoobo.helpers.log import Log
from fotoobo.helpers.output import print_logo

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})
log = logging.getLogger("fotoobo")


def version_callback(value: bool) -> None:
    """The version callback"""
    if value:
        utils.get.version()
        raise typer.Exit()


@app.callback()
def callback(  # pylint: disable=too-many-arguments
    context: typer.Context,
    config_file: str = typer.Option(
        "fotoobo.yaml",
        "--config",
        "-c",
        help="The fotoobo configuration file",
        show_default=False,
        metavar="[file]",
    ),
    log_switch: bool = typer.Option(None, "--log", "-l", help="Enable logging"),
    log_level: str = typer.Option(
        None,
        "--loglevel",
        help="The logging level. Choose from CRITICAL, ERROR, WARNING, INFO, DEBUG",
        metavar="[level]",
    ),
    nologo: bool = typer.Option(None, "--nologo", help="Disable the logo"),
    version: Optional[bool] = typer.Option(  # pylint: disable=unused-argument
        None, "--version", "-V", help="Get fotoobo version", callback=version_callback
    ),
) -> None:
    """
    The Fortinet Toolbox (fotoobo) - make IT easy

    This tool lets you interact with Fortinet assets like devices and their configuration.

    For help see the README.md or theAttribute specific documentation in the docs folder.
    """
    config.load_configuration(config_file)
    config.no_logo = True if nologo else config.no_logo

    if log_level:
        log_level = log_level.upper()

    Log.configure_logging(log_switch, log_level)

    if not config.no_logo:
        print_logo()

    log.debug("let the magic begin")

    for attr in dir(config):
        if attr.startswith("_") or attr in ["config", "load_configuration"]:
            continue

        log.debug("option '%s' is '%s'", attr, getattr(config, attr))

    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)
    log.audit(f'command="{" ".join(sys.argv)}"')  # type: ignore

    # info = context.to_info_dict()
    # rprint(info)
    # save_json_file("data/cli.json", info)
    config.cli_info = context.to_info_dict()


@app.command(hidden=True)
def greet(
    name: Optional[str] = typer.Argument(
        "", help="The name of the person to greet", show_default=False, metavar="[name]"
    ),
    bye: bool = typer.Option(False, "--bye", "-b", help="Also write bye at the end"),
    log_enabled: bool = typer.Option(False, "--log", "-l", help="Enable logging"),
) -> None:
    """
    This is the hidden Greeting function.
    It allows you to greet someone with different colors in different languages.
    """
    utils.greet(str(name), bye, log_enabled)


# fotoobo specific commands
app.add_typer(convert.app, name="convert", help="Convert commands for fotoobo")
app.add_typer(get.app, name="get", help="get commands for fotoobo")

# commands for the Fortinet products
app.add_typer(ems.app, name="ems", help="Commands for FortiClient EMS")
app.add_typer(faz.app, name="faz", help="Commands for FortiAnalyzer")
app.add_typer(fgt.app, name="fgt", help="Commands for FortiGate")
app.add_typer(fmg.app, name="fmg", help="Commands for FortiManager")
