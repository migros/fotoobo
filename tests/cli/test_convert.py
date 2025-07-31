"""
Testing the cli convert app.
"""

import shutil
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

from fotoobo.cli.main import app
from fotoobo.helpers.files import load_json_file
from tests.helper import parse_help_output

runner = CliRunner()


def test_cli_convert_no_args() -> None:
    """
    Test convert cli without issuing any arguments.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "convert"])

    # Assert
    assert result.exit_code in [0, 2]
    assert "Usage: root convert [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "--help" in result.stdout
    assert "Convert commands for fotoobo" in result.stdout


def test_cli_convert_help() -> None:
    """
    Test cli help for convert.
    """

    # Act
    result = runner.invoke(app, ["-c", "tests/fotoobo.yaml", "convert", "-h"])

    # Assert
    assert result.exit_code == 0
    arguments, options, commands = parse_help_output(result.stdout)
    assert not arguments
    assert options == {"-h", "--help"}
    assert set(commands) == {"checkpoint"}


def test_cli_convert_checkpoint_unsupported(monkeypatch: MonkeyPatch) -> None:
    """
    Test convert cli command: convert checkpoint assets with unsupported type.
    """

    # Arrange
    monkeypatch.setattr("fotoobo.cli.convert.load_json_file", Mock(return_value=[]))

    # Act
    result = runner.invoke(
        app,
        ["-c", "tests/fotoobo.yaml", "convert", "checkpoint", "infile", "outfile", "unsupported"],
    )

    # Assert
    assert result.exit_code == 1


@pytest.mark.parametrize(
    "asset_type",
    (
        pytest.param("hosts", id="test type 'hosts'"),
        pytest.param("networks", id="test type 'networks'"),
        pytest.param("address_ranges", id="test type 'address_ranges'"),
        pytest.param("groups", id="test type 'groups'"),
        pytest.param("services_icmp", id="test type 'services_icmp'"),
        pytest.param("services_icmp6", id="test type 'services_icmp6'"),
        pytest.param("services_tcp", id="test type 'services_tcp'"),
        pytest.param("services_udp", id="test type 'services_udp'"),
        pytest.param("service_groups", id="test type 'service_groups'"),
    ),
)
def test_cli_convert(asset_type: str, monkeypatch: MonkeyPatch, function_dir: Path) -> None:
    """
    Test convert.
    """

    # Arrange
    return_value: dict[str, Any] = {
        "hosts": [
            {
                "uid": "aaaa-aaaa-aaaa-aaaa",
                "name": "dummy_host_1",
                "ipv4-address": "1.1.1.1",
                "comments": "dummy_comment_2",
                "dummy": "dummy",
            },
            {
                "uid": "bbbb-bbbb-bbbb-bbbb",
                "name": "dummy_host_2",
                "ipv4-address": "2.2.2.2",
                "comments": "dummy_comment_2",
                "dummy": "dummy",
            },
        ],
        "networks": [
            {
                "name": "dummy_network_1",
                "comments": "dummy_network_comment_1",
                "subnet4": "1.1.1.0",
                "mask-length4": 24,
                "uid": "1111-1111-1111-1111",
                "dummy": "dummy",
            }
        ],
        "address_ranges": [],
        "groups": [],
        "services_icmp": [],
        "services_icmp6": [],
        "services_tcp": [],
        "services_udp": [],
        "service_groups": [],
    }
    monkeypatch.setattr("fotoobo.cli.convert.load_json_file", Mock(return_value=return_value))
    output_file = function_dir / f"convert_{asset_type}.json"

    # Act
    result = runner.invoke(
        app,
        [
            "-c",
            "tests/fotoobo.yaml",
            "convert",
            "checkpoint",
            "testfile",
            str(output_file),
            asset_type,
        ],
    )

    # Assert
    assert result.exit_code == 0
    assert output_file.is_file()
    converted = list(load_json_file(output_file) or [])

    for index in range(len(return_value[asset_type])):
        asset = converted[0]["params"][index]["data"]
        assert asset["name"] == return_value[asset_type][index]["name"]
        assert asset["comment"] == return_value[asset_type][index]["comments"]


@pytest.mark.parametrize(
    "asset_type",
    (
        pytest.param("hosts", id="test type 'hosts'"),
        pytest.param("networks", id="test type 'networks'"),
        pytest.param("address_ranges", id="test type 'address_ranges'"),
        pytest.param("groups", id="test type 'groups'"),
        pytest.param("services_icmp", id="test type 'services_icmp'"),
        pytest.param("services_icmp6", id="test type 'services_icmp6'"),
        pytest.param("services_tcp", id="test type 'services_tcp'"),
        pytest.param("services_udp", id="test type 'services_udp'"),
        pytest.param("service_groups", id="test type 'service_groups'"),
    ),
)
def test_cli_convert_with_cache(
    asset_type: str, monkeypatch: MonkeyPatch, function_dir: Path
) -> None:
    """
    Test convert with cache.
    """

    # Arrange
    return_value: dict[str, Any] = {
        "hosts": [
            {
                "uid": "aaaa-aaaa-aaaa-aaaa",
                "name": "dummy_1",
                "ipv4-address": "1.1.1.1",
                "comments": "dummy_comment_1",
                "dummy": "dummy",
            },
            {
                "uid": "cccc-cccc-cccc-cccc",
                "name": "dummy_3",
                "ipv4-address": "3.3.3.3",
                "comments": "dummy_comment_3",
                "dummy": "dummy",
            },
        ],
        "networks": [],
        "address_ranges": [],
        "groups": [],
        "services_icmp": [],
        "services_icmp6": [],
        "services_tcp": [],
        "services_udp": [],
        "service_groups": [],
    }
    monkeypatch.setattr("fotoobo.cli.convert.load_json_file", Mock(return_value=return_value))
    output_file = function_dir / f"convert_cache_{asset_type}.json"
    cache_dir = function_dir / "cache"

    if not cache_dir.is_dir():
        cache_dir.mkdir()

    shutil.copy(
        Path("tests", "data", "convert_cache_hosts.json"),
        cache_dir / "convert_cache_hosts.json",
    )

    # Act
    result = runner.invoke(
        app,
        [
            "-c",
            "tests/fotoobo.yaml",
            "convert",
            "checkpoint",
            "testfile",
            str(output_file),
            asset_type,
            str(cache_dir),
        ],
    )

    # Assert
    assert result.exit_code == 0
    assert output_file.is_file()

    converted = list(load_json_file(output_file) or [])
    if asset_type == "hosts":
        assert len(converted[0]["params"]) == 1
        assert converted[0]["params"][0]["data"]["name"] == return_value["hosts"][1]["name"]
