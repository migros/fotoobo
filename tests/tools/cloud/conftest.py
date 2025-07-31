"""
The pytest fixtures for the forticloud tools package
"""

from unittest.mock import Mock

import pytest


@pytest.fixture(autouse=True)
def fc_login(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Mock the FortiCloud login to always return 200 without to really login.
    """

    monkeypatch.setattr(
        "fotoobo.fortinet.forticloudasset.FortiCloudAsset.login", Mock(return_value=200)
    )
