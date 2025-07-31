"""
Test the FortiGate config class.
"""

from pathlib import Path
from typing import Any

import pytest

from fotoobo.fortinet.fortigate_config import FortiGateConfig


@pytest.fixture
def conf_file_vdom() -> Path:
    """
    The configuration file with a FortiGate config with VDOMs enabled.
    """

    return Path("tests/data/fortigate_config_vdom.conf")


@pytest.fixture
def conf_file_single() -> Path:
    """
    The configuration file with a FortiGate config with single VDOM mode.
    """

    return Path("tests/data/fortigate_config_single.conf")


@pytest.fixture
def conf_file_empty() -> Path:
    """
    Just an empty configuration file.
    """

    return Path("tests/data/fortigate_config_empty.conf")


@pytest.fixture
def empty_dict() -> dict[Any, Any]:
    """
    Returns an empty dictionary.
    """

    return {}


@pytest.fixture
def config_dict_as_list() -> dict[str, dict[str, str]]:
    """
    Returns a FortiGateConfig dict which contains elements as a list (key is pseudo int).
    """

    return {
        "1": {"key1": "value1", "key2": "value2"},
        "2": {"key1": "value1", "key2": "value2"},
    }


@pytest.fixture
def config_dict_as_not_a_list() -> dict[str, dict[str, str]]:
    """
    Returns a FortiGateConfig dict which contains elements as not a list (key is str).
    """

    return {
        "string1": {"key1": "value1", "key2": "value2"},
        "string2": {"key1": "value1", "key2": "value2"},
    }


class TestFortiGateConfigGeneral:
    """
    Test the FortiGateConfig class without a dummy config.
    """

    # pylint: disable=protected-access, redefined-outer-name

    @staticmethod
    def test_parse_to_dict_empty(conf_file_empty: Path) -> None:
        """
        Test the _parse_to_dict method with empty file.
        """

        # Arrange
        FortiGateConfig._config_path = []  # only needed as long as _config_path is not thread-safe

        # Act
        with conf_file_empty.open(encoding="UTF-8") as forti_file:
            config = FortiGateConfig._parse_to_dict(forti_file)

        # Assert
        assert not config


