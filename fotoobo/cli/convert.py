"""
The fotoobo convert commands
"""
import logging
from pathlib import Path

import typer

from fotoobo.helpers import cli_path
from fotoobo.helpers.files import load_json_file, save_json_file
from fotoobo.tools import convert

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fotoobo convert command callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command(no_args_is_help=True)
def checkpoint(
    infile: Path = typer.Argument(
        ...,
        help="The json file to read the Checkpoint objects from.",
        show_default=False,
        metavar="[infile]",
    ),
    outfile: Path = typer.Argument(
        ...,
        help="The json file to write the converted objects to.",
        show_default=False,
        metavar="[outfile]",
    ),
    obj_type: str = typer.Argument(
        ...,
        help="The type of objects to convert.",
        show_default=False,
        metavar="[type]",
    ),
    cache_dir: Path = typer.Argument(
        None,
        help="The cache directory to use.",
        show_default=False,
        metavar="[cache_dir]",
    ),
) -> None:
    """
    Convert Checkpoint assets into Fortinet objects.

    The Checkpoint objects have to be prepared in a json file. See
    https://fotoobo.readthedocs.io/en/latest/usage/convert.html for more information.
    """
    checkpoint_assets = load_json_file(infile)

    result = convert.checkpoint(checkpoint_assets, obj_type, outfile.name, cache_dir)

    save_json_file(outfile, result.get_result("fortinet_assets"))
