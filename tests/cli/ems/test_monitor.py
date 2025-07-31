"""
Testing the ems monitor cli app.
"""

from unittest.mock import Mock

from pytest import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from tests.helper import ResponseMock, parse_help_output

runner = CliRunner()


def test_cli_app_ems_monitor_help(help_args_with_none: str) -> None:
    """
    Test cli help for ems monitor.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "ems", "monitor"]
    args.append(help_args_with_none)
    args = list(filter(None, args))

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code in [0, 2]
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


def test_cli_app_ems_monitor_connections_help(help_args: str) -> None:
    """
    Test cli help for ems monitor connections.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "ems", "monitor", "connections"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_connections(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli for ems monitor connections.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        Mock(
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

    # Act
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "connections", "test_ems"]
    )

    # Assert
    assert result.exit_code == 0
    assert "managed   │ 1000  │ Managed" in result.stdout
    assert "unmanaged │ 99    │ Unmanaged" in result.stdout


def test_cli_app_ems_monitor_endpoint_management_status_help(help_args: str) -> None:
    """
    Test cli help for ems monitor endpoint-management-status.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-management-status"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_endpoint_management_status(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli for ems monitor connections.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        Mock(
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

    # Act
    result = runner.invoke(
        app,
        ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-management-status", "test_ems"],
    )

    # Assert
    assert result.exit_code == 0
    assert "Managed   │ 1000" in result.stdout
    assert "Unmanaged │ 99" in result.stdout


def test_cli_app_ems_monitor_endpoint_os_versions_help(help_args: str) -> None:
    """
    Test cli help for ems monitor endpoint-os-versions.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-os-versions"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_endpoint_os_versions(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli for ems monitor connections.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        Mock(
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

    # Act
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-os-versions", "test_ems"]
    )

    # Assert
    assert result.exit_code == 0
    assert "windows │ dummy_ver_1 │ 333" in result.stdout
    assert "linux   │ dummy_ver_2 │ 444" in result.stdout
    assert "Summary" in result.stdout
    assert "windows │ 777" in result.stdout
    assert "mac     │ 777" in result.stdout
    assert "linux   │ 777" in result.stdout


def test_cli_app_ems_monitor_endpoint_outofsync_help(help_args: str) -> None:
    """
    Test cli help for ems monitor endpoint-outofsync.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-outofsync"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_endpoint_outofsync(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli for ems monitor connections.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        Mock(
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

    # Act
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "endpoint-outofsync", "test_ems"]
    )

    # Assert
    assert result.exit_code == 0
    assert "out of sync │ 999" in result.stdout


def test_cli_app_ems_monitor_license_help(help_args: str) -> None:
    """
    Test cli help for ems monitor license.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "ems", "monitor", "license"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-o", "--output", "-r", "--raw", "-t", "--template"}
    assert not commands


def test_cli_app_ems_monitor_license(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli for ems monitor connections.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        Mock(
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

    # Act
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "license", "test_ems"]
    )

    # Assert
    assert result.exit_code == 0
    assert " sn           │ FCTEMS0000000000 " in result.stdout
    assert "license_expiry_days │ " in result.stdout
    assert "fabric_agent_usage  │ 10" in result.stdout
    assert "sandbox_cloud_usage │ 20" in result.stdout


def test_cli_app_ems_monitor_system_help(help_args: str) -> None:
    """
    Test cli help for ems monitor system.
    """

    # Arrange
    args = ["-c", "tests/fotoobo.yaml", "ems", "monitor", "system"]
    args.append(help_args)

    # Act
    result = runner.invoke(app, args)

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert set(arguments) == {"host"}
    assert options == {"-h", "--help", "-r", "--raw"}
    assert not commands


def test_cli_app_ems_monitor_system(monkeypatch: MonkeyPatch) -> None:
    """
    Test cli for ems monitor connections.
    """

    # Arrange
    monkeypatch.setattr(
        "fotoobo.fortinet.forticlientems.FortiClientEMS.api",
        Mock(
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

    # Act
    result = runner.invoke(
        app, ["-c", "tests/fotoobo.yaml", "ems", "monitor", "system", "test_ems"]
    )

    # Assert
    assert result.exit_code == 0
    assert " hostname    │ dummy_hostname " in result.stdout
    assert " system_time │ 2066-06-06 06:06:06 " in result.stdout
