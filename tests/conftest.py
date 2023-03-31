"""The pytest global fixtures"""

from pathlib import Path

import _pytest
import pytest


@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory: _pytest.tmpdir.TempPathFactory) -> Path:
    """creates and maintains a session temp directory"""
    return tmp_path_factory.mktemp("tests_")
