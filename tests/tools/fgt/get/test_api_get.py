"""
Test fgt tools api_get
"""

# pylint: disable=no-member
# mypy: disable-error-code=attr-defined
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

import fotoobo
from fotoobo.tools.fgt.get import api_get
from tests.helper import ResponseMock


@pytest.fixture(autouse=True)
def inventory_file(monkeypatch: MonkeyPatch) -> None:
    """Change inventory file in config to test inventory"""
    monkeypatch.setattr(
        "fotoobo.helpers.config.config.inventory_file", Path("tests/data/inventory.yaml")
    )


def test_api_get(monkeypatch: MonkeyPatch) -> None:
    """Test api_get method"""
    response_mock = ResponseMock(json=[{"http_method": "GET", "results": []}], status_code=200)
    monkeypatch.setattr(
        "fotoobo.fortinet.fortigate.FortiGate.api", MagicMock(return_value=response_mock)
    )
    result = api_get("test_fgt_1", "/test/dummy/fake")
    data = result.get_result("test_fgt_1")
    assert data
    assert data == [{"http_method": "GET", "results": []}]
    fotoobo.fortinet.fortigate.FortiGate.api.assert_called_with(
        method="get", url="/test/dummy/fake", params={"vdom": "*"}, timeout=None
    )
