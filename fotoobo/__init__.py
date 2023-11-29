"""
fotoobo - make IT easy

This is fotoobo, the mighty Fortinet toolbox for managing your Fortinet environment. It is meant
to be extendable to your needs. It's most likely the swiss army knife for Fortinet infrastructure.
"""

from .fortinet import FortiAnalyzer, FortiClientEMS, FortiGate, FortiManager

__all__ = ["FortiAnalyzer", "FortiClientEMS", "FortiGate", "FortiManager"]
__version__: str = "2.0.1"
