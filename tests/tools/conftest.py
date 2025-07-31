"""
The pytest fxtures for the tools package
"""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Change inventory file in config to test inventory.
    """

    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )
