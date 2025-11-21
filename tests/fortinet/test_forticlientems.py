"""
Test the FortiClient EMS class.
"""

# mypy: disable-error-code=attr-defined

from pathlib import Path
from unittest.mock import ANY, Mock

import pytest
from pytest import MonkeyPatch

from fotoobo.exceptions import APIError, GeneralWarning
from fotoobo.fortinet.forticlientems import FortiClientEMS
from tests.helper import ResponseMock


class TestFortiClientEMS:
    """
    Test the FortiClientEMS class.
    """

    @staticmethod
    def test_login_without_cookie(monkeypatch: MonkeyPatch) -> None:
        """
        Test the login to a FortiClient EMS with no session cookie given.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.post",
            Mock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={"result": {"retval": 1, "message": "Login successful."}},
                    status_code=200,
                )
            ),
        )
        ems = FortiClientEMS("ems_dummy", "dummy_user", "dummy_pass", ssl_verify=False)
        assert ems.api_url == "https://ems_dummy:443/api/v1"

        # Act & Assert
        assert ems.login() == 200
        assert ems.session.headers["Referer"] == "https://ems_dummy"
        assert ems.session.headers["X-CSRFToken"] == "dummy_csrf_token"

    @staticmethod
    def test_login_with_valid_cookie(monkeypatch: MonkeyPatch) -> None:
        """
        Test the login to a FortiClient EMS with valid session cookie path given.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.get",
            Mock(
                return_value=ResponseMock(
                    json={"result": {"retval": 1, "message": "Login successful."}}, status_code=200
                )
            ),
        )
        ems = FortiClientEMS(
            "ems_dummy", "dummy_user", "dummy_pass", "tests/data/", ssl_verify=False
        )
        assert ems.api_url == "https://ems_dummy:443/api/v1"

        # Act & Assert
        assert ems.login() == 200
        assert ems.session.headers["Referer"] == "https://ems_dummy"
        assert ems.session.headers["X-CSRFToken"] == "dummy_csrf_token_from_cache\n"

    @staticmethod
    def test_login_with_invalid_cookie(monkeypatch: MonkeyPatch, function_dir: Path) -> None:
        """
        Test the login to a FortiClient EMS with invalid session cookie given.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.requests.Session.get",
            Mock(
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
            Mock(
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
        destination = Path(function_dir / "ems_dummy.cookie")
        destination.write_bytes(source.read_bytes())
        source = Path("tests/data/ems_dummy.csrf")
        destination = Path(function_dir / "ems_dummy.csrf")
        destination.write_bytes(source.read_bytes())

        ems = FortiClientEMS(
            "ems_dummy", "dummy_user", "dummy_pass", str(function_dir), ssl_verify=False
        )
        assert ems.api_url == "https://ems_dummy:443/api/v1"

        # Act & Assert
        assert ems.login() == 200

    @staticmethod
    def test_login_with_cookie_but_unable_to_save_it(
        monkeypatch: MonkeyPatch, function_dir: Path
    ) -> None:
        """
        Test the login to a FortiClient EMS with no session cookie when cookie enabled which
        cannot be saved.
        """

        # Arrange
        post_mock = Mock(
            return_value=ResponseMock(
                headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                json={
                    "result": {"retval": 1, "message": "Login successful."},
                },
                status_code=200,
            ),
        )
        monkeypatch.setattr("fotoobo.fortinet.forticlientems.requests.Session.post", post_mock)
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.pickle.dump",
            Mock(side_effect=FileNotFoundError()),
        )
        # Remove the cookie and token file (if they exist)
        (function_dir / "ems_dummy.cookie").unlink(missing_ok=True)
        (function_dir / "ems_dummy.csrf").unlink(missing_ok=True)

        ems = FortiClientEMS(
            "ems_dummy", "dummy_user", "dummy_pass", str(function_dir), ssl_verify=False
        )
        assert ems.api_url == "https://ems_dummy:443/api/v1"

        # Act & Assert
        assert ems.login() == 200
        post_mock.assert_called_with(
            "https://ems_dummy:443/api/v1/auth/signin",
            headers=ANY,
            json={"name": "dummy_user", "password": "dummy_pass"},
            params=None,
            timeout=3,
            verify=False,
        )

    @staticmethod
    def test_login_with_cookie_and_invalid_session(
        monkeypatch: MonkeyPatch, function_dir: Path
    ) -> None:
        """
        Test the login to a FortiClient EMS with a session cookie but invalid session.
        """

        # Arrange
        get_mock = Mock(return_value=ResponseMock(status_code=401))
        monkeypatch.setattr("fotoobo.fortinet.forticlientems.requests.Session.get", get_mock)
        post_mock = Mock(
            return_value=ResponseMock(
                headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                json={
                    "result": {"retval": 1, "message": "Login successful."},
                },
                status_code=200,
            ),
        )
        monkeypatch.setattr("fotoobo.fortinet.forticlientems.requests.Session.post", post_mock)
        # Copy cookie and token file to the temp folder
        source = Path("tests/data/ems_dummy.cookie")
        destination = Path(function_dir / "ems_dummy.cookie")
        destination.write_bytes(source.read_bytes())
        source = Path("tests/data/ems_dummy.csrf")
        destination = Path(function_dir / "ems_dummy.csrf")
        destination.write_bytes(source.read_bytes())

        ems = FortiClientEMS(
            "ems_dummy", "dummy_user", "dummy_pass", str(function_dir), ssl_verify=False
        )
        assert ems.api_url == "https://ems_dummy:443/api/v1"

        # Act & Assert
        assert ems.login() == 200
        get_mock.assert_called_with(
            "https://ems_dummy:443/api/v1/system/serial_number",
            headers=ANY,
            json=None,
            params=None,
            timeout=3,
            verify=False,
        )
        post_mock.assert_called_with(
            "https://ems_dummy:443/api/v1/auth/signin",
            headers=ANY,
            json={"name": "dummy_user", "password": "dummy_pass"},
            params=None,
            timeout=3,
            verify=False,
        )

    @staticmethod
    def test_login_with_invalid_cookie_path(function_dir: Path, monkeypatch: MonkeyPatch) -> None:
        """
        Test the login to a FortiClient EMS with an invalid cookie path.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            Mock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status_code=200,
                )
            ),
        )
        ems = FortiClientEMS(
            "host_1", "dummy_user", "dummy_pass", str(function_dir), ssl_verify=False
        )
        assert ems.api_url == "https://host_1:443/api/v1"

        # Act & Assert
        assert ems.login() == 200

    @staticmethod
    def test_login_with_csrf_token_not_found(function_dir: Path, monkeypatch: MonkeyPatch) -> None:
        """
        Test the login to a FortiClient EMS when the csrf token was not found in the headers.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            Mock(
                return_value=ResponseMock(
                    headers={"Set-Cookie": "csrftoken_missing=dummy_csrf_token;"},
                    json={
                        "result": {"retval": 1, "message": "Login successful."},
                    },
                    status_code=200,
                )
            ),
        )
        ems = FortiClientEMS(
            "host_2", "dummy_user", "dummy_pass", str(function_dir), ssl_verify=False
        )
        assert ems.api_url == "https://host_2:443/api/v1"

        # Act & Assert
        assert ems.login() == 200

    @staticmethod
    def test_logout_with_valid_session(monkeypatch: MonkeyPatch) -> None:
        """
        Test the logout from a FortiClient EMS with a valid session.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", Mock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            Mock(return_value=ResponseMock(json={}, status_code=200)),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False)

        # Act
        response = ems.logout()

        # Assert
        assert response == 200

    @staticmethod
    def test_logout_with_invalid_session(monkeypatch: MonkeyPatch) -> None:
        """
        Test the logout from a FortiClient EMS with an invalid session.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", Mock(return_value=200)
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.get",
            Mock(return_value=ResponseMock(json={}, status_code=401)),
        )

        # Act & Assert
        with pytest.raises(APIError) as err:
            FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False).logout()

        assert "HTTP/401 Not Authorized" in str(err.value)

    @staticmethod
    def test_get_version_ok(monkeypatch: MonkeyPatch) -> None:
        """
        Test the get_version method with a valid get response.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", Mock(return_value=200)
        )
        get_mock = Mock(
            return_value=ResponseMock(
                json={"data": {"System": {"VERSION": "1.2.3"}}},
                status_code=200,
            )
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.get", get_mock)
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass")

        # Act
        response = ems.get_version()

        # Assert
        get_mock.assert_called_with(
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
        """
        Test the get_version method with an invalid get response (invalid data, no version).
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.login", Mock(return_value=200)
        )
        get_mock = Mock(return_value=ResponseMock(json={"data": {"System": {}}}, status_code=200))
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.get", get_mock)
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False)

        # Act & Assert
        with pytest.raises(GeneralWarning) as err:
            ems.get_version()

        assert "Did not find any FortiClient EMS version number in response" in str(err.value)
        get_mock.assert_called_with(
            "https://host:443/api/v1/system/consts/get?system_update_time=1",
            headers=ANY,
            json=None,
            params=None,
            timeout=3,
            verify=False,
        )

    @staticmethod
    def test_get_version_api_error(monkeypatch: MonkeyPatch) -> None:
        """
        Test the get_version method with an APIError exception.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
            Mock(side_effect=APIError(999)),
        )
        ems = FortiClientEMS("host", "dummy_user", "dummy_pass", ssl_verify=False)

        # Act & Assert
        with pytest.raises(GeneralWarning, match=r"host returned: unknown"):
            ems.get_version()
