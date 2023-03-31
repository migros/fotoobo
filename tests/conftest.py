"""The pytest global fixtures"""

from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory


@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory: TempPathFactory) -> Path:
    """creates and maintains a session temp directory"""
    return tmp_path_factory.mktemp("tests_")
