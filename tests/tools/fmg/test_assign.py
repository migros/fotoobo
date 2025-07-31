"""
Test fmg tools assign.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch

from fotoobo.tools.fmg import assign


def test_assign(monkeypatch: MonkeyPatch) -> None:
    """
    Test assign.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.assign_all_objects", Mock(return_value=1)
    )
    monkeypatch.setattr(
        "fotoobo.fortinet.fortimanager.FortiManager.wait_for_task",
        Mock(
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

    # Act
    result = assign("dummy_adoms", "dummy_policy", "test_fmg")

    # Assert
    messages = result.get_messages("test_fmg")
    assert len(messages) == 2
    assert messages[0]["level"] == "debug"
    assert messages[0]["message"] == "42: dummy / dummy_detail (10 sec)"
    assert messages[1]["message"] == "- dummy_history"
