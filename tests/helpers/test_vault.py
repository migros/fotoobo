"""
Test the Hashicorp Vault helper
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions.exceptions import GeneralError
from fotoobo.helpers.vault import Client
from tests.helper import ResponseMock


class TestClient:
    """Test the Vault approle client class"""

    @staticmethod
    @pytest.mark.parametrize(
        "token_file",
        (
            pytest.param("", id="no token file"),
            pytest.param("tests/data/vault_token.key", id="with token file"),
        ),
    )
    def test_init(token_file: str, monkeypatch: MonkeyPatch) -> None:
        """Test the Client __init__"""
        monkeypatch.setattr("fotoobo.helpers.vault.Client.load_token", MagicMock(result=True))
        client = Client(
            url="dummy_url",
            ssl_verify=False,
            namespace="dummy_namespace",
            data_path="dummy_data_path",
            role_id="dummy_role_id",
            secret_id="dummy_secret_id",
            token_file=token_file,
        )
        assert client.url == "dummy_url"
        if token_file:
            assert client.token_file == Path(token_file)

        else:
            assert client.token_file is None

        assert client.token == ""

    @staticmethod
    @pytest.mark.parametrize(
        "token_file, expect",
        (
            pytest.param("tests/data/vault_token.key", "dummy_vault_token", id="valid file"),
            pytest.param("tests/data/invalid_vault_token_file.key", "", id="invalid file"),
        ),
    )
    def test_load_token(token_file: str, expect: str, monkeypatch: MonkeyPatch) -> None:
        """Test the Client load_token"""
        monkeypatch.setattr("fotoobo.helpers.vault.Client.validate_token", MagicMock(result=True))
        client = Client(
            url="dummy_url",
            namespace="dummy_namespace",
            data_path="dummy_data_path",
            role_id="dummy_role_id",
            secret_id="dummy_secret_id",
            token_file=token_file,
        )
        assert client.token == expect

    @staticmethod
    @pytest.mark.parametrize(
        "token, is_file",
        (
            pytest.param("dummy_token", True, id="with token"),
            pytest.param("", False, id="no token"),
        ),
    )
    def test_save_token(token: str, is_file: bool, temp_dir: Path) -> None:
        """Test the Client save_token"""
        token_file: Path = temp_dir / "vault_token.key"
        token_file.unlink(missing_ok=True)
        client = Client(
            url="dummy_url",
            namespace="dummy_namespace",
            data_path="dummy_data_path",
            role_id="dummy_role_id",
            secret_id="dummy_secret_id",
        )
        assert client.token == ""
        client.token = token
        client.token_file = token_file
        assert client.save_token() == is_file
        assert token_file.is_file() == is_file

    @staticmethod
    @pytest.mark.parametrize(
        "response, valid",
        (
            pytest.param(
                ResponseMock(ok=True, json={"data": {"ttl": 60}}),
                True,
                id="valid token",
            ),
            pytest.param(
                ResponseMock(ok=True, json={"data": {"ttl": 30}}),
                False,
                id="valid token but low ttl",
            ),
            pytest.param(
                ResponseMock(ok=False),
                False,
                id="invalid token",
            ),
        ),
    )
    def test_validate_token(response: ResponseMock, valid: bool, monkeypatch: MonkeyPatch) -> None:
        """Test the Client validate_token"""
        monkeypatch.setattr("fotoobo.helpers.vault.requests.get", MagicMock(return_value=response))
        client = Client(
            url="https://dummy_url",
            namespace="dummy_namespace",
            data_path="dummy_data_path",
            role_id="dummy_role_id",
            secret_id="dummy_secret_id",
            token_ttl_limit=42,
        )
        client.token = "dummy_token"
        assert client.validate_token() == valid
        assert bool(client.token) == valid

    @staticmethod
    @pytest.mark.parametrize(
        "mock",
        (
            pytest.param(
                MagicMock(side_effect=requests.exceptions.SSLError("dummy")),
                id="SSLError",
            ),
            pytest.param(
                MagicMock(side_effect=requests.exceptions.ConnectionError("dummy")),
                id="ConnectionError",
            ),
        ),
    )
    def test_validate_token_exception(mock: ResponseMock, monkeypatch: MonkeyPatch) -> None:
        """Test the Client validate_token with exception"""
        monkeypatch.setattr("fotoobo.helpers.vault.requests.get", mock)
        client = Client(
            url="https://dummy_url",
            namespace="dummy_namespace",
            data_path="dummy_data_path",
            role_id="dummy_role_id",
            secret_id="dummy_secret_id",
        )
        client.token = "dummy_token"
        assert client.validate_token() is False
        assert client.token == ""

    @staticmethod
    @pytest.mark.parametrize(
        "response, token",
        (
            pytest.param(
                ResponseMock(ok=True, json={"auth": {"client_token": "dummy_token"}}),
                "dummy_token",
                id="valid approle login",
            ),
            pytest.param(
                ResponseMock(ok=False),
                "",
                id="invalid approle login",
            ),
        ),
    )
    def test_get_token(
        response: ResponseMock, token: str, monkeypatch: MonkeyPatch, temp_dir: Path
    ) -> None:
        """Test the Client get_token"""
        monkeypatch.setattr("fotoobo.helpers.vault.Client.load_token", MagicMock(result=True))
        monkeypatch.setattr("fotoobo.helpers.vault.requests.post", MagicMock(return_value=response))
        token_file: Path = temp_dir / "vault_token.key"
        token_file.unlink(missing_ok=True)
        client = Client(
            url="https://dummy_url",
            namespace="dummy_namespace",
            data_path="dummy_data_path",
            role_id="dummy_role_id",
            secret_id="dummy_secret_id",
            token_file=token_file.as_posix(),
        )
        client.token = "dummy_token"
        assert client.get_token() == bool(token)
        assert client.token == token
        if token:
            assert token_file.is_file()

    @staticmethod
    @pytest.mark.parametrize(
        "mock",
        (
            pytest.param(
                MagicMock(side_effect=requests.exceptions.SSLError("dummy")),
                id="SSLError",
            ),
            pytest.param(
                MagicMock(side_effect=requests.exceptions.ConnectionError("dummy")),
                id="ConnectionError",
            ),
        ),
    )
    def test_get_token_exception(mock: ResponseMock, monkeypatch: MonkeyPatch) -> None:
        """Test the Client get_token with exception"""
        monkeypatch.setattr("fotoobo.helpers.vault.requests.post", mock)
        client = Client(
            url="https://dummy_url",
            namespace="dummy_namespace",
            data_path="dummy_data_path",
            role_id="dummy_role_id",
            secret_id="dummy_secret_id",
        )
        client.token = "dummy_token"
        assert client.get_token() is False
        assert client.token == ""

    @staticmethod
    @pytest.mark.parametrize(
        "response, data",
        (
            pytest.param(
                ResponseMock(
                    ok=True, json={"data": {"data": {"dummy_fgt": {"token": "dummy_token"}}}}
                ),
                {"ok": {"data": {"data": {"dummy_fgt": {"token": "dummy_token"}}}}},
                id="OK",
            ),
            pytest.param(
                ResponseMock(
                    ok=False,
                    status_code=404,
                    reason="Not Found",
                    content=b'{"errors":[]}\n',
                ),
                {
                    "error": {
                        "content": b'{"errors":[]}\n',
                        "reason": "Not Found",
                        "status_code": 404,
                    }
                },
                id="Not Found",
            ),
            pytest.param(
                ResponseMock(
                    ok=False,
                    status_code=403,
                    reason="Forbidden",
                    content=b'{"errors":["1 error occurred:\\n\\t* permission denied\\n\\n"]}\n',
                ),
                {
                    "error": {
                        "content": b'{"errors":["1 error occurred:\\n\\t* permission denied'
                        b'\\n\\n"]}\n',
                        "reason": "Forbidden",
                        "status_code": 403,
                    }
                },
                id="Forbidden",
            ),
        ),
    )
    def test_get_data(
        response: ResponseMock, data: dict[str, Any], monkeypatch: MonkeyPatch
    ) -> None:
        """Test the Client get_data"""
        monkeypatch.setattr("fotoobo.helpers.vault.Client.get_token", MagicMock(return_value=True))
        monkeypatch.setattr("fotoobo.helpers.vault.requests.get", MagicMock(return_value=response))
        client = Client(
            url="https://dummy_url",
            namespace="dummy_namespace",
            data_path="dummy_data_path",
            role_id="dummy_role_id",
            secret_id="dummy_secret_id",
        )
        assert client.get_data() == data

    @staticmethod
    def test_get_data_no_token(monkeypatch: MonkeyPatch) -> None:
        """Test the Client get_data when no token could be retrieved"""
        monkeypatch.setattr("fotoobo.helpers.vault.Client.get_token", MagicMock(return_value=False))
        monkeypatch.setattr(
            "fotoobo.helpers.vault.requests.get", MagicMock(return_value=ResponseMock(ok=True))
        )
        client = Client(
            url="https://dummy_url",
            namespace="dummy_namespace",
            data_path="dummy_data_path",
            role_id="dummy_role_id",
            secret_id="dummy_secret_id",
        )
        with pytest.raises(GeneralError, match=r"Unable to get vault token"):
            client.get_data()
