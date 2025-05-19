"""
The Fortinet module

Here we add all the functions, classes and methods for accessing and interacting with the Fortinet
infrastructure. This module is meant to be held very generic.
"""

from .fortianalyzer import FortiAnalyzer
from .forticlientems import FortiClientEMS
from .forticloud import FortiCloudAsset
from .fortigate import FortiGate
from .fortimanager import FortiManager

__all__ = ["FortiAnalyzer", "FortiClientEMS", "FortiCloudAsset", "FortiGate", "FortiManager"]
