"""
Test fmg tools get version.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.fmg.get import version


def test_version(monkeypatch: MonkeyPatch) -> None:
    """
    Test get version.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.get_version",
        Mock(return_value="1.1.1"),
    )

    # Act
    result = version("test_fmg")

    # Assert
    assert result.get_result("test_fmg") == "1.1.1"
