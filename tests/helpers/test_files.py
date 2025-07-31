"""
Test_files helper module.
"""

# pylint: disable=redefined-outer-name

import os
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from fotoobo.exceptions import GeneralError
from fotoobo.helpers.files import (
    create_dir,
    file_to_ftp,
    file_to_zip,
    load_json_file,
    load_yaml_file,
    save_json_file,
    save_txt_file,
    save_yaml_file,
)
from fotoobo.inventory.generic import GenericDevice


@pytest.fixture
def test_data_dict() -> dict[str, Any]:
    """
    Return a FortiGate config dictionary.
    """

    return {
        "key1": "value1",
        "key2": [{"key3": "value3", "key4": "value4"}, {"key5": "value5", "key6": "value6"}],
    }


@pytest.fixture
def test_data_list() -> list[Any]:
    """
    Return a FortiGate config dictionary.
    """

    return ["value1", "value2", 3, 4]


@pytest.fixture
def json_test_file(module_dir: Path) -> Path:
    """
    Returns the filename of a json test file.
    """

    return module_dir / "test_file.json"


@pytest.fixture
def txt_test_file(module_dir: Path) -> Path:
    """
    Returns the filename of a txt test file.
    """

    return module_dir / "test_file.txt"


@pytest.fixture
def yaml_test_file(module_dir: Path) -> Path:
    """
    Returns the filename of a yaml test file.
    """

    return module_dir / "test_file.yaml"


@pytest.mark.parametrize(
    "file, mock, expected",
    (
        pytest.param(
            Path("tests/data/fortigate_config_empty.conf"),
            Mock(return_value="226 Transfer complete."),
            0,
            id="file to ftp ok",
        ),
        pytest.param(
            Path("tests/data/dummy"),
            Mock(),
            666,
            id="file to ftp with inexistent file",
        ),
        pytest.param(
            Path("tests/data/fortigate_config_empty.conf"),
            Mock(return_value="222 Some unknown error"),
            222,
            id="file to ftp with unknown error",
        ),
    ),
)
def test_file_to_ftp(file: Path, mock: Mock, expected: int, monkeypatch: MonkeyPatch) -> None:
    """
    Test the file_to_ftp function.
    """

    # Arrange
    monkeypatch.setattr("fotoobo.helpers.files.FTP.cwd", Mock(return_value=""))
    monkeypatch.setattr("fotoobo.helpers.files.FTP.sendcmd", Mock(return_value=""))
    monkeypatch.setattr("fotoobo.helpers.files.FTP.storbinary", mock)

    # Act & Assert
    assert file_to_ftp(file, GenericDevice(username="", password="", directory="")) == expected


def test_file_to_zip(json_test_file: Path, function_dir: Path) -> None:
    """
    Test the file_to_zip function.
    """

    # Arrange
    assert not json_test_file.is_file()
    json_test_file.write_text("Test", encoding="UTF-8")
    assert json_test_file.is_file()
    dst = function_dir / "test.zip"
    assert not dst.is_file()

    # Act
    file_to_zip(json_test_file, dst, 9)

    # Assert
    assert dst.is_file()


@pytest.mark.parametrize(
    "zip_level",
    (
        pytest.param(-1, id="zip level -1"),
        pytest.param(10, id="zip level 10"),
    ),
)
def test_file_to_zip_invalid_level(zip_level: int) -> None:
    """
    Test the file_to_zip function with invalid zip level.
    """

    # Act & Assert
    with pytest.raises(GeneralError, match=r"zip level must between 0 and 9"):
        file_to_zip(Path(""), Path(""), zip_level)


# Start testing the json file_helper functions


def test_save_json_file_dict(json_test_file: Path, test_data_dict: dict[str, Any]) -> None:
    """
    Test the save_json_file function.
    """

    # Act
    save_json_file(json_test_file, test_data_dict)

    # Assert
    assert json_test_file.is_file()
    content = json_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    expect = """{
        "key1": "value1",
        "key2": [
            { "key3": "value3", "key4": "value4"},
            { "key5": "value5", "key6": "value6"}
        ]
    }"""
    expect = expect.replace(" ", "").replace("\n", "")
    assert content == expect


def test_load_json_file_dict(json_test_file: Path, test_data_dict: dict[str, Any]) -> None:
    """
    Test the load_json_file function.
    """

    # Arrange
    assert json_test_file.is_file()

    # Act
    content = load_json_file(json_test_file)

    # Assert
    assert content == test_data_dict


