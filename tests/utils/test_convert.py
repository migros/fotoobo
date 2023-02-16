"""Test fotoobo utils convert"""

import os
import shutil
from copy import deepcopy
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralError
from fotoobo.helpers.files import load_json_file
from fotoobo.utils.convert import convert_checkpoint


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
def test_convert(asset_type: str, monkeypatch: MonkeyPatch, temp_dir: str) -> None:
    """Test convert"""
    return_value: Dict[str, Any] = {
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

    monkeypatch.setattr(
        "fotoobo.utils.convert.load_json_file", MagicMock(return_value=deepcopy(return_value))
    )

    output_file = os.path.join(temp_dir, f"convert_{asset_type}.json")

    convert_checkpoint("", output_file, asset_type)
    assert os.path.isfile(output_file)
    converted = list(load_json_file(output_file) or [])

    for index in range(len(return_value[asset_type])):
        asset = converted[0]["params"][index]["data"]
        assert asset["name"] == return_value[asset_type][index]["name"]
        assert asset["comment"] == return_value[asset_type][index]["comments"]


@pytest.mark.parametrize(
    "asset_type",
    (
        pytest.param("", id="test with empty type"),
        pytest.param("dummy", id="test type 'dummy'"),
    ),
)
def test_convert_unsupported_type(asset_type: str, monkeypatch: MonkeyPatch) -> None:
    """Test convert for unsupported types (which rise a GeneralError exception)"""
    monkeypatch.setattr("fotoobo.utils.convert.load_json_file", MagicMock(return_value=[]))
    with pytest.raises(GeneralError, match=r"type '.*' is not supported to convert"):
        convert_checkpoint("", "", asset_type)


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
def test_convert_with_cache(asset_type: str, monkeypatch: MonkeyPatch, temp_dir: str) -> None:
    """Test convert with cache"""
    return_value: Dict[str, Any] = {
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

    monkeypatch.setattr(
        "fotoobo.utils.convert.load_json_file", MagicMock(return_value=deepcopy(return_value))
    )

    output_file = os.path.join(temp_dir, f"convert_cache_{asset_type}.json")
    cache_dir = os.path.join(temp_dir, "cache")

    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)

    shutil.copy(
        os.path.join("tests", "data", "convert_cache_hosts.json"),
        os.path.join(cache_dir, "convert_cache_hosts.json"),
    )

    convert_checkpoint("", output_file, asset_type, cache_dir)
    assert os.path.isfile(output_file)

    converted = list(load_json_file(output_file) or [])
    if asset_type == "hosts":
        assert len(converted[0]["params"]) == 1
        assert converted[0]["params"][0]["data"]["name"] == return_value["hosts"][1]["name"]
