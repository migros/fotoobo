"""The pytest global fixtures"""

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope="session")
def session_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Creates and maintains a session temp directory.

    This directory is persistent over th whole test session and for every test. So be sure to not
    rely on a particular content of this dir. Only use it for long term temp files.
    """

    return tmp_path_factory.mktemp("session_")


@pytest.fixture(scope="module")
def module_dir(tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest) -> Path:
    """Creates and maintains a module temp directory.

    This directory is persistent over all tests in a module. Every test in that module accesses
    this same directory so pbe aware to not rely on a particular content of thos dir.
    """

    return tmp_path_factory.mktemp(f"module_{request.module.__name__}_")


@pytest.fixture(scope="function")
def function_dir(tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest) -> Path:
    """Creates and maintains a function temp directory.

    This directory is created for every single test. Tests functions or methods can not access
    others tests or functions directories.
    """

    return tmp_path_factory.mktemp(
        f"function_{request.module.__name__}_{request.function.__name__}_"
    )


@pytest.fixture(
    params=[
        pytest.param("-h", id="with -h"),
        pytest.param("--help", id="with --help"),
    ]
)
def help_args(request: pytest.FixtureRequest) -> Any:
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
def help_args_with_none(request: pytest.FixtureRequest) -> Any:
    """A parametrized fixture to return '', '-h' and '--help'

    Use this fixture when a command can't be invoked without any arguments. In this case invoking
    the command without any argument shows the help.
    This is when no_args_is_help=True
    """
    return request.param
