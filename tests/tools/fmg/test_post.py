"""
Test fmg tools post.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from fotoobo.exceptions import GeneralWarning
from fotoobo.tools.fmg import post


def test_post(monkeypatch: MonkeyPatch) -> None:
    """
    Test POST.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.tools.fmg.main.load_json_file", Mock(return_value={"dummy": "dummy"})
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.post", Mock(return_value=["dummy_message"])
    )

    # Act
    result = post(file=Path("dummy_file"), adom="dummy_adom", host="test_fmg")

    # Assert
    assert result.get_messages("test_fmg")[0]["message"] == "dummy_message"


def test_post_exception_empty_payload_file(monkeypatch: MonkeyPatch) -> None:
    """
    Test POST with exception when there is no data in the payload file.
    """

    # Arrange
    monkeypatch.setattr("fotoobo.tools.fmg.main.load_json_file", Mock(return_value=[]))

    # Act & Assert
    with pytest.raises(GeneralWarning, match=r"There is no data in the given file"):
        post(file=Path("dummy_file"), adom="dummy_adom", host="dummy_host")
