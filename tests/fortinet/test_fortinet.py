# type: ignore
"""
Test the Fortinet class
"""
from unittest.mock import MagicMock

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from urllib3.exceptions import NewConnectionError, SSLError

from fotoobo.exceptions import APIError, GeneralError
from fotoobo.fortinet.fortinet import Fortinet
from tests.helper import ResponseMock


class FortinetTestClass(Fortinet):
    """
    Represents one Fortinet sub class
    """

    def get_version(self) -> str:
        """just add it because it's an abstract method"""
        return "0.0.0"


class TestFortinet:
    """Test the Fortinet class"""

    @staticmethod
    def test_get_vendor() -> None:
        """Test the get_vendor method"""
        assert Fortinet.get_vendor() == "Fortinet"

    @staticmethod
    def test_instantiation_default() -> None:
        """Test the instantiation with an empty sub class"""
        fortigate = FortinetTestClass("host")
        assert fortigate.hostname == "host"
        assert fortigate.session.proxies == {"http": None, "https": None}
        assert fortigate.ssl_verify

    @staticmethod
    def test_instantiation_with_proxy() -> None:
        """Test the instantiation with an empty sub class"""
        fortigate = FortinetTestClass("host", proxy="proxy")
        assert fortigate.session.proxies == {"http": "proxy", "https": "proxy"}

    @staticmethod
    def test_instantiation_no_ssl_verify() -> None:
        """Test the instantiation with an empty sub class"""
        fortigate = FortinetTestClass("host", ssl_verify=False)
        assert not fortigate.ssl_verify

    @staticmethod
    def test_api_get(monkeypatch: MonkeyPatch) -> None:
        """Test api get"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(return_value=ResponseMock(json={"version": "v1.1.1"}, status=200)),
        )
        response = FortinetTestClass("dummy").api("get", "url")
        assert response.status_code == 200
        assert response.json() == {"version": "v1.1.1"}
        requests.Session.get.assert_called_with(
            "url", headers=None, json=None, params=None, timeout=3, verify=True
        )

    @staticmethod
    def test_api_post(monkeypatch: MonkeyPatch) -> None:
        """Test api post"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(return_value=ResponseMock(json={"version": "v1.1.1"}, status=200)),
        )
        response = FortinetTestClass("dummy").api("post", "url")
        assert response.status_code == 200
        assert response.json() == {"version": "v1.1.1"}
        requests.Session.post.assert_called_with(
            "url", headers=None, json=None, params=None, timeout=3, verify=True
        )

    @staticmethod
    @pytest.mark.parametrize(
        "method", (pytest.param("get", id="get"), pytest.param("post", id="post"))
    )
    def test_api_get_connection_timeout(method: str, monkeypatch: MonkeyPatch) -> None:
        """Test api get with connection timeout"""
        monkeypatch.setattr(
            f"fotoobo.fortinet.fortinet.requests.Session.{method}",
            MagicMock(side_effect=requests.exceptions.ConnectTimeout()),
        )
        with pytest.raises(GeneralError, match=r"Connection timeout \(dummy\)"):
            FortinetTestClass("dummy").api(method, "url")

    @staticmethod
    @pytest.mark.parametrize(
        "method", (pytest.param("get", id="get"), pytest.param("post", id="post"))
    )
    def test_api_get_read_timeout(method: str, monkeypatch: MonkeyPatch) -> None:
        """Test api get with read timeout"""
        monkeypatch.setattr(
            f"fotoobo.fortinet.fortinet.requests.Session.{method}",
            MagicMock(side_effect=requests.exceptions.ReadTimeout()),
        )
        with pytest.raises(GeneralError, match=r"Read timeout \(dummy\)"):
            FortinetTestClass("dummy").api(method, "url")

    @staticmethod
    def test_api_unknown_method() -> None:
        """Test api with unknown method"""
        with pytest.raises(NotImplementedError, match=r"HTTP method 'DUMMY' is not implemented"):
            FortinetTestClass("dummy").api("dummy", "url")

    @staticmethod
    @pytest.mark.parametrize(
        "method", (pytest.param("get", id="get"), pytest.param("post", id="post"))
    )
    def test_api_connection_error_unknown(method: str, monkeypatch: MonkeyPatch) -> None:
        """Test api get with unknown connection error
        Here we test the exceptions if there is no err.args[0].reason.args[0] object
        """
        monkeypatch.setattr(
            f"fotoobo.fortinet.fortinet.requests.Session.{method}",
            MagicMock(side_effect=requests.exceptions.ConnectionError()),
        )
        with pytest.raises(GeneralError) as err:
            FortinetTestClass("dummy").api(method, "url")
        assert "Unknown connection error" in str(err.value)

    @staticmethod
    @pytest.mark.parametrize(
        "method", (pytest.param("get", id="get"), pytest.param("post", id="post"))
    )
    @pytest.mark.parametrize(
        "reason, expected",
        (
            pytest.param(
                "... Connection refused ...",
                "Connection refused",
                id="connection refused",
            ),
            pytest.param(
                "... Name or service not known ...",
                "Name or service not known",
                id="unknown hostname",
            ),
        ),
    )
    def test_api_connection_error(
        method: str, reason: str, expected: str, monkeypatch: MonkeyPatch
    ) -> None:
        """Test api with connection errors"""
        monkeypatch.setattr(
            f"fotoobo.fortinet.fortinet.requests.Session.{method}",
            MagicMock(
                side_effect=requests.exceptions.ConnectionError(
                    MagicMock(reason=NewConnectionError(reason, message="")),
                )
            ),
        )
        with pytest.raises(GeneralError) as err:
            FortinetTestClass("dummy").api(method, "url")
        assert expected in str(err.value)

    @staticmethod
    @pytest.mark.parametrize(
        "method", (pytest.param("get", id="get"), pytest.param("post", id="post"))
    )
    @pytest.mark.parametrize(
        "ssl_error, expected",
        (
            pytest.param(
                SSLError(MagicMock(verify_message="unable to get local issuer certificate")),
                r"Unable to get local issuer certificate \(dummy\)",
                id="unknown cert",
            ),
            pytest.param(
                SSLError(MagicMock(spec=())),
                r"Unknown SSL error \(dummy\)",
                id="unknown error",
            ),
        ),
    )
    def test_api_ssl_error(
        method: str, ssl_error: SSLError, expected: str, monkeypatch: MonkeyPatch
    ) -> None:
        """Test api with connection errors when the cert is not valid
        We have to do this test especially for the cert_check because its message is not in
        err.args[0].reason.args[0] but in err.args[0].reason.args[0].verify_message
        """
        monkeypatch.setattr(
            f"fotoobo.fortinet.fortinet.requests.Session.{method}",
            MagicMock(side_effect=requests.exceptions.SSLError(MagicMock(reason=ssl_error))),
        )
        with pytest.raises(GeneralError, match=expected):
            FortinetTestClass("dummy").api(method, "url")

    @staticmethod
    @pytest.mark.parametrize(
        "method", (pytest.param("get", id="get"), pytest.param("post", id="post"))
    )
    @pytest.mark.parametrize(
        "status_code, expected",
        (
            pytest.param(400, "HTTP/400 Bad Request", id="HTTP/400"),
            pytest.param(401, "HTTP/401 Not Authorized", id="HTTP/401"),
            pytest.param(403, "HTTP/403 Forbidden", id="HTTP/403"),
            pytest.param(404, "HTTP/404 Resource Not Found", id="HTTP/404"),
            pytest.param(405, "HTTP/405 Method Not Allowed", id="HTTP/405"),
            pytest.param(413, "HTTP/413 Request Entity Too Large", id="HTTP/413"),
            pytest.param(424, "HTTP/424 Failed Dependency", id="HTTP/424"),
            pytest.param(429, "HTTP/429 Access temporarily blocked", id="HTTP/429"),
            pytest.param(500, "HTTP/500 Internal Server Error", id="HTTP/500"),
            pytest.param(999, "HTTP/999 general API Error", id="HTTP/999"),
        ),
    )
    def test_api_http_error(
        method: str, status_code: ResponseMock, expected: str, monkeypatch: MonkeyPatch
    ) -> None:
        """Test api with http errors
        Here we test the response from a device if the response.status_code is not 200.
        """
        monkeypatch.setattr(
            f"fotoobo.fortinet.fortinet.requests.Session.{method}",
            MagicMock(return_value=ResponseMock(json={"dummy": "dummy"}, status=status_code)),
        )
        with pytest.raises(APIError) as err:
            FortinetTestClass("dummy").api(method, "url")
        assert expected in str(err.value)
