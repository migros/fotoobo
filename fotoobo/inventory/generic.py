"""
A module for defining a generic device
"""


from typing import Union


class GenericDevice:
    """
    This is the class for a generic device.

    All kwarg will be unpacked and written to the instance as attributes. There are some mandatory
    attributes which will be filled with a default value.
    """

    def __init__(self, **kwargs: Union[str, int, bool]) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.hostname = getattr(self, "hostname", "")
        self.type = getattr(self, "type", "generic")
