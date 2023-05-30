"""
Test the FortiGate config check class
"""
from pathlib import Path

import pytest

from fotoobo.exceptions import GeneralError
from fotoobo.fortinet.fortigate_config import FortiGateConfig
from fotoobo.fortinet.fortigate_config_check import FortiGateConfigCheck
from fotoobo.helpers.files import load_yaml_file


@pytest.fixture
def conf_file_vdom() -> Path:
    """The configuration file with a FortiGate config with VDOMs enabled"""
    return Path("tests/data/fortigate_config_vdom.conf")


@pytest.fixture
def conf_file_single() -> Path:
    """The configuration file with a FortiGate config with single VDOM mode"""
    return Path("tests/data/fortigate_config_single.conf")


@pytest.fixture
def checks_file() -> Path:
    """The check bundle file for the FortiGate configuration checker"""
    return Path("tests/data/fortigate_checks.yaml")


@pytest.fixture
def config_vdom(conf_file_vdom: Path) -> FortiGateConfig:
    # pylint: disable=redefined-outer-name
    """A FortiGate configuration with VDOMs enabled"""
    return FortiGateConfig.parse_configuration_file(conf_file_vdom)


class TestFortiGateConfigCheck:
    """Test the FortiGateConfigCheck class"""

    # pylint: disable=redefined-outer-name, too-many-public-methods

    # start tests with different configuration files

    @staticmethod
    def test_check_config_single_global(conf_file_single: Path, checks_file: Path) -> None:
        """Do a configuration check with a single VDOM FortiGate configuration file"""
        conf_check = FortiGateConfigCheck(
            FortiGateConfig.parse_configuration_file(conf_file_single), load_yaml_file(checks_file)
        )
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_vdom_global(conf_file_vdom: Path, checks_file: Path) -> None:
        """Do a configuration check with a multiple VDOM FortiGate configuration file"""
        conf_check = FortiGateConfigCheck(
            FortiGateConfig.parse_configuration_file(conf_file_vdom), load_yaml_file(checks_file)
        )
        conf_check.execute_checks()
        assert len(conf_check.results) == 2

    # start generic tests for config_check with invalid check definition

    @staticmethod
    def test_check_config_empty_bundle_file(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check with an empty bundle file"""
        checks = None
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        try:
            conf_check.execute_checks()
            assert False
        except GeneralError as err:
            assert True
            assert "there are no checks defined" in err.message

    @staticmethod
    def test_check_config_generic_missing_type(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check with check key 'type' missing"""
        checks = [
            {
                "scope": "vdom",
                "path": "/root/leaf_81/leaf_82",
                "checks": {"eq": 2},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_generic_invalid_type(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check with check key 'type' invalid"""
        checks = [
            {
                "type": "dummy",
                "scope": "vdom",
                "path": "/root/leaf_81/leaf_82",
                "checks": {"eq": 2},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_generic_missing_scope(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check with check key 'scope' missing"""
        checks = [
            {
                "type": "count",
                "scope": "vdom",
                "path": "/root/leaf_81/leaf_82",
                "checks": {"eq": 2},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_generic_missing_path(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check with check key 'path' missing"""
        checks = [
            {
                "type": "count",
                "scope": "vdom",
                "checks": {"eq": 2},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_generic_missing_checks(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check with check key 'checks' missing"""
        checks = [
            {
                "type": "count",
                "scope": "vdom",
                "path": "/root/leaf_81/leaf_82",
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_generic_empty_checks(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check with check key 'checks' empty"""
        checks = [
            {
                "type": "count",
                "scope": "vdom",
                "path": "/root/leaf_81/leaf_82",
                "checks": {},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_generic_missing_multiple(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check with multiple check keys missing"""
        checks = [{"type": "count"}]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    # start tests for config_check type: count

    @staticmethod
    def test_check_config_count(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:count"""
        checks = [
            {
                "type": "count",
                "scope": "vdom",
                "path": "/root/leaf_81/leaf_82",
                "checks": {"gt": 1, "eq": 2, "lt": 3},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_count_failed(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:count with failures"""
        checks = [
            {
                "type": "count",
                "scope": "vdom",
                "path": "/leaf_81/leaf_82",
                "checks": {"gt": 100, "eq": 100, "lt": 0},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 3

    @staticmethod
    def test_check_config_count_not_a_list(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:count when configuration is not a list"""
        checks = [
            {
                "type": "count",
                "scope": "vdom",
                "path": "/root/leaf_81/",
                "checks": {"gt": 1, "eq": 2, "lt": 3},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    # start tests for config_check type: exists

    @staticmethod
    def test_check_config_exist(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:exist"""
        checks = [
            {
                "type": "exist",
                "scope": "global",
                "path": "/system/global",
                "checks": {"option_1": True, "option_2": True, "option_99": False},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_exist_failed(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:exist with failures"""
        checks = [
            {
                "type": "exist",
                "scope": "global",
                "path": "/system/global",
                "checks": {"option_1": False, "option_2": False, "option_99": True},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 3

    # start tests for config_check type: value

    @staticmethod
    def test_check_config_value(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:value"""
        checks = [
            {
                "type": "value",
                "scope": "global",
                "path": "/system/global",
                "checks": {"option_1": "value_1", "option_2": "value_2", "option_3": 3},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_value_failed(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:value with failures"""
        checks = [
            {
                "type": "value",
                "scope": "global",
                "path": "/system/global",
                "checks": {"option_1": "wrong", "option_2": "wrong", "option_3": 0},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 3

    @staticmethod
    def test_check_config_value_invalid_checks_key(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:value with an invalid key in checks"""
        checks = [
            {
                "type": "value",
                "scope": "global",
                "path": "/system/global",
                "checks": {"dummy_1": "", "dummy_2": ""},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 2

    # start tests for config_check type: value_in_list

    @staticmethod
    def test_check_config_value_in_list(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:value_in_list"""
        checks = [
            {
                "type": "value_in_list",
                "scope": "vdom",
                "path": "/leaf_81/leaf_82",
                "checks": {"id": 1},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 2

    @staticmethod
    def test_check_config_value_in_list_inverse(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:value_in_list with inverse"""
        checks = [
            {
                "type": "value_in_list",
                "scope": "vdom",
                "path": "/root/leaf_81/leaf_82",
                "inverse": True,
                "checks": {"id": 99},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 0

    @staticmethod
    def test_check_config_value_in_list_failed(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:value_in_list failed"""
        checks = [
            {
                "type": "value_in_list",
                "scope": "vdom",
                "path": "/leaf_81/leaf_82",
                "checks": {"id": 99},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 3

    @staticmethod
    def test_check_config_value_in_list_inverse_failed(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check for type:value_in_list failed with inverse"""
        checks = [
            {
                "type": "value_in_list",
                "scope": "vdom",
                "path": "/leaf_81/leaf_82",
                "inverse": True,
                "checks": {"id": 1},
            }
        ]
        conf_check = FortiGateConfigCheck(config_vdom, checks)
        conf_check.execute_checks()
        assert len(conf_check.results) == 1