def test_save_json_file_list(json_test_file: Path, test_data_list: list[str]) -> None:
    """
    Test the save_json_file function.
    """

    # Act
    save_json_file(json_test_file, test_data_list)

    # Assert
    assert json_test_file.is_file()
    content = json_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    expect = """["value1", "value2", 3, 4]"""
    expect = expect.replace(" ", "").replace("\n", "")
    assert content == expect


def test_load_json_file_list(json_test_file: Path, test_data_list: list[str]) -> None:
    """
    Test the load_json_file function.
    """

    # Arrange
    assert json_test_file.is_file()

    # Act
    content = load_json_file(json_test_file)

    # Assert
    assert content == test_data_list


def test_save_json_file_empty_dict(json_test_file: Path) -> None:
    """
    Test the save_json_file function with an empty dict.
    """

    # Arrange
    os.remove(json_test_file)
    assert not json_test_file.is_file()

    # Act
    save_json_file(json_test_file, {})

    # Assert
    assert json_test_file.is_file()
    assert json_test_file.stat().st_size == 2
    with open(json_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace(" ", "").replace("\n", "")

    assert content == "{}"


def test_load_json_file_empty_dict(json_test_file: Path) -> None:
    """
    Test the load_json_file function with an empty dict.
    """

    # Arrange
    assert json_test_file.is_file()

    # Act
    content = load_json_file(json_test_file)

    # Assert
    assert content == {}


def test_save_json_file_empty_list(json_test_file: Path) -> None:
    """
    Test the save_json_file function with an empty list.
    """

    # Arrange
    os.remove(json_test_file)
    assert not json_test_file.is_file()

    # Act
    save_json_file(json_test_file, [])

    # Assert
    assert json_test_file.is_file()
    assert json_test_file.stat().st_size == 2
    content = json_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    assert content == "[]"


def test_load_json_file_empty_list(json_test_file: Path) -> None:
    """
    Test the load_json_file function with an empty list.
    """

    # Arrange
    assert json_test_file.is_file()

    # Act
    content = load_json_file(json_test_file)

    # Assert
    assert content == []


def test_save_json_file_unsupported_type(json_test_file: Path) -> None:
    """
    Test the save_json_file function with data of unsupported type.
    """

    # Arrange
    os.remove(json_test_file)

    # Act & Assert
    assert not json_test_file.is_file()
    assert not save_json_file(json_test_file, None)  # type: ignore
    assert not save_json_file(json_test_file, 42)  # type: ignore
    assert not save_json_file(json_test_file, "42")  # type: ignore


def test_load_json_file_non_exist(json_test_file: Path) -> None:
    """
    Test the load_json_file function with not existing file.
    """

    # Arrange
    assert not json_test_file.is_file()

    # Act & Assert
    assert not load_json_file(json_test_file)


# Start testing the yaml file_helper functions


def test_save_yaml_file_dict(yaml_test_file: Path, test_data_dict: dict[str, Any]) -> None:
    """
    Test the save_yaml_file function.
    """

    # Act
    save_yaml_file(yaml_test_file, test_data_dict)

    # Assert
    assert yaml_test_file.is_file()
    content = yaml_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    expect = "key1:value1key2:-key3:value3key4:value4-key5:value5key6:value6"
    assert content == expect


def test_load_yaml_file_dict(yaml_test_file: Path, test_data_dict: dict[str, Any]) -> None:
    """
    Test the load_yaml_file function.
    """

    # Arrange
    assert yaml_test_file.is_file()

    # Act
    content = load_yaml_file(yaml_test_file)

    # Assert
    assert content == test_data_dict


def test_save_yaml_file_list(yaml_test_file: Path, test_data_list: list[str]) -> None:
    """
    Test the save_yaml_file function.
    """

    # Act
    save_yaml_file(yaml_test_file, test_data_list)

    # Assert
    assert yaml_test_file.is_file()
    content = yaml_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    expect = "-value1-value2-3-4"
    expect = expect.replace(" ", "").replace("\n", "")
    assert content == expect


def test_load_yaml_file_list(yaml_test_file: Path, test_data_list: list[str]) -> None:
    """
    Test the load_yaml_file function.
    """

    # Arrange
    assert yaml_test_file.is_file()

    # Act
    content = load_yaml_file(yaml_test_file)

    # Assert
    assert content == test_data_list


def test_save_yaml_file_empty_dict(yaml_test_file: Path) -> None:
    """
    Test the save_yaml_file function with an empty dict.
    """

    # Arrange
    os.remove(yaml_test_file)
    assert not yaml_test_file.is_file()

    # Act
    save_yaml_file(yaml_test_file, {})

    # Assert
    assert yaml_test_file.is_file()
    assert yaml_test_file.stat().st_size == 3
    content = yaml_test_file.read_text(encoding="UTF-8").replace("\n", "")
    assert content == "{}"


def test_load_yaml_file_empty_dict(yaml_test_file: Path) -> None:
    """
    Test the load_yaml_file function with an empty dict.
    """

    # Arrange
    assert yaml_test_file.is_file()

    # Act
    content = load_yaml_file(yaml_test_file)

    # Assert
    assert content == {}


def test_save_yaml_file_empty_list(yaml_test_file: Path) -> None:
    """
    Test the save_yaml_file function with an empty list.
    """

    # Arrange
    os.remove(yaml_test_file)
    assert not yaml_test_file.is_file()

    # Act
    save_yaml_file(yaml_test_file, [])

    # Assert
    assert yaml_test_file.is_file()
    assert yaml_test_file.stat().st_size == 3
    content = yaml_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    assert content == "[]"


def test_load_yaml_file_empty_list(yaml_test_file: Path) -> None:
    """
    Test the load_yaml_file function with an empty list.
    """

    # Arrange
    assert yaml_test_file.is_file()

    # Act
    content = load_yaml_file(yaml_test_file)

    # Assert
    assert content == []


def test_save_yaml_file_unsupported_type(yaml_test_file: Path) -> None:
    """
    Test the save_yaml_file function with data of unsupported type.
    """

    # Arrange
    os.remove(yaml_test_file)

    # Act & Assert
    assert not yaml_test_file.is_file()
    assert not save_yaml_file(yaml_test_file, None)  # type: ignore
    assert not save_yaml_file(yaml_test_file, 42)  # type: ignore
    assert not save_yaml_file(yaml_test_file, "42")  # type: ignore


def test_load_yaml_file_non_exist(yaml_test_file: Path) -> None:
    """
    Test the load_yaml_file function with not existing file.
    """

    # Arrange
    assert not yaml_test_file.is_file()

    # Act & Assert
    assert not load_yaml_file(yaml_test_file)


# Start testing the txt file_helper functions


@pytest.mark.parametrize(
    "content",
    (
        pytest.param("LINE_1", id="file with one line"),
        pytest.param("", id="empty file"),
        pytest.param("LINE_1\nLINE_2\nLINE_3", id="file with multiple lines"),
    ),
)
def test_save_txt_file(txt_test_file: Path, content: str) -> None:
    """
    Test the save_json_file function.
    """

    # Arrange
    assert not txt_test_file.is_file()

    # Act
    save_txt_file(txt_test_file, content)

    # Assert
    assert txt_test_file.is_file()
    new_content = txt_test_file.read_text(encoding="UTF-8")
    assert new_content == content
    txt_test_file.unlink()
    assert not txt_test_file.is_file()


# Start testing the create_dir function


def test_create_dir_for_new_directory(function_dir: Path) -> None:
    """
    Test create_dir in an existing directory.
    """

    # Arrange
    directory = function_dir / "test_dir_1"
    assert not directory.is_dir()

    # Act
    create_dir(directory)

    # Assert
    assert directory.is_dir()


def test_create_dir_for_existing_directory(function_dir: Path) -> None:
    """
    Test create_dir in an existing directory when the directory to create already exists.
    """

    # Arrange
    directory = function_dir / "test_dir_2"
    assert not directory.is_dir()
    directory.mkdir()
    assert directory.is_dir()

    # Act
    create_dir(directory)

    # Assert
    assert directory.is_dir()


def test_create_dir_for_sub_sub_directory(function_dir: Path) -> None:
    """
    Test create_dir when trying to create a sub, subdirectory.
    """

    # Arrange
    directory = function_dir / "test_dir_3" / "test_dir_4"

    # Act
    create_dir(directory)

    # Assert
    assert directory.is_dir()


def test_create_dir_with_os_error(monkeypatch: MonkeyPatch) -> None:
    """
    Test create_dir when an OSError exception is raised.
    """

    # Arrange
    mkdir_mock = Mock(side_effect=OSError())
    monkeypatch.setattr("fotoobo.helpers.files.Path.mkdir", mkdir_mock)

    # Act & Assert
    with pytest.raises(GeneralError, match=r"Unable to create directory dummy"):
        create_dir(Path("dummy"))

    mkdir_mock.assert_called_once_with(parents=True)
