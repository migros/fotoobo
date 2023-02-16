"""
Test the hidden greeting utility
"""

from typing import Any

from fotoobo.utils import greet


def test_greet(capsys: Any) -> None:
    """Test greet"""
    greet("name", False, False)
    out, _ = capsys.readouterr()
    assert "Hi name" in out
    assert "Aloha" in out
    assert "Good Bye" not in out


def test_greet_bye(capsys: Any) -> None:
    """Test greet with bye"""
    greet("name", True, False)
    out, _ = capsys.readouterr()
    assert "Hi name" in out
    assert "Aloha" in out
    assert "Good Bye" in out
