"""
Test ems tools get version.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.ems.get import version


def test_version(monkeypatch: MonkeyPatch) -> None:
    """
    Test get version.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.get_version",
        Mock(return_value="1.1.1"),
    )

    # Act
    result = version("test_ems")

    # Assert
    data = result.get_result("test_ems")
    assert data == "v1.1.1"
