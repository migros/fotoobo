"""
The fotoobo get commands
"""
import logging

import typer
from rich import print as rich_print
from rich.panel import Panel

from fotoobo.helpers import cli_path
from fotoobo.tools import get

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The fotoobo get command callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


@app.command()
def inventory() -> None:
    """
    Print a summary over your fotoobo inventory.
    """
    result = get.inventory()

    result.print_result_as_table(title="fotoobo inventory", headers=["Device", "Hostname", "Type"])


@app.command()
def version(
    verbose: bool = typer.Option(
        False, "-v", help="Verbose output (also show the most important modules)."
    ),
) -> None:
    """
    Print the fotoobo version.
    """
    result = get.version(verbose)

    if verbose:
        out_list = [
            {
                "module": "[bold]fotoobo[/]",
                "version": f"[bold]{result.get_result('version')[0]['version']}[/]",
            }
        ]

        out_list += result.get_result("version")[1:]

    else:
        out_list = result.get_result("version")

    result.print_table_raw(out_list, headers=[], auto_header=False, title="fotoobo version")


@app.command()
def commands() -> None:
    """
    Print the fotoobo commands structure.
    """
    result = get.commands()
    tree = result.get_result("commands")

    rich_print(
        Panel(tree, border_style="#FF33BB", title="cli commands structure", title_align="right")
    )
