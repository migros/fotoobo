"""
Test the FortiCloudAsset class
"""

# pylint: disable=no-member
# mypy: disable-error-code=attr-defined

from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions.exceptions import GeneralWarning
from fotoobo.fortinet.forticloudasset import FortiCloudAsset
from tests.helper import ResponseMock


class TestFortiCloud:
    """Test the FortiCloud class"""

    @staticmethod
    def test_init() -> None:
        """Test the FortiCloud init"""
        cloud = FortiCloudAsset(
            username="dummy_username",
            password="dummy_password",
        )

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
        """Test the FortiCloud api method"""
        monkeypatch.setattr(
            "requests.Session.post",
            MagicMock(return_value=ResponseMock(json={"key": "value"}, status_code=200)),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.forticloudasset.FortiCloudAsset.login", MagicMock(return_value=200)
        )
        forticloud = FortiCloudAsset("dummy_username", "dummy_password")
        # forticloud.access_token = "dummy_token"
        assert forticloud.api("post", "dummy").json() == {"key": "value"}
        requests.Session.post.assert_called_with(
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
    def test_get_version(response: Dict[str, str], expected: str, monkeypatch: MonkeyPatch) -> None:
        """Test get version"""
        monkeypatch.setattr(
            "fotoobo.fortinet.forticloudasset.FortiCloudAsset.post",
            MagicMock(return_value=response),
        )
        assert FortiCloudAsset("dummy_username", "dummy_password").get_version() == expected
        FortiCloudAsset.post.assert_called_with(url="/folders/list")

    @staticmethod
    def test_get_version_api_http_error(monkeypatch: MonkeyPatch) -> None:
        """Test get version with http error"""
        monkeypatch.setattr(
            "requests.Session.post",
            MagicMock(return_value=ResponseMock(json={"version": "dummy"}, status_code=401)),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.forticloudasset.FortiCloudAsset.login", MagicMock(return_value=200)
        )
        with pytest.raises(GeneralWarning, match=r"HTTP/401") as err:
            FortiCloudAsset("dummy_username", "dummy_password").get_version()
        assert "support.fortinet.com returned: HTTP/401 Not Authorized" in str(err.value)
        requests.Session.post.assert_called_with(
            "https://support.fortinet.com:443/ES/api/registration/v3/folders/list",
            headers={"Content-Type": "application/json", "Authorization": "Bearer "},
            json={},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_login_with_no_cache(monkeypatch: MonkeyPatch, temp_dir: Path) -> None:
        """Test login method"""
        monkeypatch.setattr(
            "requests.post",
            MagicMock(
                return_value=ResponseMock(
                    json={"access_token": "dummy_access_token"}, status_code=200
                )
            ),
        )

        forticloud = FortiCloudAsset("dummy_username", "dummy_password", token_path=temp_dir)
        assert forticloud.login() == 200
        assert forticloud.access_token == "dummy_access_token"

    @staticmethod
    def test_login_with_valid_cache(monkeypatch: MonkeyPatch, temp_dir: Path) -> None:
        """Test login method when a valid token is in the cache"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.post",
            MagicMock(return_value=ResponseMock(json={}, status_code=200)),
        )

        with open(temp_dir / "support.fortinet.com.token", "w", encoding="UTF-8") as file:
            file.write("dummy_access_token")

        forticloud = FortiCloudAsset("dummy_username", "dummy_password", token_path=temp_dir)
        assert forticloud.login() == 200
        assert forticloud.access_token == "dummy_access_token"

    @staticmethod
    def test_login_with_invalid_cache(monkeypatch: MonkeyPatch, temp_dir: Path) -> None:
        """Test login method when an invalid token is in the cache"""
        token_file = temp_dir / "support.fortinet.com.token"
        responses = MagicMock()
        responses.side_effect = [
            ResponseMock(json={}, status_code=401),
            ResponseMock(json={"access_token": "dummy_access_token"}, status_code=200),
        ]
        monkeypatch.setattr("requests.post", responses)
        token_file.write_text("invalid,access_token", encoding="UTF-8")

        forticloud = FortiCloudAsset("dummy_username", "dummy_password", token_path=temp_dir)
        assert forticloud.login() == 200
        assert forticloud.access_token == "dummy_access_token"
        assert token_file.read_text(encoding="UTF-8") == "dummy_access_token"

    @staticmethod
    def test_login_with_invalid_cache_and_alue_verror(
        monkeypatch: MonkeyPatch, temp_dir: Path
    ) -> None:
        """Test login method when an invalid token is in the cache and the auth returns a
        ValueError"""
        token_file = temp_dir / "support.fortinet.com.token"
        responses = MagicMock()
        responses.side_effect = [
            ValueError("Invalid token"),
            ResponseMock(json={"access_token": "dummy_access_token"}, status_code=200),
        ]
        monkeypatch.setattr("requests.post", responses)
        token_file.write_text("invalid,access_token", encoding="UTF-8")

        forticloud = FortiCloudAsset("dummy_username", "dummy_password", token_path=temp_dir)
        assert forticloud.login() == 200
        assert forticloud.access_token == "dummy_access_token"
        assert token_file.read_text(encoding="UTF-8") == "dummy_access_token"

    @staticmethod
    def test_post(monkeypatch: MonkeyPatch) -> None:
        """Test get version with http error"""
        monkeypatch.setattr(
            "requests.Session.post",
            MagicMock(
                return_value=ResponseMock(json={"dummy_key": "dummy_value"}, status_code=200)
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.forticloudasset.FortiCloudAsset.login", MagicMock(return_value=200)
        )
        forticloud = FortiCloudAsset("dummy_username", "dummy_password")
        response = forticloud.post("/dummy_url")
        assert response == {"dummy_key": "dummy_value"}
        requests.Session.post.assert_called_with(
            "https://support.fortinet.com:443/ES/api/registration/v3/dummy_url",
            headers={"Content-Type": "application/json", "Authorization": "Bearer "},
            json={},
            params=None,
            timeout=10,
            verify=True,
        )
