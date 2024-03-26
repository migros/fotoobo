"""Test fotoobo convert tools"""

import shutil
from pathlib import Path
from typing import Any, Dict

import pytest

from fotoobo.exceptions import GeneralError
from fotoobo.tools.convert import checkpoint


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
def test_convert(asset_type: str) -> None:
    """Test convert"""
    checkpoint_assets: Dict[str, Any] = {
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

    result = checkpoint(checkpoint_assets, asset_type, "out_file_name")
    converted = result.get_result("fortinet_assets") or []

    for index in range(len(checkpoint_assets[asset_type])):
        asset = converted[0]["params"][index]["data"]
        assert asset["name"] == checkpoint_assets[asset_type][index]["name"]
        assert asset["comment"] == checkpoint_assets[asset_type][index]["comments"]


@pytest.mark.parametrize(
    "asset_type",
    (
        pytest.param("", id="test with empty type"),
        pytest.param("dummy", id="test type 'dummy'"),
    ),
)
def test_convert_unsupported_type(asset_type: str) -> None:
    """Test convert for unsupported types (which rise a GeneralError exception)"""
    with pytest.raises(GeneralError, match=r"type '.*' is not supported to convert"):
        checkpoint([], "", asset_type)


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
def test_convert_with_cache(asset_type: str, temp_dir: Path) -> None:
    """Test convert with cache"""
    checkpoint_assets: Dict[str, Any] = {
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

    output_file_name = f"convert_cache_{asset_type}.json"
    cache_dir = temp_dir / "cache"

    if not cache_dir.is_dir():
        cache_dir.mkdir()

    shutil.copy(
        Path("tests", "data", "convert_cache_hosts.json"),
        cache_dir / "convert_cache_hosts.json",
    )

    result = checkpoint(checkpoint_assets, asset_type, output_file_name, cache_dir)

    converted = result.get_result("fortinet_assets")
    if asset_type == "hosts":
        # We have one ("aaa-*") already in the cache, only need to convert 1
        assert len(converted[0]["params"]) == 1
        converted_name = converted[0]["params"][0]["data"]["name"]
        expected_name = checkpoint_assets["hosts"][1]["name"]
        assert converted_name == expected_name
