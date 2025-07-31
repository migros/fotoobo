"""
Test the FortiManager class.
"""

# pylint: disable=no-member, too-many-lines
# mypy: disable-error-code=attr-defined

from typing import Any
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from fotoobo.exceptions import APIError
from fotoobo.fortinet.fortimanager import FortiManager
from tests.helper import ResponseMock


class TestFortiManager:
    """
    Test the FortiManager class.
    """

    # pylint: disable=too-many-public-methods

    @staticmethod
    def _response_mock_api_ok() -> Mock:
        """
        Fixture to return a mocked response for API ok.
        """

        return Mock(
            return_value=ResponseMock(
                json={"result": [{"data": {}, "status": {"code": 0, "message": "OK"}}]},
                status_code=200,
            )
        )

    @staticmethod
    @pytest.fixture
    def api_delete_ok(monkeypatch: MonkeyPatch) -> None:
        """
        Fixture to patch the FortiManager.api_delete() method.
        """

        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.api_delete",
            TestFortiManager._response_mock_api_ok(),
        )

    @staticmethod
    @pytest.fixture
    def api_get_ok(monkeypatch: MonkeyPatch) -> None:
        """
        Fixture to patch the FortiManager.api_get() method.
        """

        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.api_get",
            TestFortiManager._response_mock_api_ok(),
        )

    @staticmethod
    def test_api_delete(monkeypatch: MonkeyPatch) -> None:
        """
        Test api_delete.
        """

        # Arrange
        url: str = "/pm/config/adom/dummy/obj/firewall/address/dummy"
        post_mock = Mock(
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
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.api_delete(url).json()["result"][0]["status"]["code"] == 0
        post_mock.assert_called_with(
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
        """
        Test api_get method.
        """

        # Arrange
        url: str = "/pm/config/global/obj/firewall/address/dummy"
        params = {"option": ["scope member"]}
        post_mock = Mock(
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
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)
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

        # Act & Assert
        if with_params:
            assert fmg.api_get(url, params).json()["result"][0]["status"]["code"] == 0
            expected_call[1]["json"]["params"][0] = {  # type: ignore
                **expected_call[1]["json"]["params"][0],  # type: ignore
                **{"option": ["scope member"]},
            }
            post_mock.assert_called_with(
                *expected_call[0],
                **expected_call[1],
            )

        else:
            assert fmg.api_get(url).json()["result"][0]["status"]["code"] == 0
            post_mock.assert_called_with(*expected_call[0], **expected_call[1])

    @staticmethod
    def test_assign_all_objects(monkeypatch: MonkeyPatch) -> None:
        """
        Test assign_all_objects.
        """

        # Arrange
        post_mock = Mock(
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
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        assert FortiManager("host", "", "").assign_all_objects("dummy_adom", "dummy_policy") == 111
        post_mock.assert_called_with(
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
        """
        Test assign_all_objects with http error 404.
        """

        # Arrange
        post_mock = Mock(return_value=ResponseMock(json={}, status_code=404))
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        with pytest.raises(APIError) as err:
            FortiManager("host", "", "").assign_all_objects("dummy_adom", "dummy_policy")

        assert "HTTP/404 Resource Not Found" in str(err.value)
        post_mock.assert_called_with(
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
        """
        Test assign_all_objects with status code != 0.
        """

        # Arrange
        post_mock = Mock(
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
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        assert FortiManager("host", "", "").assign_all_objects("adom1,adom2", "policy1") == 0
        post_mock.assert_called_with(
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
        """
        Test fmg delete_adom_address.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_adom_address("dummy", "dummy")["status"]["code"] == 0
        FortiManager.api_delete.assert_called_with(
            "/pm/config/adom/dummy/obj/firewall/address/dummy"
        )

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_address_dry() -> None:
        """
        Test fmg delete_adom_address with dry-run.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_adom_address("dummy", "dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_address_group() -> None:
        """
        Test fmg delete_adom_address_group.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_adom_address_group("dummy", "dummy")["status"]["code"] == 0
        FortiManager.api_delete.assert_called_with(
            "/pm/config/adom/dummy/obj/firewall/addrgrp/dummy"
        )

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_address_group_dry() -> None:
        """
        Test fmg delete_adom_address_group with dry-run.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_adom_address_group("dummy", "dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_service() -> None:
        """
        Test fmg delete_adom_service.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_adom_service("dummy", "dummy")["status"]["code"] == 0
        FortiManager.api_delete.assert_called_with(
            "/pm/config/adom/dummy/obj/firewall/service/custom/dummy"
        )

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_service_dry() -> None:
        """
        Test fmg delete_adom_service with dry-run.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_adom_service("dummy", "dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_service_group() -> None:
        """
        Test fmg delete_adom_service_group.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_adom_service_group("dummy", "dummy")["status"]["code"] == 0
        FortiManager.api_delete.assert_called_with(
            "/pm/config/adom/dummy/obj/firewall/service/group/dummy"
        )

    @staticmethod
    @pytest.mark.usefixtures("api_delete_ok")
    def test_delete_adom_service_group_dry() -> None:
        """
        Test fmg delete_adom_service_group with dry-run.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
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
        """
        Test fmg delete_global_address.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.get_global_address",
            Mock(
                return_value={
                    "data": get_global_address_data,
                    "status": get_global_address_status,
                }
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.delete_adom_address",
            Mock(return_value={"status": delete_adom_address_status}),
        )
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_global_address("dummy")["status"]["code"] in [0, 7, 601]

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok", "api_delete_ok")
    def test_delete_global_address_dry() -> None:
        """
        Test fmg delete_global_address with dry-run.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_global_address("dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

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
        """
        Test fmg delete_global_address_group.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.get_global_address_group",
            Mock(
                return_value={
                    "data": get_global_address_group_data,
                    "status": get_global_address_group_status,
                }
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.delete_adom_address_group",
            Mock(return_value={"status": delete_adom_address_group_status}),
        )
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_global_address_group("dummy")["status"]["code"] in [0, 7, 601]

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok", "api_delete_ok")
    def test_delete_global_address_group_dry() -> None:
        """
        Test fmg delete_global_address_group with dry-run.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_global_address_group("dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

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
        """
        Test fmg delete_global_service.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.get_global_service",
            Mock(
                return_value={
                    "data": get_global_service_data,
                    "status": get_global_service_status,
                }
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.delete_adom_service",
            Mock(return_value={"status": delete_adom_service_status}),
        )
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_global_service("dummy")["status"]["code"] in [0, 7, 601]

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok", "api_delete_ok")
    def test_delete_global_service_dry() -> None:
        """
        Test fmg delete_global_service with dry-run.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_global_service("dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

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
        """
        Test fmg delete_global_service_group.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.get_global_service_group",
            Mock(
                return_value={
                    "data": get_global_service_group_data,
                    "status": get_global_service_group_status,
                }
            ),
        )
        monkeypatch.setattr(
            "fotoobo.fortinet.fortimanager.FortiManager.delete_adom_service_group",
            Mock(return_value={"status": delete_adom_service_group_status}),
        )
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_global_service_group("dummy")["status"]["code"] in [0, 7, 601]

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok", "api_delete_ok")
    def test_delete_global_service_group_dry() -> None:
        """
        Test fmg delete_global_service_group with dry-run.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.delete_global_service_group("dummy", dry=True) == {}
        FortiManager.api_delete.assert_not_called()

    @staticmethod
    def test_get_adoms(monkeypatch: MonkeyPatch) -> None:
        """
        Test fmg get adoms.
        """

        # Arrange
        post_mock = Mock(
            return_value=ResponseMock(
                json={"result": [{"data": [{"name": "dummy"}]}]}, status_code=200
            )
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        assert FortiManager("host", "", "").get_adoms() == [{"name": "dummy"}]
        post_mock.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/dvmdb/adom"}], "session": ""},
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_get_adoms_http_error(monkeypatch: MonkeyPatch) -> None:
        """
        Test fmg get adoms with a status != 200.
        """

        # Arrange
        monkeypatch.setattr(
            "fotoobo.fortinet.fortinet.requests.Session.post",
            Mock(return_value=ResponseMock(json={}, status_code=400)),
        )

        # Act & Assert
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
        """
        Test fmg get_global_address.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.get_global_address("dummy", scope_member=scope_member)["status"]["code"] == 0
        expected_call: list[Any] = ["/pm/config/global/obj/firewall/address/dummy"]
        if scope_member:
            expected_call.append({"option": ["scope member"]})

        FortiManager.api_get.assert_called_with(*expected_call)

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    def test_get_global_addresses() -> None:
        """
        Test fmg get_global_addresses.
        """

        # Arrange & Act & Assert
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
        """
        Test fmg get_global_address_group.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
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
        """
        Test fmg get_global_address_groups.
        """

        # Arrange & Act & Assert
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
        """
        Test fmg get_global_service.
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
        assert fmg.get_global_service("dummy", scope_member=scope_member)["status"]["code"] == 0
        expected_call: list[Any] = ["/pm/config/global/obj/firewall/service/custom/dummy"]
        if scope_member:
            expected_call.append({"option": ["scope member"]})

        FortiManager.api_get.assert_called_with(*expected_call)

    @staticmethod
    @pytest.mark.usefixtures("api_get_ok")
    def test_get_global_services() -> None:
        """
        Test fmg get_global_services.
        """

        # Arrange & Act & Assert
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
        """
        Test fmg get_global_service_group
        """

        # Arrange
        fmg = FortiManager("host", "", "")

        # Act & Assert
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
        """
        Test fmg get_global_service_groups.
        """

        # Arrange & Act & Assert
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
    def test_get_version(response: Mock, expected: str, monkeypatch: MonkeyPatch) -> None:
        """
        Test FortiManager get version.
        """

        # Arrange
        post_mock = Mock(return_value=ResponseMock(json=response, status_code=200))
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        assert FortiManager("host", "", "").get_version() == expected
        post_mock.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/sys/status"}], "session": ""},
            params=None,
            timeout=3,
            verify=True,
        )

    @staticmethod
    def test_login(monkeypatch: MonkeyPatch) -> None:
        """
        Test the login to a FortiManager.
        """

        # Arrange
        post_mock = Mock(
            return_value=ResponseMock(
                json={
                    "id": 1,
                    "result": [{"status": {"code": 0, "message": "OK"}, "url": "/sys/login/user"}],
                    "session": "dummy_session_key",
                },
                status_code=200,
            )
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)
        fmg = FortiManager("host", "user", "pass")

        # Act & Assert
        assert fmg.login() == 200
        post_mock.assert_called_with(
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
        """
        Test the login to a FortiManager when a session_path is given.
        """

        # Arrange
        post_mock = Mock(
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
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)
        fmg = FortiManager("host", "user", "pass")
        fmg.hostname = "test_fmg"
        fmg.session_path = "tests/data"

        # Act & Assert
        assert fmg.login() == 200
        post_mock.assert_called_with(
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
        Test the login to a FortiManager when a session_path is given, but the session key is
        invalid.
        """

        # Arrange
        post_mock = Mock(
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
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)
        fmg = FortiManager("host", "user", "pass")
        fmg.hostname = "test_fmg"
        fmg.session_path = "tests/data"

        # Act & Assert
        assert fmg.login() == 200
        post_mock.assert_called_with(
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
    def test_login_with_session_path_not_found(function_dir: str, monkeypatch: MonkeyPatch) -> None:
        """
        Test the login to a FortiManager when a session_path is given, but the session path is
        invalid.
        """

        # Arrange
        post_mock = Mock(
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
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)
        fmg = FortiManager("host", "user", "pass")
        fmg.hostname = "test_fmg_dummy"
        fmg.session_path = function_dir

        # Act & Assert
        assert fmg.login() == 200
        post_mock.assert_called_with(
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
        """
        Test the logout of a FortiManager.
        """

        # Arrange
        post_mock = Mock(
            return_value=ResponseMock(
                json={
                    "method": "exec",
                    "params": [{"url": "/sys/logout"}],
                    "session": "dummy_session_key",
                },
                status_code=200,
            )
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)
        fortimanager = FortiManager("host", "user", "pass")

        # Act & Assert
        assert fortimanager.logout() == 200
        post_mock.assert_called_with(
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
        """
        Test fmg post with a single dict.
        """

        # Arrange
        post_mock = Mock(
            return_value=ResponseMock(json={"result": [{"status": {"code": 0}}]}, status_code=200)
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        assert not FortiManager("host", "", "").post("ADOM", {"params": [{"url": "{adom}"}]})
        post_mock.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_post_multiple(monkeypatch: MonkeyPatch) -> None:
        """
        Test fmg post with a list of dicts.
        """

        # Arrange
        post_mock = Mock(
            return_value=ResponseMock(json={"result": [{"status": {"code": 0}}]}, status_code=200)
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        assert not FortiManager("host", "", "").post("ADOM", [{"params": [{"url": "{adom}"}]}])
        post_mock.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_post_single_global(monkeypatch: MonkeyPatch) -> None:
        """
        Test fmg post with a single dict.
        """

        # Arrange
        post_mock = Mock(
            return_value=ResponseMock(json={"result": [{"status": {"code": 0}}]}, status_code=200)
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        assert not FortiManager("host", "", "").post("global", {"params": [{"url": "{adom}"}]})
        post_mock.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "global"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_post_response_error(monkeypatch: MonkeyPatch) -> None:
        """
        Test post set with en error in the response.
        """

        # Arrange
        post_mock = Mock(
            return_value=ResponseMock(
                json={"result": [{"status": {"code": 444, "message": "dummy"}, "url": "dummy"}]},
                status_code=200,
            )
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        assert FortiManager("host", "", "").post("ADOM", [{"params": [{"url": "{adom}"}]}]) == [
            "dummy: dummy (code: 444)"
        ]
        post_mock.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_post_http_error(monkeypatch: MonkeyPatch) -> None:
        """
        Test fmg post with an error in the response.
        """

        # Arrange
        post_mock = Mock(return_value=ResponseMock(json={}, status_code=444))
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act & Assert
        with pytest.raises(APIError) as err:
            FortiManager("host", "", "").post("ADOM", [{"params": [{"url": "{adom}"}]}])
        assert "HTTP/444 general API Error" in str(err.value)
        post_mock.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"params": [{"url": "adom/ADOM"}], "session": ""},
            params=None,
            timeout=10,
            verify=True,
        )

    @staticmethod
    def test_wait_for_task(monkeypatch: MonkeyPatch) -> None:
        """
        Test the wait_for_task method.
        """

        # Arrange
        post_mock = Mock(
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
        )
        monkeypatch.setattr("fotoobo.fortinet.fortinet.requests.Session.post", post_mock)

        # Act
        messages = FortiManager("host", "", "").wait_for_task(222, 0)

        # Assert
        assert isinstance(messages, list)
        assert messages[0]["task_id"] == 222
        post_mock.assert_called_with(
            "https://host:443/jsonrpc",
            headers=None,
            json={"method": "get", "params": [{"url": "/task/task/222/line"}], "session": ""},
            params=None,
            timeout=3,
            verify=True,
        )
