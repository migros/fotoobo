# type: ignore
"""
Test the FortiGate class
"""
from typing import Dict

# pylint: disable=no-member
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralWarning
from fotoobo.fortinet.fortigate import FortiGate
from fotoobo.fortinet.fortinet import Fortinet
from tests.helper import ResponseMock


class TestFortiGate:
    """Test the FortiGate class"""

    @staticmethod
    def test_api(monkeypatch: MonkeyPatch) -> None:
        """Test the FortiGate api method"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.Fortinet.api",
            MagicMock(return_value=ResponseMock(json={"key": "value"}, status=200)),
        )
        fortigate = FortiGate("", "token")
        assert fortigate.api("get", "dummy").json() == {"key": "value"}
        assert fortigate.session.headers["Authorization"] == "Bearer token"
        Fortinet.api.assert_called_with(
            "get", "dummy", payload=None, params=None, timeout=None, headers=None
        )

    @staticmethod
    def test_backup(monkeypatch: MonkeyPatch) -> None:
        """Test the FortiGate backup method"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortigate.FortiGate.api",
            MagicMock(return_value=ResponseMock(text="Dummy Backup Data", status=200)),
        )
        assert FortiGate("", "").backup(timeout=66) == "Dummy Backup Data"
        FortiGate.api.assert_called_with(
            "get", "monitor/system/config/backup", params={"scope": "global"}, timeout=66
        )

    @staticmethod
    @pytest.mark.parametrize(
        "response, expected",
        (
            pytest.param({"version": "v1.1.1"}, "v1.1.1", id="v1.1.1"),
            pytest.param({"version": "dummy"}, "dummy", id="dummy"),
            pytest.param({"version": ""}, "", id="empty"),
            pytest.param({"dummy": ""}, "unknown", id="key not found"),
        ),
    )
    def test_get_version(response: Dict[str, str], expected: str, monkeypatch: MonkeyPatch) -> None:
        """Test get version"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortigate.FortiGate.api",
            MagicMock(return_value=ResponseMock(json=response, status=200)),
        )
        assert FortiGate("", "").get_version() == expected
        FortiGate.api.assert_called_with("get", "monitor/system/status")

    @staticmethod
    def test_get_version_api_http_error(monkeypatch: MonkeyPatch) -> None:
        """Test get version with http error"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(return_value=ResponseMock(json={"dummy": "dummy"}, status=404)),
        )
        with pytest.raises(GeneralWarning) as err:
            FortiGate("", "").get_version()
        assert "HTTP/404 Resource Not Found" in str(err.value)
