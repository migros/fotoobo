"""
utils fmg
"""

from . import get
from .assign_ import assign
from .set_ import set  # pylint: disable=redefined-builtin

__all__ = ["assign", "get", "set"]
