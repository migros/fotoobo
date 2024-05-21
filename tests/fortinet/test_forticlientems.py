# type: ignore
"""
Test the FortiClient EMS class
"""

# pylint: disable=no-member

from pathlib import Path
from unittest.mock import ANY, MagicMock

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
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={"result": {"retval": 1, "message": "Login successful."}},
                    status_code=200,
                )
            ),
        )
        ems = FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", ssl_verify=False)
        assert ems.api_url == "https://ems_dummy:443/api/v1"
        assert ems.login() == 200
        assert ems.session.headers["Referer"] == "https://ems_dummy"
        assert ems.session.headers["X-CSRFToken"] == "dummy_csrf_token"

    @staticmethod
    def test_login_with_valid_cookie(monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS with valid session cookie path given"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.get",
            MagicMock(
                return_value=ResponseMock(
                    json={"result": {"retval": 1, "message": "Login successful."}}, status_code=200
                )
            ),
        )
        ems = FortiClientEMS(
            "ems_dummy", "dummy_user", "dummy_pass", "tests/data/", ssl_verify=False
        )
        assert ems.api_url == "https://ems_dummy:443/api/v1"
        assert ems.login() == 200
        assert ems.session.headers["Referer"] == "https://ems_dummy"
        assert ems.session.headers["X-CSRFToken"] == "dummy_csrf_token_from_cache\n"

    @staticmethod
    def test_login_with_invalid_cookie(monkeypatch: MonkeyPatch, temp_dir: Path) -> None:
        """Test the login to a FortiClient EMS with invalid session cookie given"""
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
                    status_code=401,
                )
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status_code=200,
                ),
            ),
        )
        # Copy cookie and token file to the temp folder
        source = Path("tests/data/ems_dummy.cookie")
        destination = Path(temp_dir / "ems_dummy.cookie")
        destination.write_bytes(source.read_bytes())
        source = Path("tests/data/ems_dummy.csrf")
        destination = Path(temp_dir / "ems_dummy.csrf")
        destination.write_bytes(source.read_bytes())

        ems = FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", temp_dir, ssl_verify=False)
        assert ems.api_url == "https://ems_dummy:443/api/v1"
        assert ems.login() == 200

    @staticmethod
    def test_login_with_cookie_but_unable_to_save_it(
        monkeypatch: MonkeyPatch, temp_dir: Path
    ) -> None:
        """Test the login to a FortiClient EMS with no session cookie when cookie enabled which
        cannot be saved."""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status_code=200,
                ),
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.pickle.dump",
            MagicMock(side_effect=FileNotFoundError()),
        )
        # Remove the cookie and token file (if they exist)
        Path(temp_dir / "ems_dummy.cookie").unlink(missing_ok=True)
        Path(temp_dir / "ems_dummy.csrf").unlink(missing_ok=True)

        ems = FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", temp_dir, ssl_verify=False)
        assert ems.api_url == "https://ems_dummy:443/api/v1"
        assert ems.login() == 200
        requests.Session.post.assert_called_with(
            "https://ems_dummy:443/api/v1/auth/signin",
            headers={
                "User-Agent": "python-requests/2.32.1",
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Referer": "https://ems_dummy",
                "X-CSRFToken": "dummy_csrf_token",
            },
            json={"name": "dummy_user", "password": "dummy_pass"},
            params=None,
            timeout=3,
            verify=False,
        )

    @staticmethod
    def test_login_with_cookie_and_invalid_session(
        monkeypatch: MonkeyPatch, temp_dir: Path
    ) -> None:
        """Test the login to a FortiClient EMS with a session cookie but invalid session"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.get",
            MagicMock(return_value=ResponseMock(status_code=401)),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status_code=200,
                ),
            ),
        )
        # Copy cookie and token file to the temp folder
        source = Path("tests/data/ems_dummy.cookie")
        destination = Path(temp_dir / "ems_dummy.cookie")
        destination.write_bytes(source.read_bytes())
        source = Path("tests/data/ems_dummy.csrf")
        destination = Path(temp_dir / "ems_dummy.csrf")
        destination.write_bytes(source.read_bytes())

        ems = FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", temp_dir, ssl_verify=False)
        assert ems.api_url == "https://ems_dummy:443/api/v1"
        assert ems.login() == 200
        requests.Session.get.assert_called_with(
            "https://ems_dummy:443/api/v1/system/serial_number",
            headers={
                "User-Agent": "python-requests/2.32.1",
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Referer": "https://ems_dummy",
                "X-CSRFToken": "dummy_csrf_token",
            },
            json=None,
            params=None,
            timeout=3,
            verify=False,
        )
        requests.Session.post.assert_called_with(
            "https://ems_dummy:443/api/v1/auth/signin",
            headers={
                "User-Agent": "python-requests/2.32.1",
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Referer": "https://ems_dummy",
                "X-CSRFToken": "dummy_csrf_token",
            },
            json={"name": "dummy_user", "password": "dummy_pass"},
            params=None,
            timeout=3,
            verify=False,
        )

    @staticmethod
    def test_login_with_invalid_cookie_path(temp_dir: Path, monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS with an invalid cookie path"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status_code=200,
                )
            ),
        )
        ems = FortiClientEMS("host_1", "dummy_user", "dummy_pass", temp_dir, ssl_verify=False)
        assert ems.api_url == "https://host_1:443/api/v1"
        assert ems.login() == 200

    @staticmethod
    def test_login_with_csrf_token_not_found(temp_dir: Path, monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiClient EMS when the csrf token was not found in the headers"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken_missing=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status_code=200,
                )
            ),
        )
        ems = FortiClientEMS("host_2", "dummy_user", "dummy_pass", temp_dir, ssl_verify=False)
        assert ems.api_url == "https://host_2:443/api/v1"
        assert ems.login() == 200

    @staticmethod
    def test_logout_with_valid_session(monkeypatch: MonkeyPatch) -> None:
        """Test the logout from a FortiClient EMS with a valid session"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(return_value=ResponseMock(json={}, status_code=200)),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False)
        response = ems.logout()
        assert response == 200

    @staticmethod
    def test_logout_with_invalid_session(monkeypatch: MonkeyPatch) -> None:
        """Test the logout from a FortiClient EMS with an invalid session"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(return_value=ResponseMock(json={}, status_code=401)),
        )
        with pytest.raises(APIError) as err:
            FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False).logout()
        assert "HTTP/401 Not Authorized" in str(err.value)

    @staticmethod
    def test_get_version_ok(monkeypatch: MonkeyPatch) -> None:
        """Test the get_version method with a valid get response"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(
                return_value=ResponseMock(
                    json={"data": {"System": {"VERSION": "1.2.3"}}},
                    status_code=200,
                )
            ),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass")
        response = ems.get_version()
        requests.Session.get.assert_called_with(
            "https://host:443/api/v1/system/consts/get?system_update_time=1",
            headers=ANY,
            json=None,
            params=None,
            timeout=3,
            verify=True,
        )
        assert response == "1.2.3"

    @staticmethod
    def test_get_version_invalid(monkeypatch: MonkeyPatch) -> None:
        """Test the get_version method with an invalid get response (invalid data, no version)"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", MagicMock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            MagicMock(return_value=ResponseMock(json={"data": {"System": {}}}, status_code=200)),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False)
        with pytest.raises(GeneralWarning) as err:
            ems.get_version()
        assert "Did not find any FortiClient EMS version number in response" in str(err.value)
        requests.Session.get.assert_called_with(
            "https://host:443/api/v1/system/consts/get?system_update_time=1",
            headers=ANY,
            json=None,
            params=None,
            timeout=3,
            verify=False,
        )

    @staticmethod
    def test_get_version_api_error(monkeypatch: MonkeyPatch) -> None:
        """Test the get_version method with an APIError exception"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
            MagicMock(side_effect=APIError(999)),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False)
        with pytest.raises(GeneralWarning, match=r"host returned: unknown"):
            ems.get_version()
