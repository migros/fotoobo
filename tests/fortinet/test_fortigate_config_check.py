"""
Test the FortiGate config check class
"""
from pathlib import Path
from typing import Any, Dict, List

import pytest

from fotoobo.exceptions import GeneralError
from fotoobo.fortinet.fortigate_config import FortiGateConfig
from fotoobo.fortinet.fortigate_config_check import FortiGateConfigCheck
from fotoobo.helpers.files import load_yaml_file
from fotoobo.helpers.result import Result


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

    # start tests with different configuration files

    @staticmethod
    def test_check_config_single_global(conf_file_single: Path, checks_file: Path) -> None:
        """Do a configuration check with a single VDOM FortiGate configuration file"""
        result = Result[Any]()
        config = FortiGateConfig.parse_configuration_file(conf_file_single)
        conf_check = FortiGateConfigCheck(config, load_yaml_file(checks_file), result)
        conf_check.execute_checks()
        assert len(result.get_messages(config.info.hostname)) == 0

    @staticmethod
    def test_check_config_vdom_global(conf_file_vdom: Path, checks_file: Path) -> None:
        """Do a configuration check with a multiple VDOM FortiGate configuration file"""
        result = Result[Any]()
        config = FortiGateConfig.parse_configuration_file(conf_file_vdom)
        conf_check = FortiGateConfigCheck(config, load_yaml_file(checks_file), result)
        conf_check.execute_checks()
        assert len(result.get_messages(config.info.hostname)) == 2

    # start generic tests for config_check with invalid check definition

    @staticmethod
    def test_check_config_empty_bundle_file(config_vdom: FortiGateConfig) -> None:
        """Do a configuration check with an empty bundle file"""
        checks = None
        result = Result[Any]()
        conf_check = FortiGateConfigCheck(config_vdom, checks, result)
        try:
            conf_check.execute_checks()
            assert False
        except GeneralError as err:
            assert True
            assert "there are no checks defined" in err.message

    @staticmethod
    @pytest.mark.parametrize(
        "checks,expected_messages_count",
        (
            pytest.param(
                [
                    {
                        "scope": "vdom",
                        "path": "/root/leaf_81/leaf_82",
                        "checks": {"eq": 2},
                    }
                ],
                0,
                id="check key type missing",
            ),
            pytest.param(
                [
                    {
                        "type": "dummy",
                        "scope": "vdom",
                        "path": "/root/leaf_81/leaf_82",
                        "checks": {"eq": 2},
                    }
                ],
                0,
                id="check key 'type' invalid",
            ),
            pytest.param(
                [
                    {
                        "type": "count",
                        "scope": "vdom",
                        "path": "/root/leaf_81/leaf_82",
                        "checks": {"eq": 2},
                    }
                ],
                0,
                id="check key 'scope' missing",
            ),
            pytest.param(
                [
                    {
                        "type": "count",
                        "scope": "vdom",
                        "checks": {"eq": 2},
                    }
                ],
                0,
                id="check key 'path' missing",
            ),
            pytest.param(
                [
                    {
                        "type": "count",
                        "scope": "vdom",
                        "path": "/root/leaf_81/leaf_82",
                    }
                ],
                0,
                id="check key 'checks' missing",
            ),
            pytest.param(
                [
                    {
                        "type": "count",
                        "scope": "vdom",
                        "path": "/root/leaf_81/leaf_82",
                        "checks": {},
                    }
                ],
                0,
                id="check key 'checks' empty",
            ),
            pytest.param([{"type": "count"}], 0, id="multiple check keys missing"),
            pytest.param(
                [
                    {
                        "type": "count",
                        "scope": "vdom",
                        "path": "/root/leaf_81/leaf_82",
                        "checks": {"gt": 1, "eq": 2, "lt": 3},
                    }
                ],
                0,
                id="check for type 'count'",
            ),
            pytest.param(
                [
                    {
                        "type": "count",
                        "scope": "vdom",
                        "path": "/leaf_81/leaf_82",
                        "checks": {"gt": 100, "eq": 100, "lt": 0},
                    }
                ],
                3,
                id="check for type 'count' with failures",
            ),
            pytest.param(
                [
                    {
                        "type": "count",
                        "scope": "vdom",
                        "path": "/root/leaf_81/",
                        "checks": {"gt": 1, "eq": 2, "lt": 3},
                    }
                ],
                0,
                id="check for type 'count' when configuration is not a list",
            ),
            pytest.param(
                [
                    {
                        "type": "exist",
                        "scope": "global",
                        "path": "/system/global",
                        "checks": {"option_1": True, "option_2": True, "option_99": False},
                    }
                ],
                0,
                id="check for type 'exist'",
            ),
            pytest.param(
                [
                    {
                        "type": "exist",
                        "scope": "global",
                        "path": "/system/global",
                        "checks": {"option_1": False, "option_2": False, "option_99": True},
                    }
                ],
                3,
                id="check for type 'exist' with failures",
            ),
            pytest.param(
                [
                    {
                        "type": "value",
                        "scope": "global",
                        "path": "/system/global",
                        "checks": {"option_1": "value_1", "option_2": "value_2", "option_3": 3},
                    }
                ],
                0,
                id="check for type 'value'",
            ),
            pytest.param(
                [
                    {
                        "type": "value",
                        "scope": "global",
                        "path": "/system/global",
                        "checks": {"option_1": "wrong", "option_2": "wrong", "option_3": 0},
                    }
                ],
                3,
                id="check for type 'value' with failures",
            ),
            pytest.param(
                [
                    {
                        "type": "value",
                        "scope": "global",
                        "path": "/system/global",
                        "checks": {"dummy_1": "", "dummy_2": ""},
                    }
                ],
                2,
                id="check for type 'value' with an invalid key in checks",
            ),
            pytest.param(
                [
                    {
                        "type": "value_in_list",
                        "scope": "vdom",
                        "path": "/leaf_81/leaf_82",
                        "checks": {"id": 1},
                    }
                ],
                2,
                id="check for type 'value_in_list'",
            ),
            pytest.param(
                [
                    {
                        "type": "value_in_list",
                        "scope": "vdom",
                        "path": "/root/leaf_81/leaf_82",
                        "inverse": True,
                        "checks": {"id": 99},
                    }
                ],
                0,
                id="check for type 'value_in_list' with inverse",
            ),
            pytest.param(
                [
                    {
                        "type": "value_in_list",
                        "scope": "vdom",
                        "path": "/leaf_81/leaf_82",
                        "checks": {"id": 99},
                    }
                ],
                3,
                id="check for type 'value_in_list' failed",
            ),
            pytest.param(
                [
                    {
                        "type": "value_in_list",
                        "scope": "vdom",
                        "path": "/leaf_81/leaf_82",
                        "inverse": True,
                        "checks": {"id": 1},
                    }
                ],
                1,
                id="check for type 'value_in_list failed with inverse",
            ),
        ),
    )
    def test_check_config_generic_missing_type(
        checks: List[Dict[str, Any]], expected_messages_count: int, config_vdom: FortiGateConfig
    ) -> None:
        """
        Test the configuration check functionality
        Args:
            checks:
            expected_messages_count:
            config_vdom:

        Returns:

        """
        result = Result[Any]()

        conf_check = FortiGateConfigCheck(config_vdom, checks, result)
        conf_check.execute_checks()

        assert len(result.get_messages(config_vdom.info.hostname)) == expected_messages_count
