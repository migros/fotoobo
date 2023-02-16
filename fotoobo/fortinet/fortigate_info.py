"""
The FortiGateInfo class
"""
from dataclasses import dataclass


@dataclass(eq=False, order=False)
class FortiGateInfo:
    """
    This dataclass holds FortiGate meta information from the configuration file.
    """

    # pylint: disable=too-many-instance-attributes

    # attributes in alphabetical order
    buildno: str = ""
    conf_file_ver: str = ""
    global_vdom: str = ""
    hostname: str = ""
    model: str = ""
    opmode: str = ""
    os_version: str = ""
    type: str = ""
    user: str = ""
    vdom: str = ""  # 0 in single vdom mode, 1 in multiple vdom mode
