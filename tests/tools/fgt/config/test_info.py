"""
Test fgt tools config info
"""

from pathlib import Path

import pytest

from fotoobo.exceptions.exceptions import GeneralWarning
from fotoobo.tools.fgt.config import info


@pytest.mark.parametrize(
    "file",
    (
        pytest.param(Path("tests/data/fortigate_config_single.conf"), id="single"),
        pytest.param(Path("tests/data/fortigate_config_vdom.conf"), id="vdom"),
    ),
)
def test_info(file: Path) -> None:
    """test the info utility"""
    infos = info(file)
    assert infos.get_result("HOSTNAME UNKNOWN").buildno == "8303"


@pytest.mark.parametrize(
    "file",
    (
        pytest.param(Path("tests/data/fortigate_config_empty.conf"), id="single"),
        pytest.param(Path("tests/data/"), id="vdom"),
    ),
)
def test_info_empty(file: Path) -> None:
    """test the info utility with directory and empty configuration file"""
    with pytest.raises(GeneralWarning, match=r"There is no info in"):
        info(file)


def test_info_no_files_in_dir() -> None:
    """test the info utility with directory and empty configuration file"""
    with pytest.raises(GeneralWarning, match=r"there are no configuration files"):
        info(Path("tests/"))
