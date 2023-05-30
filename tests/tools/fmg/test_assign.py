"""Test fmg tools assign"""


from unittest.mock import MagicMock
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.tools.fmg import assign


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


@pytest.fixture(autouse=True)
def fmg_login(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiManager login to always return 200 without to really login"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.login",
        MagicMock(return_value=200),
    )


@pytest.fixture(autouse=True)
def fmg_logout(monkeypatch: MonkeyPatch) -> None:
    """Mock the FortiManager logout to always return 200 without to really logout"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.logout",
        MagicMock(return_value=200),
    )


def test_assign(monkeypatch: MonkeyPatch) -> None:
    """Test assign"""
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.assign_all_objects", MagicMock(return_value=1)
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.wait_for_task",
        MagicMock(
            return_value=(
                [
                    {
                        "name": "dummy",
                        "state": 0,
                        "task_id": 42,
                        "detail": "",
                        "start_tm": 10,
                        "end_tm": 20,
                        "history": [{"detail": ""}],
                    }
                ]
            )
        ),
    )
    assign("dummy_adoms", "dummy_policy", "test_fmg")
    assert True
