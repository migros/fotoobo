"""
The Fortinet module

Here we add all the functions, classes and methods for accessing and interacting with the Fortinet
infrastructure. This module is meant to be held very generic.
"""

from .fortianalyzer import FortiAnalyzer
from .forticlientems import FortiClientEMS
from .fortigate import FortiGate
from .fortimanager import FortiManager

__all__ = ["FortiAnalyzer", "FortiClientEMS", "FortiGate", "FortiManager"]
