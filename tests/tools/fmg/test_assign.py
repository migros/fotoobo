"""Test fmg tools assign"""

from pathlib import Path
from unittest.mock import MagicMock

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
                        "state": 4,
                        "task_id": 42,
                        "detail": "dummy_detail",
                        "start_tm": 10,
                        "end_tm": 20,
                        "history": [{"detail": "dummy_history"}],
                    }
                ]
            )
        ),
    )
    result = assign("dummy_adoms", "dummy_policy", "test_fmg")
    messages = result.get_messages("test_fmg")
    assert len(messages) == 2
    assert messages[0]["level"] == "debug"
    assert messages[0]["message"] == "42: dummy / dummy_detail (10 sec)"
    assert messages[1]["message"] == "- dummy_history"
