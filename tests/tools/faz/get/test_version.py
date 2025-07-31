"""
Test faz tools get version.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.faz.get import version


def test_version(monkeypatch: MonkeyPatch) -> None:
    """
    Test get version.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortianalyzer.FortiAnalyzer.get_version", Mock(return_value="1.1.1")
    )

    # Act
    result = version("test_faz")

    # Assert
    data = result.get_result("test_faz")
    assert data == "1.1.1"
