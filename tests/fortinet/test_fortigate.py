"""
Test the FortiGate class
"""

# pylint: disable=no-member
# mypy: disable-error-code=attr-defined

from typing import Dict
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
    def test_init_no_hostname(monkeypatch: MonkeyPatch) -> None:
        """Test the FortiGate init when not specifying a hostname"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.Fortinet.api",
            MagicMock(return_value=ResponseMock(json={"key": "value"}, status_code=200)),
        )
        with pytest.raises(GeneralWarning) as err:
            FortiGate("", "token")
        assert "No hostname specified" in str(err.value)

    @staticmethod
    def test_api(monkeypatch: MonkeyPatch) -> None:
        """Test the FortiGate api method"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.Fortinet.api",
            MagicMock(return_value=ResponseMock(json={"key": "value"}, status_code=200)),
        )
        fortigate = FortiGate("dummy_hostname", "token")
        assert fortigate.api("get", "dummy").json() == {"key": "value"}
        assert fortigate.session.headers["Authorization"] == "Bearer token"
        Fortinet.api.assert_called_with(
            "get", "dummy", payload=None, params=None, timeout=None, headers=None
        )

    def test_api_get(self, monkeypatch: MonkeyPatch) -> None:
        """Test the FortiGate api_get method"""
        response_mock = ResponseMock(json=[{"http_method": "GET", "results": []}], status_code=200)
        monkeypatch.setattr(
            "fotoobo.fortinet.fortigate.FortiGate.api", MagicMock(return_value=response_mock)
        )
        fortigate = FortiGate("dummy_hostname", "token")
        result = fortigate.api_get("/test/dummy/fake")
        assert result == [{"http_method": "GET", "results": []}]
        FortiGate.api.assert_called_with(
            method="get", url="/test/dummy/fake", params={"vdom": "*"}, timeout=None
        )

    @staticmethod
    def test_backup(monkeypatch: MonkeyPatch) -> None:
        """Test the FortiGate backup method"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortigate.FortiGate.api",
            MagicMock(return_value=ResponseMock(text="Dummy Backup Data", status_code=200)),
        )
        assert FortiGate("dummy_hostname", "").backup(timeout=66) == "Dummy Backup Data"
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
            MagicMock(return_value=ResponseMock(json=response, status_code=200)),
        )
        assert FortiGate("dummy_hostname", "").get_version() == expected
        FortiGate.api.assert_called_with("get", "monitor/system/status")

    @staticmethod
    def test_get_version_api_http_error(monkeypatch: MonkeyPatch) -> None:
        """Test get version with http error"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(return_value=ResponseMock(json={"dummy": "dummy"}, status_code=404)),
        )
        with pytest.raises(GeneralWarning) as err:
            FortiGate("dummy_hostname", "").get_version()
        assert "HTTP/404 Resource Not Found" in str(err.value)
