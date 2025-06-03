"""The pytest global fixtures"""

from pathlib import Path
from typing import Any

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.tmpdir import TempPathFactory


@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory: TempPathFactory) -> Path:
    """creates and maintains a session temp directory"""
    return tmp_path_factory.mktemp("tests_")


@pytest.fixture(
    params=[
        pytest.param("-h", id="with -h"),
        pytest.param("--help", id="with --help"),
    ]
)
def help_args(request: FixtureRequest) -> Any:
    """A parametrized fixture to return '-h' and '--help'

    Use this fixture when a command can be invoked without any arguments. In this case invoking the
    command without any argument starts the command instead of showing the help.
    This is when no_args_is_help=False which is default"""
    return request.param


@pytest.fixture(
    params=[
        pytest.param("", id="no help arg"),
        pytest.param("-h", id="with -h"),
        pytest.param("--help", id="with --help"),
    ]
)
def help_args_with_none(request: FixtureRequest) -> Any:
    """A parametrized fixture to return '', '-h' and '--help'

    Use this fixture when a command can't be invoked without any arguments. In this case invoking
    the command without any argument shows the help.
    This is when no_args_is_help=True
    """
    return request.param
