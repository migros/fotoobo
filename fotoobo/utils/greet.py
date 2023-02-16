"""
The fotoobo greeting utility

This function is a hidden fotoobo command which is meant for testing purposes. It has no functional
effect. Use and modify it whenever you want. But be sure to also write the tests for it.
"""

import logging

import typer

log = logging.getLogger("fotoobo")


def greet(name: str, bye: bool, log_enabled: bool) -> None:
    """
    This is the hidden Greeting function.
    It allows you to greet someone with different colors in different languages.
    """
    log.debug("local logging option is: %s", log_enabled)
    greeting = f"{typer.style('🌼Aloha🌼', fg=typer.colors.GREEN)}"
    greeting += f", {typer.style('⚽Hola⚽', fg=typer.colors.YELLOW)}"
    greeting += f", {typer.style('✨Bonjour✨', fg=typer.colors.BLUE)}"
    greeting += f", {typer.style('⚡Hallo⚡', fg=typer.colors.RED)}"
    greeting += f", {typer.style('☀Ciao☀', fg=typer.colors.BRIGHT_GREEN)}"
    greeting += f", {typer.style('🌟Konnichiwa🌟', fg=typer.colors.BRIGHT_YELLOW)}"
    greeting += f", {typer.style('🎉Howdy-doody🎉', fg=typer.colors.BRIGHT_BLUE)}!"
    if name:
        greeting = f"Hi {typer.style(name, bold=True)}, {greeting}"

    typer.echo(greeting)
    if bye:
        typer.echo(typer.style("Good Bye", fg=typer.colors.BLACK, bg=typer.colors.WHITE))
