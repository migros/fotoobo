"""
Test the FortiGate config class
"""
import os
from typing import Any, Dict

import pytest

from fotoobo.fortinet.fortigate_config import FortiGateConfig


@pytest.fixture
def conf_file_vdom() -> str:
    """The configuration file with a FortiGate config with VDOMs enabled"""
    return "tests/data/fortigate_config_vdom.conf"


@pytest.fixture
def conf_file_single() -> str:
    """The configuration file with a FortiGate config with single VDOM mode"""
    return "tests/data/fortigate_config_single.conf"


@pytest.fixture
def conf_file_empty() -> str:
    """Just an empty configuration file"""
    return "tests/data/fortigate_config_empty.conf"


@pytest.fixture
def empty_dict() -> Dict[Any, Any]:
    """returns an empty dict"""
    return {}


@pytest.fixture
def config_dict_as_list() -> Dict[str, Dict[str, str]]:
    """returns a FortiGateConfig dict which contains elements as a list (key is int)"""
    return {
        "1": {"key1": "value1", "key2": "value2"},
        "2": {"key1": "value1", "key2": "value2"},
    }


@pytest.fixture
def config_dict_as_not_a_list() -> Dict[str, Dict[str, str]]:
    """returns a FortiGateConfig dict which contains elements as not a list (key is str)"""
    return {
        "string1": {"key1": "value1", "key2": "value2"},
        "string2": {"key1": "value1", "key2": "value2"},
    }


class TestFortiGateConfigGeneral:
    # pylint: disable=protected-access, redefined-outer-name
    """Test the FortiGateConfig class without a dummy config"""

    @staticmethod
    def test_parse_to_dict_empty(conf_file_empty: str) -> None:
        """Test the _parse_to_dict method with empty file"""
        FortiGateConfig._config_path = []  # only needed as long as _config_path is not thread-safe
        with open(conf_file_empty, "r", encoding="UTF-8") as forti_file:
            config = FortiGateConfig._parse_to_dict(forti_file)
        assert not config


