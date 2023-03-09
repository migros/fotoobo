"""
The utilities (utils) module

Use this module to add business logic for your Fortinet infrastructure. This module uses the
relevant fotoobo and Fortinet modules. By default the utils functions are invoked by the cli app,
but they may also be accessed directly.
"""

from . import convert, ems, faz, fgt, fmg, get
from .greet import greet

__all__ = [
    "convert",
    "ems",
    "faz",
    "fgt",
    "fmg",
    "get",
    "greet",
]
