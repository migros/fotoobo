"""
Test the output helper
"""

from pathlib import Path
from typing import Any

import pytest

from fotoobo.helpers.output import (
    print_logo,
    write_policy_to_html,
)


@pytest.fixture
def html_test_file(temp_dir: str) -> Path:
    """Returns the filename of a json test file"""
    return Path(temp_dir) / "test_file.html"


def test_print_logo(capsys: Any) -> None:
    """Test print_logo"""
    print_logo()
    out, _ = capsys.readouterr()
    assert "f o t o o b o" in out


def test_write_policy_to_html(html_test_file: Path) -> None:  # pylint: disable=redefined-outer-name
    """Test write_policy_to_html"""
    assert not html_test_file.is_file()
    write_policy_to_html(
        [
            {"h1": "h1", "h2": "h2", "h3": "h3"},
            {"global-label": "dummy", "groups": "dummy"},
            {"_hitcount": 0, "status": 0, "_last_hit": 0, "action": 0, "send-deny-packet": 0},
            {"_hitcount": 1, "status": 1, "_last_hit": 1, "action": 1},
        ],
        html_test_file,
    )
    assert html_test_file.is_file()
