"""
The pytest fixtures for the FortiManager tools package.
"""

from unittest.mock import Mock

import pytest


@pytest.fixture(autouse=True)
def fmg_login(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock the FortiManager login to always return 200 without to really login.
    """

    monkeypatch.setattr("fotoobo.fortinet.fortimanager.FortiManager.login", Mock(return_value=200))


@pytest.fixture(autouse=True)
def fmg_logout(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock the FortiManager logout to always return 200 without to really logout.
    """

    monkeypatch.setattr("fotoobo.fortinet.fortimanager.FortiManager.logout", Mock(return_value=200))
