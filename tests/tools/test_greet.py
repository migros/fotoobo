"""
Test the hidden greeting utility.
"""

from typing import Any

from fotoobo.tools import greet


def test_greet(capsys: Any) -> None:
    """
    Test greet.
    """

    # Act
    greet("name", False, False)

    # Assert
    out, _ = capsys.readouterr()
    assert "Hi name" in out
    assert "Aloha" in out
    assert "Good Bye" not in out


def test_greet_bye(capsys: Any) -> None:
    """
    Test greet with bye.
    """

    # Act
    greet("name", True, False)

    # Assert
    out, _ = capsys.readouterr()
    assert "Hi name" in out
    assert "Aloha" in out
    assert "Good Bye" in out