class TestFortiGateConfigSingle:
    """
    Test the FortiGateConfig class with a dummy config which is in single VDOM mode.
    """

    # pylint: disable=protected-access, redefined-outer-name

    @staticmethod
    def test_config_is_list_with_list(config_dict_as_list: dict[str, str]) -> None:
        """
        Test the _config_is_list method if the configuration is a list.
        """

        # Act & Assert
        assert FortiGateConfig._config_is_list(config_dict_as_list)

    @staticmethod
    def test_config_is_list_with_not_list(config_dict_as_not_a_list: dict[str, Any]) -> None:
        """
        Test the _config_is_list method if the configuration is not a list.
        """

        # Act & Assert
        assert not FortiGateConfig._config_is_list(config_dict_as_not_a_list)

    @staticmethod
    def test_config_is_list_empty(empty_dict: dict[Any, Any]) -> None:
        """
        Test the _config_is_list method if the configuration is empty.
        """

        # Act & Assert
        assert not FortiGateConfig._config_is_list(empty_dict)

    @staticmethod
    def test_config_convert_dict_to_list() -> None:
        """
        Test the _config_convert_dict_to_list.
        """

        # Arrange
        config = {
            "1": {"key1": "value1", "key2": "value2"},
            "2": {"key1": "value1", "key2": "value2"},
        }
        expect = [
            {"key1": "value1", "key2": "value2", "id": 1},
            {"key1": "value1", "key2": "value2", "id": 2},
        ]

        # Act & Assert
        assert FortiGateConfig._config_convert_dict_to_list(config) == expect
        assert not FortiGateConfig._config_convert_dict_to_list({})

    @staticmethod
    def test_parse_config_comment() -> None:
        """
        Test the _parse_config_comment method.
        """

        # Arrange & Act & Assert multiple times (not how we shoudl do it)
        info: dict[str, str] = {}
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
    def test_parse_to_dict(conf_file_single: Path) -> None:
        """
        Test the _parse_to_dict method with dummy file.
        """

        # Arrange
        FortiGateConfig._config_path = []  # only needed as long as _config_path is not thread-safe

        # Act
        with conf_file_single.open(encoding="UTF-8") as forti_file:
            config = FortiGateConfig._parse_to_dict(forti_file)

        # Assert
        assert config["info"]["buildno"] == "8303"
        assert config["leaf_n"]["option_n"] == "value_n"
        assert config["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_parse_configuration_file(conf_file_single: Path) -> None:
        """
        Test the parse_configuration_file method with dummy file.
        """

        # Act
        config = FortiGateConfig.parse_configuration_file(conf_file_single)

        # Assert
        assert config.info.buildno == "8303"
        assert config.vdom_config["root"]["leaf_n"]["option_n"] == "value_n"
        assert config.vdom_config["root"]["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_save_configuration_file(module_dir: Path, conf_file_single: Path) -> None:
        """
        Test the load_configuration_file method with dummy file.
        """

        # Arrange
        filename = module_dir / "testsingle.json"
        assert not filename.is_file()
        config = FortiGateConfig.parse_configuration_file(conf_file_single)

        # Act
        config.save_configuration_file(filename)

        # Assert
        assert filename.is_file()

    @staticmethod
    def test_load_configuration_file(module_dir: Path) -> None:
        """
        Test the load_configuration_file method with dummy file.
        """

        # Arrange
        filename = module_dir / "testsingle.json"
        assert filename.is_file()

        # Act
        config = FortiGateConfig.load_configuration_file(filename)

        # Assert
        assert config.info.buildno == "8303"
        assert config.vdom_config["root"]["leaf_n"]["option_n"] == "value_n"
        assert config.vdom_config["root"]["leaf_z"]["option_z"] == "value_z"


class TestFortiGateConfigVDOM:
    """
    Test the FortiGateConfig class with a dummy config which has VDOMs in it.
    """

    # pylint: disable=protected-access, redefined-outer-name

    @staticmethod
    def test_fortigate_config_class_instantiation() -> None:
        """
        Test the FortiGateConfigClass instantiation.
        """

        # Act
        config = FortiGateConfig()

        # Assert
        assert config.global_config == {}
        assert config.vdom_config == {}

    @staticmethod
    def test_config_is_list_with_list(config_dict_as_list: dict[str, str]) -> None:
        """
        Test the _config_is_list method if the configuration is a list.
        """

        # Act & Assert
        assert FortiGateConfig._config_is_list(config_dict_as_list)

    @staticmethod
    def test_config_is_list_with_not_list(config_dict_as_not_a_list: dict[str, Any]) -> None:
        """
        Test the _config_is_list method if the configuration is not a list.
        """

        # Act & Assert
        assert not FortiGateConfig._config_is_list(config_dict_as_not_a_list)

    @staticmethod
    def test_config_is_list_empty(empty_dict: dict[Any, Any]) -> None:
        """
        Test the _config_is_list method if the configuration is empty.
        """

        # Act & Assert
        assert not FortiGateConfig._config_is_list(empty_dict)

    @staticmethod
    def test_config_convert_dict_to_list() -> None:
        """
        Test the _config_convert_dict_to_list.
        """

        # Arrange
        config = {
            "1": {"key1": "value1", "key2": "value2"},
            "2": {"key1": "value1", "key2": "value2"},
        }
        expect = [
            {"key1": "value1", "key2": "value2", "id": 1},
            {"key1": "value1", "key2": "value2", "id": 2},
        ]

        # Act & Assert
        assert FortiGateConfig._config_convert_dict_to_list(config) == expect
        assert not FortiGateConfig._config_convert_dict_to_list({})

    @staticmethod
    def test_parse_config_comment() -> None:
        """
        Test the _parse_config_comment method.
        """

        # Arrange & Act & Assert multiple times (not how we should do it)
        info: dict[str, str] = {}
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
    def test_parse_to_dict(conf_file_vdom: Path) -> None:
        """
        Test the _parse_to_dict method with dummy file.
        """

        # Arrange
        FortiGateConfig._config_path = []  # only needed as long as _config_path is not thread-safe

        # Act
        with conf_file_vdom.open(encoding="UTF-8") as forti_file:
            config = FortiGateConfig._parse_to_dict(forti_file)

        # Assert
        assert config["info"]["buildno"] == "8303"
        assert config["vdom"]["vdom_n"]["leaf_n"]["option_n"] == "value_n"
        assert config["vdom"]["vdom_z"]["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_parse_configuration_file(conf_file_vdom: Path) -> None:
        """
        Test the parse_configuration_file method with dummy file.
        """

        # Act
        config = FortiGateConfig.parse_configuration_file(conf_file_vdom)

        # Assert
        assert config.info.buildno == "8303"
        assert config.vdom_config["vdom_n"]["leaf_n"]["option_n"] == "value_n"
        assert config.vdom_config["vdom_z"]["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_save_configuration_file(module_dir: Path, conf_file_vdom: Path) -> None:
        """
        Test the load_configuration_file method with dummy file.
        """

        # Arrange
        filename = module_dir / "testvdom.json"
        assert not filename.is_file()
        config = FortiGateConfig.parse_configuration_file(conf_file_vdom)

        # Act
        config.save_configuration_file(filename)

        # Assert
        assert filename.is_file()

    @staticmethod
    def test_load_configuration_file(module_dir: Path) -> None:
        """
        Test the load_configuration_file method with dummy file.
        """

        # Arrange
        filename = module_dir / "testvdom.json"
        assert filename.is_file()

        # Act
        config = FortiGateConfig.load_configuration_file(filename)

        # Assert
        assert config.info.buildno == "8303"
        assert config.vdom_config["vdom_n"]["leaf_n"]["option_n"] == "value_n"
        assert config.vdom_config["vdom_z"]["leaf_z"]["option_z"] == "value_z"

    @staticmethod
    def test_get_configuration_global(conf_file_single: Path, conf_file_vdom: Path) -> None:
        """
        Test the get_configuration_file method for global configuration.
        """

        # Arrange
        config_single = FortiGateConfig.parse_configuration_file(conf_file_single)
        config_vdom = FortiGateConfig.parse_configuration_file(conf_file_vdom)

        # Act & Assert
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
    def test_get_configuration_single(conf_file_single: Path) -> None:
        """
        Test the get_configuration_file method for vdom configuration in single mode.
        """

        # Arrange
        config = FortiGateConfig.parse_configuration_file(conf_file_single)

        # Act & Assert
        assert config.get_configuration("vdom")
        assert config.get_configuration("vdom", "")
        assert config.get_configuration("vdom", "/")
        assert config.get_configuration("vdom", "/root/leaf_1/option_1") == "value_1"
        assert config.get_configuration("vdom", "/root/leaf_1/option_1/") == "value_1"
        assert config.get_configuration("vdom", "/root/leaf_1//option_1/") == "value_1"
        assert not config.get_configuration("vdom", "/root/not/option_1/")
        assert not config.get_configuration("vdom", "/root/leaf_1/not")

    @staticmethod
    def test_get_configuration_vdom(conf_file_vdom: Path) -> None:
        """
        Test the get_configuration_file method for vdom configuration in vdom mode.
        """

        # Arrange
        config = FortiGateConfig.parse_configuration_file(conf_file_vdom)

        # Act & Assert
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
