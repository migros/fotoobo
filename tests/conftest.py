"""The pytest global fixtures"""

import pytest


@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):  # type: ignore # (it's a pathlib.Path object)
    """creates and maintains a session temp directory"""
    return tmp_path_factory.mktemp("tests_")
