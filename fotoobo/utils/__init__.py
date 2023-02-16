"""
The utilities (utils) module

Use this module to add business logic for your Fortinet infrastructure. This module uses the
relevant fotoobo and Fortinet modules. By default the utils functions are invoked by the cli app,
but they may also be accessed directly.
"""

from . import ems, faz, fgt, fmg
from .convert import convert_checkpoint
from .fgt.confcheck import fgt_confcheck
from .get import commands, inventory, version
from .greet import greet

__all__ = [
    "convert_checkpoint",
    "ems",
    "faz",
    "fgt",
    "fgt_confcheck",
    "fmg",
    "inventory",
    "greet",
    "version",
]
