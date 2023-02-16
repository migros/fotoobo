"""
Test the FortiManager class
"""
# pylint: disable=no-member
from unittest.mock import MagicMock, patch

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import APIError
from fotoobo.fortinet.fortimanager import FortiManager
from tests.helper import ResponseMock


class TestFortiManager:
    """Test the FortiManager class"""

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": [
                        {
                            "data": {"task": 111},
                            "status": {"code": 0, "message": "OK"},
                            "url": "/securityconsole/assign/package",
                        }
                    ]
                },
                status=200,
            )
        ),
    )
    def test_assign_all_objects() -> None:
        """Test assign_all_objects"""
        assert FortiManager("", "", "").assign_all_objects("DUMMY") == 111
        requests.Session.post.assert_called_with(  # type: ignore
            "https:///jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [
                    {
                        "data": {
                            "flags": ["cp_all_objs"],
                            "pkg": "default",
                            "target": [{"adom": "DUMMY", "excluded": "disable"}],
                        },
                        "url": "/securityconsole/assign/package",
                    }
                ],
                "session": "",
            },
            verify=True,
            timeout=3,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(return_value=ResponseMock(json={}, status=404)),
    )
    def test_assign_all_objects_http_404() -> None:
        """Test assign_all_objects with http error 404"""
        with pytest.raises(APIError) as err:
            FortiManager("", "", "").assign_all_objects("DUMMY")
        assert "HTTP/404 Resource Not Found" in str(err.value)
        requests.Session.post.assert_called_with(  # type: ignore
            "https:///jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [
                    {
                        "data": {
                            "flags": ["cp_all_objs"],
                            "pkg": "default",
                            "target": [{"adom": "DUMMY", "excluded": "disable"}],
                        },
                        "url": "/securityconsole/assign/package",
                    }
                ],
                "session": "",
            },
            verify=True,
            timeout=3,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": [
                        {
                            "data": {},
                            "status": {"code": 22, "message": "NOT-OK"},
                            "url": "/securityconsole/assign/package",
                        }
                    ]
                },
                status=200,
            )
        ),
    )
    def test_assign_all_objects_status_not_ok() -> None:
        """Test assign_all_objects with status code != 0"""
        assert FortiManager("", "", "").assign_all_objects("DUMMY") == 0
        requests.Session.post.assert_called_with(  # type: ignore
            "https:///jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [
                    {
                        "data": {
                            "flags": ["cp_all_objs"],
                            "pkg": "default",
                            "target": [{"adom": "DUMMY", "excluded": "disable"}],
                        },
                        "url": "/securityconsole/assign/package",
                    }
                ],
                "session": "",
            },
            verify=True,
            timeout=3,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(json={"result": [{"data": [{"name": "dummy"}]}]}, status=200)
        ),
    )
    def test_get_adoms() -> None:
        """Test fmg get adoms"""
        assert FortiManager("", "", "").get_adoms() == [{"name": "dummy"}]
        requests.Session.post.assert_called_with(  # type:ignore
            "https:///jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/dvmdb/adom"}], "session": ""},
            verify=True,
            timeout=3,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(return_value=ResponseMock(json={}, status=400)),
    )
    def test_get_adoms_http_error() -> None:
        """Test fmg get adoms with a status != 200"""
        with pytest.raises(APIError) as err:
            FortiManager("", "", "").get_adoms()
        assert "HTTP/400 Bad Request" in str(err.value)

    @staticmethod
    @pytest.mark.parametrize(
        "response, expected",
        (
            pytest.param({"result": [{"data": {"Version": "v1.1.1-xyz"}}]}, "v1.1.1", id="ok"),
            pytest.param({"result": [{"data": {"Version": "dummy"}}]}, "", id="dummy"),
            pytest.param({"result": [{"data": {"Version": ""}}]}, "", id="empty version field"),
            pytest.param({"result": [{"data": {}}]}, "", id="empty data"),
            pytest.param({"result": []}, "", id="empty result"),
            pytest.param({}, "", id="empty return_value"),
        ),
    )
    def test_get_version(response: MagicMock, expected: str, monkeypatch: MonkeyPatch) -> None:
        """Test FortiManager get version"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(return_value=ResponseMock(json=response, status=200)),
        )
        assert FortiManager("", "", "").get_version() == expected
        requests.Session.post.assert_called_with(  # type: ignore
            "https:///jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/sys/status"}], "session": ""},
            verify=True,
            timeout=3,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "id": 1,
                    "result": [{"status": {"code": 0, "message": "OK"}, "url": "/sys/login/user"}],
                    "session": "dummy_session",
                },
                status=200,
            )
        ),
    )
    def test_login() -> None:
        """Test the login to a fortimanager"""
        fmg = FortiManager("host", "user", "pass")
        assert fmg.login() == 200
        requests.Session.post.assert_called_with(  # type: ignore
            "https://host/jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [{"data": {"passwd": "pass", "user": "user"}, "url": "/sys/login/user"}],
                "session": "",
            },
            verify=True,
            timeout=3,
        )

    @staticmethod
    @patch("fotoobo.fortinet.fortimanager.FortiManager.login", MagicMock(return_value=200))
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "method": "exec",
                    "params": [{"url": "/sys/logout"}],
                    "session": "dummy_session",
                },
                status=200,
            )
        ),
    )
    def test_logout() -> None:
        """Test the logout of a fortimanager"""
        fortimanager = FortiManager("host", "user", "pass")
        assert fortimanager.logout() == 200
        requests.Session.post.assert_called_with(  # type: ignore
            "https://host/jsonrpc",
            headers=None,
            json={"method": "exec", "params": [{"url": "/sys/logout"}], "session": ""},
            verify=True,
            timeout=3,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(json={"result": [{"status": {"code": 0}}]}, status=200)
        ),
    )
    def test_set_single() -> None:
        """Test fmg set with a single dict"""
        assert FortiManager("", "", "").set("ADOM", {"params": [{"url": "{adom}"}]}) == 0
        requests.Session.post.assert_called_with(  # type:ignore
            "https:///jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            verify=True,
            timeout=10,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(json={"result": [{"status": {"code": 0}}]}, status=200)
        ),
    )
    def test_set_multiple() -> None:
        """Test fmg set with a list of dicts"""
        assert FortiManager("", "", "").set("ADOM", [{"params": [{"url": "{adom}"}]}]) == 0
        requests.Session.post.assert_called_with(  # type:ignore
            "https:///jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            verify=True,
            timeout=10,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(json={"result": [{"status": {"code": 0}}]}, status=200)
        ),
    )
    def test_set_single_global() -> None:
        """Test fmg set with a single dict"""
        assert FortiManager("", "", "").set("global", {"params": [{"url": "{adom}"}]}) == 0
        requests.Session.post.assert_called_with(  # type:ignore
            "https:///jsonrpc",
            headers=None,
            json={"params": [{"url": "global"}], "session": ""},
            verify=True,
            timeout=10,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={"result": [{"status": {"code": 444, "message": "dummy"}, "url": "dummy"}]},
                status=200,
            )
        ),
    )
    def test_set_response_error() -> None:
        """Test fmg set with en error in the response"""
        assert FortiManager("", "", "").set("ADOM", [{"params": [{"url": "{adom}"}]}]) == 1
        requests.Session.post.assert_called_with(  # type:ignore
            "https:///jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            verify=True,
            timeout=10,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(return_value=ResponseMock(json={}, status=444)),
    )
    def test_set_http_error() -> None:
        """Test fmg set with an error in the response"""
        with pytest.raises(APIError) as err:
            FortiManager("", "", "").set("ADOM", [{"params": [{"url": "{adom}"}]}])
        assert "HTTP/444 general API Error" in str(err.value)
        requests.Session.post.assert_called_with(  # type:ignore
            "https:///jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            verify=True,
            timeout=10,
        )

    @staticmethod
    @patch(
        "fotoobo.fortinet.fortinet.requests.Session.post",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": [
                        {
                            "data": [
                                {
                                    "history": [
                                        {"detail": "detail 1", "percent": 10},
                                        {"detail": "detail 2", "percent": 20},
                                    ],
                                    "state": 4,
                                    "percent": 100,
                                    "detail": "main detail",
                                    "task_id": 222,
                                },
                            ],
                            "status": {"code": 0, "message": "OK"},
                            "url": "/task/task/222/line",
                        }
                    ]
                },
                status=200,
            )
        ),
    )
    def test_wait_for_task() -> None:
        """Test wait_for_task"""
        messages = FortiManager("", "", "").wait_for_task(222, 0)
        assert isinstance(messages, list)
        assert messages[0]["task_id"] == 222
        requests.Session.post.assert_called_with(  # type: ignore
            "https:///jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/task/task/222/line"}], "session": ""},
            verify=True,
            timeout=3,
        )
