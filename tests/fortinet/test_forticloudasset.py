"""
Test the FortiCloudAsset class.
"""

# mypy: disable-error-code=attr-defined

from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from fotoobo.exceptions.exceptions import GeneralWarning
from fotoobo.fortinet.forticloudasset import FortiCloudAsset
from tests.helper import ResponseMock


class TestFortiCloud:
    """
    Test the FortiCloud class.
    """

    @staticmethod
    def test_init() -> None:
        """
        Test the FortiCloudAsset init.
        """

        # Act
        cloud = FortiCloudAsset(
            username="dummy_username",
            password="dummy_password",
        )

        # Assert
        assert cloud.api_url == "https://support.fortinet.com:443/ES/api/registration/v3"
        assert cloud.password == "dummy_password"
        assert cloud.username == "dummy_username"
        assert cloud.access_token == ""
        assert cloud.ssl_verify is True
        assert cloud.token_path == ""
        assert cloud.type == "forticloudasset"
        assert cloud.ALLOWED_HTTP_METHODS == ["POST"]

    @staticmethod
    def test_api(monkeypatch: MonkeyPatch) -> None:
        """
        Test the FortiCloud api method.
        """

        # Arrange
        post_mock = Mock(return_value=ResponseMock(json={"key": "value"}, status_code=200))
        monkeypatch.setattr("requests.Session.post", post_mock)
        monkeypatch.setattr(
            "fotoobo.fortinet.forticloudasset.FortiCloudAsset.login", Mock(return_value=200)
        )
        forticloud = FortiCloudAsset("dummy_username", "dummy_password")

        # Act & Assert
        assert forticloud.api("post", "dummy").json() == {"key": "value"}
        post_mock.assert_called_with(
            "https://support.fortinet.com:443/ES/api/registration/v3/dummy",
            headers={"Content-Type": "application/json", "Authorization": "Bearer "},
            json={},
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "response, expected",
        (
            pytest.param({"version": "v1.1.1"}, "v1.1.1", id="v1.1.1"),
            pytest.param({"version": "dummy"}, "dummy", id="dummy"),
            pytest.param({"version": ""}, "", id="empty"),
        ),
    )
    def test_get_version(response: dict[str, str], expected: str, monkeypatch: MonkeyPatch) -> None:
        """
        Test get version.
        """

        # Arrange
        post_mock = Mock(return_value=response)
        monkeypatch.setattr("fotoobo.fortinet.forticloudasset.FortiCloudAsset.post", post_mock)

        # Act & Assert
        assert FortiCloudAsset("dummy_username", "dummy_password").get_version() == expected
        post_mock.assert_called_with(url="/folders/list")

    @staticmethod
    def test_get_version_api_http_error(monkeypatch: MonkeyPatch) -> None:
        """
        Test get version with http error.
        """

        # Arrange
        post_mock = Mock(return_value=ResponseMock(json={"version": "dummy"}, status_code=401))
        monkeypatch.setattr("requests.Session.post", post_mock)
        monkeypatch.setattr(
            "fotoobo.fortinet.forticloudasset.FortiCloudAsset.login", Mock(return_value=200)
        )

        # Act & Assert
        with pytest.raises(GeneralWarning, match=r"HTTP/401") as err:
            FortiCloudAsset("dummy_username", "dummy_password").get_version()

        assert "support.fortinet.com returned: HTTP/401 Not Authorized" in str(err.value)
        post_mock.assert_called_with(
            "https://support.fortinet.com:443/ES/api/registration/v3/folders/list",
            headers={"Content-Type": "application/json", "Authorization": "Bearer "},
            json={},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_login_with_no_cache(monkeypatch: MonkeyPatch, function_dir: Path) -> None:
        """
        Test login method.
        """

        # Arrange
        monkeypatch.setattr(
            "requests.post",
            Mock(
                return_value=ResponseMock(
                    json={"access_token": "dummy_access_token"}, status_code=200
                )
            ),
        )
        forticloud = FortiCloudAsset("dummy_username", "dummy_password", token_path=function_dir)

        # Act & Assert
        assert forticloud.login() == 200
        assert forticloud.access_token == "dummy_access_token"

    @staticmethod
    def test_login_with_valid_cache(monkeypatch: MonkeyPatch, function_dir: Path) -> None:
        """
        Test login method when a valid token is in the cache.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.post",
            Mock(return_value=ResponseMock(json={}, status_code=200)),
        )

        with open(function_dir / "support.fortinet.com.token", "w", encoding="UTF-8") as file:
            file.write("dummy_access_token")

        forticloud = FortiCloudAsset("dummy_username", "dummy_password", token_path=function_dir)

        # Act & Assert
        assert forticloud.login() == 200
        assert forticloud.access_token == "dummy_access_token"

    @staticmethod
    def test_login_with_invalid_cache(monkeypatch: MonkeyPatch, function_dir: Path) -> None:
        """
        Test login method when an invalid token is in the cache.
        """

        # Arrange
        token_file = function_dir / "support.fortinet.com.token"
        responses = Mock()
        responses.side_effect = [
            ResponseMock(json={}, status_code=401),
            ResponseMock(json={"access_token": "dummy_access_token"}, status_code=200),
        ]
        monkeypatch.setattr("requests.post", responses)
        token_file.write_text("invalid,access_token", encoding="UTF-8")

        forticloud = FortiCloudAsset("dummy_username", "dummy_password", token_path=function_dir)

        # Act & Assert
        assert forticloud.login() == 200
        assert forticloud.access_token == "dummy_access_token"
        assert token_file.read_text(encoding="UTF-8") == "dummy_access_token"

    @staticmethod
    def test_login_with_invalid_cache_and_alue_verror(
        monkeypatch: MonkeyPatch, function_dir: Path
    ) -> None:
        """
        Test login method when an invalid token is in the cache and the auth returns a ValueError.
        """

        # Arrange
        token_file = function_dir / "support.fortinet.com.token"
        responses = Mock()
        responses.side_effect = [
            ValueError("Invalid token"),
            ResponseMock(json={"access_token": "dummy_access_token"}, status_code=200),
        ]
        monkeypatch.setattr("requests.post", responses)
        token_file.write_text("invalid,access_token", encoding="UTF-8")

        forticloud = FortiCloudAsset("dummy_username", "dummy_password", token_path=function_dir)

        # Act & Assert
        assert forticloud.login() == 200
        assert forticloud.access_token == "dummy_access_token"
        assert token_file.read_text(encoding="UTF-8") == "dummy_access_token"

    @staticmethod
    def test_post(monkeypatch: MonkeyPatch) -> None:
        """
        Test get version with http error.
        """

        # Arrange
        post_mock = Mock(
            return_value=ResponseMock(json={"dummy_key": "dummy_value"}, status_code=200)
        )
        monkeypatch.setattr("requests.Session.post", post_mock)
        monkeypatch.setattr(
            "fotoobo.fortinet.forticloudasset.FortiCloudAsset.login", Mock(return_value=200)
        )
        forticloud = FortiCloudAsset("dummy_username", "dummy_password")

        # Act
        response = forticloud.post("/dummy_url")

        # Assert
        assert response == {"dummy_key": "dummy_value"}
        post_mock.assert_called_with(
            "https://support.fortinet.com:443/ES/api/registration/v3/dummy_url",
            headers={"Content-Type": "application/json", "Authorization": "Bearer "},
            json={},
            params=None,
            timeout=10,
            verify=True,
        )
