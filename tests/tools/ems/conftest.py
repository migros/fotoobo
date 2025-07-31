"""
The pytest fixtures for the ems tools package
"""

from unittest.mock import Mock

import pytest


@pytest.fixture(autouse=True)
def ems_login(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock the FortiClient EMS login to always return 200 without to really login.
    """

    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.login", Mock(return_value=200)
    )
