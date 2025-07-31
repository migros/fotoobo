"""
Test the FortiAnalyzer class.
"""

# mypy: disable-error-code=attr-defined

from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from fotoobo.fortinet.fortianalyzer import FortiAnalyzer
from tests.helper import ResponseMock


class TestFortiAnalyzer:
    """
    Test the FortiAnalyzer class.

    Should this really be tested as FortiAnalyzer.get_version only calls super().get_version() which
    is the FortiManager.get_version method. This is tested in test_fortimanager.py.
    I'll leave it here for completeness.
    """

    @staticmethod
    @pytest.mark.parametrize(
        "response, expected",
        (
            pytest.param({"result": [{"data": {"Version": "v1.1.1-xyz"}}]}, "v1.1.1", id="ok"),
            pytest.param({"result": [{"data": {"Version": ""}}]}, "", id="empty"),
            pytest.param({"result": [{"data": {}}]}, "", id="empty data"),
            pytest.param({"result": []}, "", id="empty result"),
            pytest.param({}, "", id="empty return_value"),
        ),
    )
    def test_get_version(response: Mock, expected: str, monkeypatch: MonkeyPatch) -> None:
        """
        Test FortiAnalyzer get version.
        """

        # Arrange
        response_mock = Mock(return_value=ResponseMock(json=response, status_code=200))
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", response_mock)

        # Act & Assert
        assert FortiAnalyzer("host", "", "").get_version() == expected
        response_mock.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/sys/status"}], "session": ""},
            params=None,
            timeout=3,
            verify=True,
        )
