"""
The pytest fixture for the FAZ tools package.
"""

from unittest.mock import Mock

import pytest


@pytest.fixture(autouse=True)
def faz_login(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock the FortiAnalyzer login to always return 200 without to really login.
    """

    monkeypatch.setattr(
        "fotoobo.fortinet.fortianalyzer.FortiAnalyzer.login", Mock(return_value=200)
    )


@pytest.fixture(autouse=True)
def faz_logout(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock the FortiAnalyzer logout to always return 200 without to really logout.
    """

    monkeypatch.setattr(
        "fotoobo.fortinet.fortianalyzer.FortiAnalyzer.logout", Mock(return_value=200)
    )
