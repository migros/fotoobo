"""
Test fcasset tools get version.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.cloud.asset.get import version


def test_version(monkeypatch: MonkeyPatch) -> None:
    """
    Test get version.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticloudasset.FortiCloudAsset.get_version",
        Mock(return_value="3.0"),
    )

    # Act
    result = version("forticloudasset")

    # Assert
    data = result.get_result("forticloudasset")
    assert data == "3.0"
