"""
Test fgt tools config info
"""

import pytest

from fotoobo.exceptions.exceptions import GeneralWarning
from fotoobo.tools.fgt.config import info


@pytest.mark.parametrize(
    "file",
    (
        pytest.param("tests/data/fortigate_config_single.conf", id="single"),
        pytest.param("tests/data/fortigate_config_vdom.conf", id="vdom"),
    ),
)
def test_info(file: str) -> None:
    """test the info utility"""
    infos = info(file)
    assert infos[0].buildno == "8303"


@pytest.mark.parametrize(
    "file",
    (
        pytest.param("tests/data/fortigate_config_empty.conf", id="single"),
        pytest.param("tests/data/", id="vdom"),
    ),
)
def test_info_empty(file: str) -> None:
    """test the info utility with directory and empty configuration file"""
    with pytest.raises(GeneralWarning, match=r"There is no info in"):
        info(file)


def test_info_no_files_in_dir() -> None:
    """test the info utility with directory and empty configuration file"""
    with pytest.raises(GeneralWarning, match=r"there are no configuration files"):
        info("tests/")
