# type: ignore
"""
Test the FortiClient EMS class
"""
from unittest.mock import MagicMock, patch

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import APIError, GeneralWarning
from fotoobo.fortinet.forticlientems import FortiClientEMS
from tests.helper import ResponseMock


class TestFortiClientEMS:
    """Test the FortiClientEMS class"""

    @staticmethod
    def test_login_without_cookie(monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS with no session cookie given"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={"result": {"retval": 1, "message": "Login successful."}}, status=200
                )
            ),
        )
        ems = FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", ssl_verify=False)
        assert ems.api_url == "https://ems_dummy/api/v1"
        assert ems.login() == 200

    @staticmethod
    def test_login_with_valid_cookie(monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS with valid session cookie path given"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.get",
            MagicMock(
                return_value=ResponseMock(
                    json={"result": {"retval": 1, "message": "Login successful."}}, status=200
                )
            ),
        )
        ems = FortiClientEMS(
            "ems_dummy", "dummy_user", "dummy_pass", "tests/data/", ssl_verify=False
        )
        assert ems.api_url == "https://ems_dummy/api/v1"
        assert ems.login() == 200

    @staticmethod
    def test_login_with_invalid_cookie(monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS with no session cookie given"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.get",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "result": {
                            "retval": -4,
                            "message": "Session has expired or does not exist.",
                        },
                    },
                    status=401,
                )
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status=200,
                ),
            ),
        )
        ems = FortiClientEMS(
            "ems_dummy", "dummy_user", "dummy_pass", "tests/data/", ssl_verify=False
        )
        assert ems.api_url == "https://ems_dummy/api/v1"
        assert ems.login() == 200

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": "Login successful."},
                },
                status=200,
            )
        ),
    )
    def test_login_with_invalid_cookie_path(temp_dir: str) -> None:
        """Test the login to a FortiClient EMS with an invalid cookie path"""
        ems = FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", temp_dir, ssl_verify=False)
        assert ems.api_url == "https://ems_dummy/api/v1"
        assert ems.login() == 200

    @staticmethod
    @patch("fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200))
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(return_value=ResponseMock(json={}, status=200)),
    )
    def test_logout_with_valid_session() -> None:
        """Test the logout from a FortiClient EMS with a valid session"""
        ems = FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", ssl_verify=False)
        response = ems.logout()
        assert response == 200

    @staticmethod
    @patch("fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200))
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(return_value=ResponseMock(json={}, status=401)),
    )
    def test_logout_with_invalid_session() -> None:
        """Test the logout from a FortiClient EMS with an invalid session"""
        with pytest.raises(APIError) as err:
            FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", ssl_verify=False).logout()
        assert "HTTP/401 Not Authorized" in str(err.value)

    @staticmethod
    @patch("fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200))
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(
            return_value=ResponseMock(
                json={"data": {"System": {"VERSION": "1.2.3"}}},
                status=200,
            )
        ),
    )
    def test_get_version_ok() -> None:
        """Test the get_version method with a valid get response"""
        ems = FortiClientEMS("dummy_ems", "dummy_user", "dummy_pass")
        response = ems.get_version()
        requests.Session.get.assert_called_with(
            "https://dummy_ems/api/v1/system/consts/get?system_update_time=1",
            params={},
            verify=True,
            timeout=3,
        )
        assert response == "1.2.3"

    @staticmethod
    @patch("fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200))
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.get",
        MagicMock(return_value=ResponseMock(json={"data": {"System": {}}}, status=200)),
    )
    def test_get_version_invalid() -> None:
        """Test the get_version method with an invalid get response (invalid data, no version)"""
        ems = FortiClientEMS("dummy_ems", "dummy_user", "dummy_pass", ssl_verify=False)
        with pytest.raises(GeneralWarning) as err:
            ems.get_version()
        assert "did not find any FortiClient EMS version number in response" in str(err.value)
        requests.Session.get.assert_called_with(
            "https://dummy_ems/api/v1/system/consts/get?system_update_time=1",
            params={},
            verify=False,
            timeout=3,
        )

    @staticmethod
    def test_get_version_api_error(monkeypatch: MonkeyPatch) -> None:
        """Test the get_version method with an APIError exception"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
            MagicMock(side_effect=APIError(999)),
        )
        ems = FortiClientEMS("dummy_ems", "dummy_user", "dummy_pass", ssl_verify=False)
        with pytest.raises(GeneralWarning, match=r"dummy_ems returned: unknown"):
            ems.get_version()
