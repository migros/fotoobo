"""
The fotoobo convert commands
"""
import logging

import typer

from fotoobo import utils
from fotoobo.helpers import cli_path

app = typer.Typer()
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


@app.command()
def checkpoint(
    infile: str = typer.Argument(
        ...,
        help="The json file to read the Checkpoint objects from",
        show_default=False,
        metavar="[infile]",
    ),
    outfile: str = typer.Argument(
        ...,
        help="The json file to write the converted objects to",
        show_default=False,
        metavar="[outfile]",
    ),
    obj_type: str = typer.Argument(
        ...,
        help="The type of objects to convert",
        show_default=False,
        metavar="[type]",
    ),
    cache_dir: str = typer.Argument(
        None,
        help="The cache directory to use",
        show_default=False,
        metavar="[cache_dir]",
    ),
) -> None:
    """
    Convert Checkpoint assets into Fortinet objects

    The Checkpoint objects have to be prepared in a json file. See convert.md for the syntax.
    The argument [type] defines what object type to convert.
    """
    utils.convert_checkpoint(infile, outfile, obj_type, cache_dir)
