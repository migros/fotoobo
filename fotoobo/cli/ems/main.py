"""
The FortiClient EMS commands
"""
import logging

import typer

from fotoobo.cli.ems import get_commands as get
from fotoobo.cli.ems import monitor
from fotoobo.helpers import cli_path

app = typer.Typer()
log = logging.getLogger("fotoobo")


@app.callback()
def callback(context: typer.Context) -> None:
    """
    The ems subcommand callback

    Args:
        context (Context): the context object of the typer app
    """
    cli_path.append(str(context.invoked_subcommand))
    log.debug("about to execute command: '%s'", context.invoked_subcommand)


app.add_typer(get.app, name="get", help="FortiClient EMS get commands")
app.add_typer(monitor.app, name="monitor", help="FortiClient EMS monitor commands")
