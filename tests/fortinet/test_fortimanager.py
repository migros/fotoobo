"""
Test the FortiManager class
"""

# pylint: disable=no-member, too-many-lines
# mypy: disable-error-code=attr-defined
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import APIError
from fotoobo.fortinet.fortimanager import FortiManager
from tests.helper import ResponseMock


class TestFortiManager:  # pylint: disable=too-many-public-methods
    """Test the FortiManager class"""

    @staticmethod
    @pytest.fixture
    def response_mock_api_ok() -> MagicMock:
        """Fixture to return a mocked response for API ok"""
        return MagicMock(
            return_value=ResponseMock(
                json={"result": [{"data": {}, "status": {"code": 0, "message": "OK"}}]},
                status_code=200,
            )
        )

    @staticmethod
    @pytest.fixture
    def api_delete_ok(response_mock_api_ok: MagicMock, monkeypatch: MonkeyPatch) -> None:
        """Fixture to patch the FortiManager.api_delete() method"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.api_delete", response_mock_api_ok
        )

    @staticmethod
    @pytest.fixture
    def api_get_ok(response_mock_api_ok: MagicMock, monkeypatch: MonkeyPatch) -> None:
        """Fixture to patch the FortiManager.api_get() method"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.api_get", response_mock_api_ok
        )

    @staticmethod
    def test_api_delete(monkeypatch: MonkeyPatch) -> None:
        """Test api_delete"""
        url: str = "/pm/config/adom/dummy/obj/firewall/address/dummy"
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "result": [
                            {
                                "status": {"code": 0, "message": "OK"},
                                "url": url,
                            }
                        ]
                    },
                    status_code=200,
                )
            ),
        )
        fmg = FortiManager("host", "", "")
        assert fmg.api_delete(url).json()["result"][0]["status"]["code"] == 0
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"method": "delete", "params": [{"url": url}], "session": ""},
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "with_params",
        (
            pytest.param(False, id="without params"),
            pytest.param(True, id="with params"),
        ),
    )
    def test_api_get(with_params: bool, monkeypatch: MonkeyPatch) -> None:
        """test api_get"""
        url: str = "/pm/config/global/obj/firewall/address/dummy"
        params = {"option": ["scope member"]}
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "result": [
                            {
                                "data": {
                                    "name": "dummy",
                                    "uuid": "88888888-4444-4444-4444-121212121212",
                                },
                                "status": {"code": 0, "message": "OK"},
                                "url": url,
                            }
                        ]
                    },
                    status_code=200,
                )
            ),
        )
        fmg = FortiManager("host", "", "")
        expected_call = (
            ["https://host:443/jsonrpc"],
            {
                "headers": None,
                "json": {
                    "method": "get",
                    "params": [
                        {
                            "url": "/pm/config/global/obj/firewall/address/dummy",
                        }
                    ],
                    "session": "",
                },
                "params": None,
                "timeout": 3,
                "verify": True,
            },
        )
        if with_params:
            assert fmg.api_get(url, params).json()["result"][0]["status"]["code"] == 0
            expected_call[1]["json"]["params"][0] = {  # type: ignore
                **expected_call[1]["json"]["params"][0],  # type: ignore
                **{"option": ["scope member"]},
            }
            requests.Session.post.assert_called_with(
                *expected_call[0],
                **expected_call[1],
            )

        else:
            assert fmg.api_get(url).json()["result"][0]["status"]["code"] == 0
            requests.Session.post.assert_called_with(*expected_call[0], **expected_call[1])

    @staticmethod
    def test_assign_all_objects(monkeypatch: MonkeyPatch) -> None:
        """Test assign_all_objects"""
        monkeypatch.setattr(
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
                    status_code=200,
                )
            ),
        )
        assert FortiManager("host", "", "").assign_all_objects("dummy_adom", "dummy_policy") == 111
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [
                    {
                        "data": {
                            "flags": ["cp_all_objs"],
                            "pkg": "dummy_policy",
                            "target": [{"adom": "dummy_adom", "excluded": "disable"}],
                        },
                        "url": "/securityconsole/assign/package",
                    }
                ],
                "session": "",
            },
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_assign_all_objects_http_404(monkeypatch: MonkeyPatch) -> None:
        """Test assign_all_objects with http error 404"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(return_value=ResponseMock(json={}, status_code=404)),
        )
        with pytest.raises(APIError) as err:
            FortiManager("host", "", "").assign_all_objects("dummy_adom", "dummy_policy")

        assert "HTTP/404 Resource Not Found" in str(err.value)
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [
                    {
                        "data": {
                            "flags": ["cp_all_objs"],
                            "pkg": "dummy_policy",
                            "target": [{"adom": "dummy_adom", "excluded": "disable"}],
                        },
                        "url": "/securityconsole/assign/package",
                    }
                ],
                "session": "",
            },
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_assign_all_objects_status_not_ok(monkeypatch: MonkeyPatch) -> None:
        """Test assign_all_objects with status code != 0"""
        monkeypatch.setattr(
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
                    status_code=200,
                )
            ),
        )
        assert FortiManager("host", "", "").assign_all_objects("adom1,adom2", "policy1") == 0
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [
                    {
                        "data": {
                            "flags": ["cp_all_objs"],
                            "pkg": "policy1",
                            "target": [
                                {"adom": "adom1", "excluded": "disable"},
                                {"adom": "adom2", "excluded": "disable"},
                            ],
                        },
                        "url": "/securityconsole/assign/package",
                    }
                ],
                "session": "",
            },
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_address() -> None:
        """Test fmg delete_adom_address"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_adom_address("dummy", "dummy")["status"]["code"] == 0
        FortiManager.api_delete.assert_called_with(
            "/pm/config/adom/dummy/obj/firewall/address/dummy"
        )

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_address_dry() -> None:
        """Test fmg delete_adom_address with dry-run"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_adom_address("dummy", "dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_address_group() -> None:
        """Test fmg delete_adom_address_group"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_adom_address_group("dummy", "dummy")["status"]["code"] == 0
        FortiManager.api_delete.assert_called_with(
            "/pm/config/adom/dummy/obj/firewall/addrgrp/dummy"
        )

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_address_group_dry() -> None:
        """Test fmg delete_adom_address_group with dry-run"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_adom_address_group("dummy", "dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_service() -> None:
        """Test fmg delete_adom_service"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_adom_service("dummy", "dummy")["status"]["code"] == 0
        FortiManager.api_delete.assert_called_with(
            "/pm/config/adom/dummy/obj/firewall/service/custom/dummy"
        )

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_service_dry() -> None:
        """Test fmg delete_adom_service with dry-run"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_adom_service("dummy", "dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_service_group() -> None:
        """Test fmg delete_adom_service_group"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_adom_service_group("dummy", "dummy")["status"]["code"] == 0
        FortiManager.api_delete.assert_called_with(
            "/pm/config/adom/dummy/obj/firewall/service/group/dummy"
        )

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_service_group_dry() -> None:
        """Test fmg delete_adom_service_group with dry-run"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_adom_service_group("dummy", "dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    @pytest.mark.parametrize(
        "get_global_address_data",
        (
            pytest.param({"scope member": [{"name": "ADOM"}]}, id="with scope member"),
            pytest.param({}, id="without scope member"),
        ),
    )
    @pytest.mark.parametrize(
        "get_global_address_status",
        (
            pytest.param({"code": 0, "message": "OK"}, id="status OK"),
            pytest.param({"code": 7, "message": "dummy"}, id="status dummy"),
        ),
    )
    @pytest.mark.parametrize(
        "delete_adom_address_status",
        (
            pytest.param({"code": 0, "message": "OK"}, id="status OK"),
            pytest.param({"code": 7, "message": "dummy"}, id="status dummy"),
        ),
    )
    def test_delete_global_address(
        get_global_address_data: dict[str, Any],
        get_global_address_status: dict[str, Any],
        delete_adom_address_status: dict[str, Any],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test fmg delete_global_address"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.get_global_address",
            MagicMock(
                return_value={
                    "data": get_global_address_data,
                    "status": get_global_address_status,
                }
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.delete_adom_address",
            MagicMock(return_value={"status": delete_adom_address_status}),
        )
        fmg = FortiManager("host", "", "")
        assert fmg.delete_global_address("dummy")["status"]["code"] in [0, 7]

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok", "api_delete_ok")
    def test_delete_global_address_dry() -> None:
        """Test fmg delete_global_address with dry-run"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_global_address("dummy", dry=True) == {}
        # FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    @pytest.mark.parametrize(
        "get_global_address_group_data",
        (
            pytest.param({"scope member": [{"name": "ADOM"}]}, id="with scope member"),
            pytest.param({}, id="without scope member"),
        ),
    )
    @pytest.mark.parametrize(
        "get_global_address_group_status",
        (
            pytest.param({"code": 0, "message": "OK"}, id="status OK"),
            pytest.param({"code": 7, "message": "dummy"}, id="status dummy"),
        ),
    )
    @pytest.mark.parametrize(
        "delete_adom_address_group_status",
        (
            pytest.param({"code": 0, "message": "OK"}, id="status OK"),
            pytest.param({"code": 7, "message": "dummy"}, id="status dummy"),
        ),
    )
    def test_delete_global_address_group(
        get_global_address_group_data: dict[str, Any],
        get_global_address_group_status: dict[str, Any],
        delete_adom_address_group_status: dict[str, Any],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test fmg delete_global_address_group"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.get_global_address_group",
            MagicMock(
                return_value={
                    "data": get_global_address_group_data,
                    "status": get_global_address_group_status,
                }
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.delete_adom_address_group",
            MagicMock(return_value={"status": delete_adom_address_group_status}),
        )
        fmg = FortiManager("host", "", "")
        assert fmg.delete_global_address_group("dummy")["status"]["code"] in [0, 7]

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok", "api_delete_ok")
    def test_delete_global_address_group_dry() -> None:
        """Test fmg delete_global_address_group with dry-run"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_global_address_group("dummy", dry=True) == {}
        # FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    @pytest.mark.parametrize(
        "get_global_service_data",
        (
            pytest.param({"scope member": [{"name": "ADOM"}]}, id="with scope member"),
            pytest.param({}, id="without scope member"),
        ),
    )
    @pytest.mark.parametrize(
        "get_global_service_status",
        (
            pytest.param({"code": 0, "message": "OK"}, id="status OK"),
            pytest.param({"code": 7, "message": "dummy"}, id="status dummy"),
        ),
    )
    @pytest.mark.parametrize(
        "delete_adom_service_status",
        (
            pytest.param({"code": 0, "message": "OK"}, id="status OK"),
            pytest.param({"code": 7, "message": "dummy"}, id="status dummy"),
        ),
    )
    def test_delete_global_service(
        get_global_service_data: dict[str, Any],
        get_global_service_status: dict[str, Any],
        delete_adom_service_status: dict[str, Any],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test fmg delete_global_service"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.get_global_service",
            MagicMock(
                return_value={
                    "data": get_global_service_data,
                    "status": get_global_service_status,
                }
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.delete_adom_service",
            MagicMock(return_value={"status": delete_adom_service_status}),
        )
        fmg = FortiManager("host", "", "")
        assert fmg.delete_global_service("dummy")["status"]["code"] in [0, 7]

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok", "api_delete_ok")
    def test_delete_global_service_dry() -> None:
        """Test fmg delete_global_service with dry-run"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_global_service("dummy", dry=True) == {}
        # FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    @pytest.mark.parametrize(
        "get_global_service_group_data",
        (
            pytest.param({"scope member": [{"name": "ADOM"}]}, id="with scope member"),
            pytest.param({}, id="without scope member"),
        ),
    )
    @pytest.mark.parametrize(
        "get_global_service_group_status",
        (
            pytest.param({"code": 0, "message": "OK"}, id="status OK"),
            pytest.param({"code": 7, "message": "dummy"}, id="status dummy"),
        ),
    )
    @pytest.mark.parametrize(
        "delete_adom_service_group_status",
        (
            pytest.param({"code": 0, "message": "OK"}, id="status OK"),
            pytest.param({"code": 7, "message": "dummy"}, id="status dummy"),
        ),
    )
    def test_delete_global_service_group(
        get_global_service_group_data: dict[str, Any],
        get_global_service_group_status: dict[str, Any],
        delete_adom_service_group_status: dict[str, Any],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test fmg delete_global_service_group"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.get_global_service_group",
            MagicMock(
                return_value={
                    "data": get_global_service_group_data,
                    "status": get_global_service_group_status,
                }
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.delete_adom_service_group",
            MagicMock(return_value={"status": delete_adom_service_group_status}),
        )
        fmg = FortiManager("host", "", "")
        assert fmg.delete_global_service_group("dummy")["status"]["code"] in [0, 7]

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok", "api_delete_ok")
    def test_delete_global_service_group_dry() -> None:
        """Test fmg delete_global_service_group with dry-run"""
        fmg = FortiManager("host", "", "")
        assert fmg.delete_global_service_group("dummy", dry=True) == {}
        # FortiManager.api_delete.assert_not_called()

    @staticmethod
    def test_get_adoms(monkeypatch: MonkeyPatch) -> None:
        """Test fmg get adoms"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={"result": [{"data": [{"name": "dummy"}]}]}, status_code=200
                )
            ),
        )
        assert FortiManager("host", "", "").get_adoms() == [{"name": "dummy"}]
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/dvmdb/adom"}], "session": ""},
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_get_adoms_http_error(monkeypatch: MonkeyPatch) -> None:
        """Test fmg get adoms with a status != 200"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(return_value=ResponseMock(json={}, status_code=400)),
        )
        with pytest.raises(APIError) as err:
            FortiManager("", "", "").get_adoms()
        assert "HTTP/400 Bad Request" in str(err.value)

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    @pytest.mark.parametrize(
        "scope_member",
        (
            pytest.param(True, id="with scope member"),
            pytest.param(False, id="without scope member"),
        ),
    )
    def test_get_global_address(scope_member: bool) -> None:
        """Test fmg get_global_address"""
        fmg = FortiManager("host", "", "")
        assert fmg.get_global_address("dummy", scope_member=scope_member)["status"]["code"] == 0
        expected_call: list[Any] = ["/pm/config/global/obj/firewall/address/dummy"]
        if scope_member:
            expected_call.append({"option": ["scope member"]})

        FortiManager.api_get.assert_called_with(*expected_call)

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    def test_get_global_addresses() -> None:
        """Test fmg get_global_addresses"""
        assert FortiManager("host", "", "").get_global_addresses()["status"]["code"] == 0
        FortiManager.api_get.assert_called_with(
            "/pm/config/global/obj/firewall/address", timeout=10
        )

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    @pytest.mark.parametrize(
        "scope_member",
        (
            pytest.param(True, id="with scope member"),
            pytest.param(False, id="without scope member"),
        ),
    )
    def test_get_global_address_group(scope_member: bool) -> None:
        """Test fmg get_global_address_group"""
        fmg = FortiManager("host", "", "")
        assert (
            fmg.get_global_address_group("dummy", scope_member=scope_member)["status"]["code"] == 0
        )
        expected_call: list[Any] = ["/pm/config/global/obj/firewall/addrgrp/dummy"]
        if scope_member:
            expected_call.append({"option": ["scope member"]})
        FortiManager.api_get.assert_called_with(*expected_call)

        # assert fmg.get_global_address_group("dummy")["status"]["code"] == 0
        # FortiManager.api_get.assert_called_with("/pm/config/global/obj/firewall/addrgrp/dummy")

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    def test_get_global_address_groups() -> None:
        """Test fmg get_global_address_groups"""
        assert FortiManager("host", "", "").get_global_address_groups()["status"]["code"] == 0
        FortiManager.api_get.assert_called_with(
            "/pm/config/global/obj/firewall/addrgrp", timeout=10
        )

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    @pytest.mark.parametrize(
        "scope_member",
        (
            pytest.param(True, id="with scope member"),
            pytest.param(False, id="without scope member"),
        ),
    )
    def test_get_global_service(scope_member: bool) -> None:
        """Test fmg get_global_service"""
        fmg = FortiManager("host", "", "")
        assert fmg.get_global_service("dummy", scope_member=scope_member)["status"]["code"] == 0
        expected_call: list[Any] = ["/pm/config/global/obj/firewall/service/custom/dummy"]
        if scope_member:
            expected_call.append({"option": ["scope member"]})
        FortiManager.api_get.assert_called_with(*expected_call)

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    def test_get_global_services() -> None:
        """Test fmg get_global_services"""
        assert FortiManager("host", "", "").get_global_services()["status"]["code"] == 0
        FortiManager.api_get.assert_called_with(
            "/pm/config/global/obj/firewall/service/custom", timeout=10
        )

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    @pytest.mark.parametrize(
        "scope_member",
        (
            pytest.param(True, id="with scope member"),
            pytest.param(False, id="without scope member"),
        ),
    )
    def test_get_global_service_group(scope_member: bool) -> None:
        """Test fmg get_global_service_group"""
        fmg = FortiManager("host", "", "")
        assert (
            fmg.get_global_service_group("dummy", scope_member=scope_member)["status"]["code"] == 0
        )
        expected_call: list[Any] = ["/pm/config/global/obj/firewall/service/group/dummy"]
        if scope_member:
            expected_call.append({"option": ["scope member"]})
        FortiManager.api_get.assert_called_with(*expected_call)

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    def test_get_global_service_groups() -> None:
        """Test fmg get_global_service_groups"""
        assert FortiManager("host", "", "").get_global_service_groups()["status"]["code"] == 0
        FortiManager.api_get.assert_called_with(
            "/pm/config/global/obj/firewall/service/group", timeout=10
        )

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
            MagicMock(return_value=ResponseMock(json=response, status_code=200)),
        )
        assert FortiManager("host", "", "").get_version() == expected
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/sys/status"}], "session": ""},
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_login(monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiManager"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "id": 1,
                        "result": [
                            {"status": {"code": 0, "message": "OK"}, "url": "/sys/login/user"}
                        ],
                        "session": "dummy_session_key",
                    },
                    status_code=200,
                )
            ),
        )
        fmg = FortiManager("host", "user", "pass")
        assert fmg.login() == 200
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [{"data": {"passwd": "pass", "user": "user"}, "url": "/sys/login/user"}],
            },
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_login_with_session_path(monkeypatch: MonkeyPatch) -> None:
        """Test the login to a FortiManager when a session_path is given"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "id": 1,
                        "result": [
                            {
                                "status": {"code": 0, "message": "dummy"},
                                "url": "/sys/status",
                            }
                        ],
                        "session": "dummy_session_key",
                    },
                    status_code=200,
                )
            ),
        )
        fmg = FortiManager("host", "user", "pass")
        fmg.hostname = "test_fmg"
        fmg.session_path = "tests/data"
        assert fmg.login() == 200
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={
                "method": "get",
                "params": [{"url": "/sys/status"}],
                "session": "dummy_session_key",
            },
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_login_with_session_path_invalid_key(monkeypatch: MonkeyPatch) -> None:
        """
        Test the login to a FortiManager when a session_path is given but the session key is invalid
        """
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "id": 1,
                        "result": [
                            {
                                "status": {"code": -11, "message": "dummy"},
                                "url": "/sys/status",
                            }
                        ],
                        "session": "dummy_session_key",
                    },
                    status_code=200,
                )
            ),
        )
        fmg = FortiManager("host", "user", "pass")
        fmg.hostname = "test_fmg"
        fmg.session_path = "tests/data"
        assert fmg.login() == 200
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [{"data": {"passwd": "pass", "user": "user"}, "url": "/sys/login/user"}],
            },
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_login_with_session_path_not_found(temp_dir: str, monkeypatch: MonkeyPatch) -> None:
        """
        Test the login to a FortiManager when a session_path is given but the session key is invalid
        """
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "id": 1,
                        "result": [
                            {
                                "status": {"code": 0, "message": "dummy"},
                                "url": "/sys/status",
                            }
                        ],
                        "session": "dummy_session_key",
                    },
                    status_code=200,
                )
            ),
        )
        fmg = FortiManager("host", "user", "pass")
        fmg.hostname = "test_fmg_dummy"
        fmg.session_path = temp_dir
        assert fmg.login() == 200
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [{"data": {"passwd": "pass", "user": "user"}, "url": "/sys/login/user"}],
            },
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_logout(monkeypatch: MonkeyPatch) -> None:
        """Test the logout of a FortiManager"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "method": "exec",
                        "params": [{"url": "/sys/logout"}],
                        "session": "dummy_session_key",
                    },
                    status_code=200,
                )
            ),
        )
        fortimanager = FortiManager("host", "user", "pass")
        assert fortimanager.logout() == 200
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={
                "method": "exec",
                "params": [{"url": "/sys/logout"}],
                "session": "dummy_session_key",
            },
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_post_single(monkeypatch: MonkeyPatch) -> None:
        """Test fmg post with a single dict"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={"result": [{"status": {"code": 0}}]}, status_code=200
                )
            ),
        )
        assert not FortiManager("host", "", "").post("ADOM", {"params": [{"url": "{adom}"}]})
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_post_multiple(monkeypatch: MonkeyPatch) -> None:
        """Test fmg post with a list of dicts"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={"result": [{"status": {"code": 0}}]}, status_code=200
                )
            ),
        )
        assert not FortiManager("host", "", "").post("ADOM", [{"params": [{"url": "{adom}"}]}])
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_post_single_global(monkeypatch: MonkeyPatch) -> None:
        """Test fmg post with a single dict"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={"result": [{"status": {"code": 0}}]}, status_code=200
                )
            ),
        )
        assert not FortiManager("host", "", "").post("global", {"params": [{"url": "{adom}"}]})
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "global"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_post_response_error(monkeypatch: MonkeyPatch) -> None:
        """Test post set with en error in the response"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(
                return_value=ResponseMock(
                    json={
                        "result": [{"status": {"code": 444, "message": "dummy"}, "url": "dummy"}]
                    },
                    status_code=200,
                )
            ),
        )
        assert FortiManager("host", "", "").post("ADOM", [{"params": [{"url": "{adom}"}]}]) == [
            "dummy: dummy (code: 444)"
        ]
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_post_http_error(monkeypatch: MonkeyPatch) -> None:
        """Test fmg post with an error in the response"""
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            MagicMock(return_value=ResponseMock(json={}, status_code=444)),
        )
        with pytest.raises(APIError) as err:
            FortiManager("host", "", "").post("ADOM", [{"params": [{"url": "{adom}"}]}])
        assert "HTTP/444 general API Error" in str(err.value)
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_wait_for_task(monkeypatch: MonkeyPatch) -> None:
        """Test wait_for_task"""
        monkeypatch.setattr(
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
                    status_code=200,
                )
            ),
        )
        messages = FortiManager("host", "", "").wait_for_task(222, 0)
        assert isinstance(messages, list)
        assert messages[0]["task_id"] == 222
        requests.Session.post.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/task/task/222/line"}], "session": ""},
            params=None,
            timeout=3,
            verify=True,
        )
