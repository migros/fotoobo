"""
Test fmg tools get adoms.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.fmg.get import adoms


def test_adoms(monkeypatch: MonkeyPatch) -> None:
    """
    Test get adoms.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.get_adoms",
        Mock(
            return_value=[
                {"name": "adom_1", "os_ver": "1", "mr": "2"},
                {"name": "adom_2", "os_ver": "3", "mr": "4"},
            ]
        ),
    )

    # Act
    result = adoms("test_fmg")

    # Assert
    assert len(result.results) == 2
    assert result.get_result("adom_1") == "1.2"
    assert result.get_result("adom_2") == "3.4"