class TestFortiGateConfigSingle:
    # pylint: disable=protected-access, redefined-outer-name
    """Test the FortiGateConfig class with a dummy config which is in single VDOM mode"""

    @staticmethod
    def test_config_is_list_with_list(config_dict_as_list: Dict[str, str]) -> None:
        """Test the _config_is_list method if the configuration is a list"""
        assert FortiGateConfig._config_is_list(config_dict_as_list)

    @staticmethod
    def test_config_is_list_with_not_list(config_dict_as_not_a_list: Dict[str, Any]) -> None:
        """Test the _config_is_list method if the configuration is not a list"""
        assert not FortiGateConfig._config_is_list(config_dict_as_not_a_list)

    @staticmethod
    def test_config_is_list_empty(empty_dict: Dict[Any, Any]) -> None:
        """Test the _config_is_list method if the configuration is empty"""
        assert not FortiGateConfig._config_is_list(empty_dict)

    @staticmethod
    def test_config_convert_dict_to_list() -> None:
        """Test the _config_convert_dict_to_list"""
        config = {
            "1": {"key1": "value1", "key2": "value2"},
            "2": {"key1": "value1", "key2": "value2"},
        }
        expect = [
            {"key1": "value1", "key2": "value2", "id": 1},
            {"key1": "value1", "key2": "value2", "id": 2},
        ]
        assert FortiGateConfig._config_convert_dict_to_list(config) == expect
        assert not FortiGateConfig._config_convert_dict_to_list({})

    @staticmethod
    def test_parse_config_comment() -> None:
        """Test the _parse_config_comment method"""
        info: Dict[str, str] = {}
        comment_line = "#config-version=FGT999-9.9.9-FW-build9999-210217:opmode=1:vdom=2:user=pi"
        FortiGateConfig._parse_config_comment(info, comment_line)
        expect = {
            "model": "FGT999",
            "os_version": "9.9.9",
            "type": "FW",
            "opmode": "1",
            "vdom": "2",
            "user": "pi",
        }
        assert info == expect
        info = {}
        FortiGateConfig._parse_config_comment(info, "#conf_file_ver=1234567890")
        assert info == {"conf_file_ver": "1234567890"}
        info = {}
        FortiGateConfig._parse_config_comment(info, "#buildno=8303")
        assert info == {"buildno": "8303"}
        info = {}
        FortiGateConfig._parse_config_comment(info, "#global_vdom=007")
        assert info == {"global_vdom": "007"}
        info = {}
        FortiGateConfig._parse_config_comment(info, "")
        assert not info

    @staticmethod
    def test_parse_to_dict(conf_file_single: str) -> None:
        """Test the _parse_to_dict method with dummy file"""
        FortiGateConfig._config_path = []  # only needed as long as _config_path is not thread-safe
        with open(conf_file_single, "r", encoding="UTF-8") as forti_file:
            config = FortiGateConfig._parse_to_dict(forti_file)
        assert config["info"]["buildno"] == "8303"
        assert config["leaf_n"]["option_n"] == "value_n"
        assert config["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_parse_configuration_file(conf_file_single: str) -> None:
        """Test the parse_configuration_file method with dummy file"""
        config = FortiGateConfig.parse_configuration_file(conf_file_single)
        assert config.info.buildno == "8303"
        assert config.vdom_config["root"]["leaf_n"]["option_n"] == "value_n"
        assert config.vdom_config["root"]["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_save_configuration_file(temp_dir: str, conf_file_single: str) -> None:
        """Test the load_configuration_file method with dummy file"""
        filename = os.path.join(temp_dir, "testsingle.json")
        assert not os.path.isfile(filename)
        config = FortiGateConfig.parse_configuration_file(conf_file_single)
        config.save_configuration_file(filename)
        assert os.path.isfile(filename)

    @staticmethod
    def test_load_configuration_file(temp_dir: str) -> None:
        """Test the load_configuration_file method with dummy file"""
        filename = os.path.join(temp_dir, "testsingle.json")
        assert os.path.isfile(filename)
        config = FortiGateConfig.load_configuration_file(filename)
        assert config.info.buildno == "8303"
        assert config.vdom_config["root"]["leaf_n"]["option_n"] == "value_n"
        assert config.vdom_config["root"]["leaf_z"]["option_z"] == "value_z"


class TestFortiGateConfigVDOM:
    # pylint: disable=protected-access, redefined-outer-name
    """Test the FortiGateConfig class with a dummy config which has VDOMs in it"""

    @staticmethod
    def test_fortigate_config_class_instantiation() -> None:
        """Test the FortiGateConfigClass instantiation"""
        config = FortiGateConfig()
        assert config.global_config == {}
        assert config.vdom_config == {}

    @staticmethod
    def test_config_is_list_with_list(config_dict_as_list: Dict[str, str]) -> None:
        """Test the _config_is_list method if the configuration is a list"""
        assert FortiGateConfig._config_is_list(config_dict_as_list)

    @staticmethod
    def test_config_is_list_with_not_list(config_dict_as_not_a_list: Dict[str, Any]) -> None:
        """Test the _config_is_list method if the configuration is not a list"""
        assert not FortiGateConfig._config_is_list(config_dict_as_not_a_list)

    @staticmethod
    def test_config_is_list_empty(empty_dict: Dict[Any, Any]) -> None:
        """Test the _config_is_list method if the configuration is empty"""
        assert not FortiGateConfig._config_is_list(empty_dict)

    @staticmethod
    def test_config_convert_dict_to_list() -> None:
        """Test the _config_convert_dict_to_list"""
        config = {
            "1": {"key1": "value1", "key2": "value2"},
            "2": {"key1": "value1", "key2": "value2"},
        }
        expect = [
            {"key1": "value1", "key2": "value2", "id": 1},
            {"key1": "value1", "key2": "value2", "id": 2},
        ]
        assert FortiGateConfig._config_convert_dict_to_list(config) == expect
        assert not FortiGateConfig._config_convert_dict_to_list({})

    @staticmethod
    def test_parse_config_comment() -> None:
        """Test the _parse_config_comment method"""
        info: Dict[str, str] = {}
        comment_line = "#config-version=FGT999-9.9.9-FW-build9999-210217:opmode=1:vdom=2:user=pi"
        FortiGateConfig._parse_config_comment(info, comment_line)
        expect = {
            "model": "FGT999",
            "os_version": "9.9.9",
            "type": "FW",
            "opmode": "1",
            "vdom": "2",
            "user": "pi",
        }
        assert info == expect
        info = {}
        FortiGateConfig._parse_config_comment(info, "#conf_file_ver=1234567890")
        assert info == {"conf_file_ver": "1234567890"}
        info = {}
        FortiGateConfig._parse_config_comment(info, "#buildno=8303")
        assert info == {"buildno": "8303"}
        info = {}
        FortiGateConfig._parse_config_comment(info, "#global_vdom=007")
        assert info == {"global_vdom": "007"}
        info = {}
        FortiGateConfig._parse_config_comment(info, "")
        assert not info

    @staticmethod
    def test_parse_to_dict(conf_file_vdom: str) -> None:
        """Test the _parse_to_dict method with dummy file"""
        FortiGateConfig._config_path = []  # only needed as long as _config_path is not thread-safe
        with open(conf_file_vdom, "r", encoding="UTF-8") as forti_file:
            config = FortiGateConfig._parse_to_dict(forti_file)
        assert config["info"]["buildno"] == "8303"
        assert config["vdom"]["vdom_n"]["leaf_n"]["option_n"] == "value_n"
        assert config["vdom"]["vdom_z"]["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_parse_configuration_file(conf_file_vdom: str) -> None:
        """Test the parse_configuration_file method with dummy file"""
        config = FortiGateConfig.parse_configuration_file(conf_file_vdom)
        assert config.info.buildno == "8303"
        assert config.vdom_config["vdom_n"]["leaf_n"]["option_n"] == "value_n"
        assert config.vdom_config["vdom_z"]["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_save_configuration_file(temp_dir: str, conf_file_vdom: str) -> None:
        """Test the load_configuration_file method with dummy file"""
        filename = os.path.join(temp_dir, "testvdom.json")
        assert not os.path.isfile(filename)
        config = FortiGateConfig.parse_configuration_file(conf_file_vdom)
        config.save_configuration_file(filename)
        assert os.path.isfile(filename)

    @staticmethod
    def test_load_configuration_file(temp_dir: str) -> None:
        """Test the load_configuration_file method with dummy file"""
        filename = os.path.join(temp_dir, "testvdom.json")
        assert os.path.isfile(filename)
        config = FortiGateConfig.load_configuration_file(filename)
        assert config.info.buildno == "8303"
        assert config.vdom_config["vdom_n"]["leaf_n"]["option_n"] == "value_n"
        assert config.vdom_config["vdom_z"]["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_get_configuration_global(conf_file_single: str, conf_file_vdom: str) -> None:
        """Test the get_configuration_file method for global configuration"""
        config_single = FortiGateConfig.parse_configuration_file(conf_file_single)
        config_vdom = FortiGateConfig.parse_configuration_file(conf_file_vdom)
        for config in [config_single, config_vdom]:
            assert config.get_configuration()
            assert config.get_configuration("global")
            assert config.get_configuration("global", "")
            assert config.get_configuration("global", "/")
            assert config.get_configuration("global", "/system/global/option_1") == "value_1"
            assert config.get_configuration("global", "/system/global/option_1/") == "value_1"
            assert config.get_configuration("global", "/system/global//option_1/") == "value_1"
            assert not config.get_configuration("global", "/system/not/option_1/")
            assert not config.get_configuration("global", "/system/global/not")

    @staticmethod
    def test_get_configuration_single(conf_file_single: str) -> None:
        """Test the get_configuration_file method for vdom configuration in single mode"""
        config = FortiGateConfig.parse_configuration_file(conf_file_single)
        assert config.get_configuration("vdom")
        assert config.get_configuration("vdom", "")
        assert config.get_configuration("vdom", "/")
        assert config.get_configuration("vdom", "/root/leaf_1/option_1") == "value_1"
        assert config.get_configuration("vdom", "/root/leaf_1/option_1/") == "value_1"
        assert config.get_configuration("vdom", "/root/leaf_1//option_1/") == "value_1"
        assert not config.get_configuration("vdom", "/root/not/option_1/")
        assert not config.get_configuration("vdom", "/root/leaf_1/not")

    @staticmethod
    def test_get_configuration_vdom(conf_file_vdom: str) -> None:
        """Test the get_configuration_file method for vdom configuration in vdom mode"""
        config = FortiGateConfig.parse_configuration_file(conf_file_vdom)
        assert config.get_configuration("vdom")
        assert config.get_configuration("vdom", "")
        assert config.get_configuration("vdom", "/")
        assert config.get_configuration("vdom", "/root/leaf_1/option_1") == "value_1"
        assert config.get_configuration("vdom", "/root/leaf_1/option_1/") == "value_1"
        assert config.get_configuration("vdom", "/root/leaf_1//option_1/") == "value_1"
        assert not config.get_configuration("vdom", "/root/not/option_1/")
        assert config.get_configuration("vdom", "/root/leaf_1/option_1") == "value_1"
        assert config.get_configuration("vdom", "/vdom_n/leaf_n/option_n") == "value_n"
        assert config.get_configuration("vdom", "/vdom_z/leaf_z/option_z") == "value_z"
