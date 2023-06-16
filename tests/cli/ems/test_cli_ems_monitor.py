"""
Testing the ems monitor cli app
"""
from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import ResponseMock, parse_help_output

runner = CliRunner()


def test_cli_app_ems_monitor_help() -> None:
    """Test cli help for ems monitor"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {
        "connections",
        "endpoint-management-status",
        "endpoint-os-versions",
        "endpoint-outofsync",
        "license",
        "system",
    }


def test_cli_app_ems_monitor_connections_help() -> None:
    """Test cli help for ems monitor connections"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "connections", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_connections(monkeypatch: MonkeyPatch) -> None:
    """Test cli for ems monitor connections"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": [
                        {"token": "managed", "value": 1000, "name": "Managed"},
                        {"token": "unmanaged", "value": 99, "name": "Unmanaged"},
                    ],
                }
            )
        ),
    )
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "connections", "test_ems"]
    )

    assert result.exit_code == 0

    assert "managed   │ 1000  │ Managed" in result.stdout
    assert "unmanaged │ 99    │ Unmanaged" in result.stdout


def test_cli_app_ems_monitor_endpoint_management_status_help() -> None:
    """Test cli help for ems monitor endpoint-management-status"""
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-management-status", "-h"]
    )
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_endpoint_management_status(monkeypatch: MonkeyPatch) -> None:
    """Test cli for ems monitor connections"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": [
                        {"token": "managed", "value": 1000, "name": "Managed"},
                        {"token": "unmanaged", "value": 99, "name": "Unmanaged"},
                    ],
                }
            )
        ),
    )
    result = runner.invoke(
        app,
        ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-management-status", "test_ems"],
    )

    assert result.exit_code == 0

    assert "Managed   │ 1000" in result.stdout
    assert "Unmanaged │ 99" in result.stdout


def test_cli_app_ems_monitor_endpoint_os_versions_help() -> None:
    """Test cli help for ems monitor endpoint-os-versions"""
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-os-versions", "-h"]
    )
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_endpoint_os_versions(monkeypatch: MonkeyPatch) -> None:
    """Test cli for ems monitor connections"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": [
                        {"token": "dummy_os_1", "name": "dummy_ver_1", "value": 333},
                        {"token": "dummy_os_2", "name": "dummy_ver_2", "value": 444},
                    ],
                }
            )
        ),
    )
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-os-versions", "test_ems"]
    )

    assert result.exit_code == 0

    assert "windows │ dummy_ver_1 │ 333" in result.stdout
    assert "linux   │ dummy_ver_2 │ 444" in result.stdout
    assert "Summary" in result.stdout
    assert "windows │ 777" in result.stdout
    assert "mac     │ 777" in result.stdout
    assert "linux   │ 777" in result.stdout


def test_cli_app_ems_monitor_endpoint_outofsync_help() -> None:
    """Test cli help for ems monitor endpoint-outofsync"""
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-outofsync", "-h"]
    )
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_endpoint_outofsync(monkeypatch: MonkeyPatch) -> None:
    """Test cli for ems monitor connections"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": {
                        "endpoints": [{"device_id": 888, "name": "dummy_device_name"}],
                        "total": 999,
                    },
                }
            )
        ),
    )
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-outofsync", "test_ems"]
    )

    assert result.exit_code == 0

    assert "out of sync │ 999" in result.stdout


def test_cli_app_ems_monitor_license_help() -> None:
    """Test cli help for ems monitor license"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "license", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_license(monkeypatch: MonkeyPatch) -> None:
    """Test cli for ems monitor connections"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": None},
                    "data": {
                        "sn": "FCTEMS0000000000",
                        "hid": "00000000-0000-0000-0000-000000000000-00000000",
                        "seats": {"fabric_agent": 1000, "sandbox_cloud": 2000},
                        "future_seats": {"fabric_agent": 1000, "sandbox_cloud": 2000},
                        "licenses": [
                            {
                                "expiry_date": "2099-01-01T00:00:00",
                                "start_date": "2098-01-01T00:00:00",
                                "type": "fabric_agent",
                            },
                        ],
                        "is_trial": False,
                        "license_ver": 0,
                        "future_ver": 0,
                        "error": None,
                        "vdom_seats": {"fabric_agent": 1000, "sandbox_cloud": 2000},
                        "used": {
                            "fabric_agent": 100,
                            "sandbox_cloud": 400,
                        },
                    },
                }
            )
        ),
    )
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "license", "test_ems"]
    )

    assert result.exit_code == 0

    assert " sn           │ FCTEMS0000000000 " in result.stdout

    assert "license_expiry_days │ " in result.stdout
    assert "fabric_agent_usage  │ 10" in result.stdout
    assert "sandbox_cloud_usage │ 20" in result.stdout


def test_cli_app_ems_monitor_system_help() -> None:
    """Test cli help for ems monitor system"""
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "system", "-h"])
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-r", "--raw"}
    assert not commands


def test_cli_app_ems_monitor_system(monkeypatch: MonkeyPatch) -> None:
    """Test cli for ems monitor connections"""
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        MagicMock(
            return_value=ResponseMock(
                json={
                    "result": {"retval": 1, "message": "System info retrieved successfully."},
                    "data": {
                        "name": "dummy_hostname",
                        "system_time": "2066-06-06 06:06:06",
                        "license": {
                            "sn": "FCTEMS0000000000",
                            "hid": "00000000-0000-0000-0000-000000000000-00000000",
                            "seats": {"fabric_agent": 1001, "sandbox_cloud": 1002},
                            "future_seats": {"fabric_agent": 1001, "sandbox_cloud": 1002},
                            "licenses": [
                                {
                                    "expiry_date": "2099-01-01T00:00:00",
                                    "start_date": "2098-01-01T00:00:00",
                                    "type": "fabric_agent",
                                },
                            ],
                            "is_trial": False,
                            "license_ver": 0,
                            "future_ver": 0,
                            "error": None,
                            "used": {"fabric_agent": 1001, "sandbox_cloud": 1002},
                        },
                    },
                }
            )
        ),
    )
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "system", "test_ems"]
    )

    assert result.exit_code == 0

    assert " hostname    │ dummy_hostname " in result.stdout
    assert " system_time │ 2066-06-06 06:06:06 " in result.stdout
