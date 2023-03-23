"""
test_file_helper
"""
# pylint: disable=redefined-outer-name

import os
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralError
from fotoobo.helpers.files import (
    create_dir,
    file_to_ftp,
    file_to_zip,
    load_json_file,
    load_yaml_file,
    save_json_file,
    save_with_template,
    save_yaml_file,
)
from fotoobo.inventory.generic import GenericDevice


@pytest.fixture
def test_data_dict() -> Dict[str, Any]:
    """Return a FortiGate config dict"""
    return {
        "key1": "value1",
        "key2": [{"key3": "value3", "key4": "value4"}, {"key5": "value5", "key6": "value6"}],
    }


@pytest.fixture
def test_data_list() -> List[Any]:
    """Return a FortiGate config dict"""
    return ["value1", "value2", 3, 4]


@pytest.fixture
def json_test_file(temp_dir: str) -> str:
    """Returns the filename of a json test file"""
    return os.path.join(temp_dir, "test_file.json")


@pytest.fixture
def yaml_test_file(temp_dir: str) -> str:
    """Returns the filename of a yaml test file"""
    return os.path.join(temp_dir, "test_file.yaml")


@pytest.mark.parametrize(
    "file, mock, expected",
    (
        pytest.param(
            "tests/data/fortigate_config_empty.conf",
            MagicMock(return_value="226 Transfer complete."),
            0,
            id="file to ftp ok",
        ),
        pytest.param(
            "tests/data/dummy",
            MagicMock(),
            666,
            id="file to ftp with inexistent file",
        ),
        pytest.param(
            "tests/data/fortigate_config_empty.conf",
            MagicMock(return_value="222 Some unknown error"),
            222,
            id="file to ftp with unknown error",
        ),
    ),
)
def test_file_to_ftp(file: str, mock: MagicMock, expected: int, monkeypatch: MonkeyPatch) -> None:
    """Test the file_to_ftp function"""
    monkeypatch.setattr("fotoobo.helpers.files.FTP.cwd", MagicMock(return_value=""))
    monkeypatch.setattr("fotoobo.helpers.files.FTP.sendcmd", MagicMock(return_value=""))
    monkeypatch.setattr("fotoobo.helpers.files.FTP.storbinary", mock)
    assert file_to_ftp(file, GenericDevice(username="", password="", directory="")) == expected


def test_file_to_zip(json_test_file: str, temp_dir: str) -> None:
    """Test the file_to_zip function"""
    assert not os.path.isfile(json_test_file)
    with open(json_test_file, "w", encoding="UTF-8") as test_file:
        test_file.write("Test")
    assert os.path.isfile(json_test_file)
    dst = os.path.join(temp_dir, "test.zip")
    assert not os.path.isfile(dst)
    file_to_zip(json_test_file, dst, 9)
    assert os.path.isfile(dst)


@pytest.mark.parametrize(
    "zip_level",
    (
        pytest.param(-1, id="zip level -1"),
        pytest.param(10, id="zip level 10"),
    ),
)
def test_file_to_zip_invalid_level(zip_level: int) -> None:
    """Test the file_to_zip function with invalid zip level"""
    with pytest.raises(GeneralError, match=r"zip level must between 0 and 9"):
        file_to_zip("", "", zip_level)


# Start testing the json file_helper functions


def test_save_json_file_dict(json_test_file: str, test_data_dict: Dict[str, Any]) -> None:
    """Test the save_json_file function"""
    save_json_file(json_test_file, test_data_dict)
    assert os.path.isfile(json_test_file)
    with open(json_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace(" ", "").replace("\n", "")
    expect = """{
        "key1": "value1",
        "key2": [
            { "key3": "value3", "key4": "value4"},
            { "key5": "value5", "key6": "value6"}
        ]
    }"""
    expect = expect.replace(" ", "").replace("\n", "")
    assert content == expect


def test_load_json_file_dict(json_test_file: str, test_data_dict: Dict[str, Any]) -> None:
    """Test the load_json_file function"""
    assert os.path.isfile(json_test_file)
    content = load_json_file(json_test_file)
    assert content == test_data_dict


def test_save_json_file_list(json_test_file: str, test_data_list: List[str]) -> None:
    """Test the save_json_file function"""
    save_json_file(json_test_file, test_data_list)
    assert os.path.isfile(json_test_file)
    with open(json_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace(" ", "").replace("\n", "")
    expect = """["value1", "value2", 3, 4]"""
    expect = expect.replace(" ", "").replace("\n", "")
    assert content == expect


def test_load_json_file_list(json_test_file: str, test_data_list: List[str]) -> None:
    """Test the load_json_file function"""
    assert os.path.isfile(json_test_file)
    content = load_json_file(json_test_file)
    assert content == test_data_list


def test_save_json_file_empty_dict(json_test_file: str) -> None:
    """Test the save_json_file function with an empty dict"""
    os.remove(json_test_file)
    assert not os.path.isfile(json_test_file)
    save_json_file(json_test_file, {})
    assert os.path.isfile(json_test_file)
    assert os.path.getsize(json_test_file) == 2
    with open(json_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace(" ", "").replace("\n", "")
    assert content == "{}"


def test_load_json_file_empty_dict(json_test_file: str) -> None:
    """Test the load_json_file function with an empty dict"""
    assert os.path.isfile(json_test_file)
    content = load_json_file(json_test_file)
    assert content == {}


def test_save_json_file_empty_list(json_test_file: str) -> None:
    """Test the save_json_file function with an empty list"""
    os.remove(json_test_file)
    assert not os.path.isfile(json_test_file)
    save_json_file(json_test_file, [])
    assert os.path.isfile(json_test_file)
    assert os.path.getsize(json_test_file) == 2
    with open(json_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace(" ", "").replace("\n", "")
    assert content == "[]"


def test_load_json_file_empty_list(json_test_file: str) -> None:
    """Test the load_json_file function with an empty list"""
    assert os.path.isfile(json_test_file)
    content = load_json_file(json_test_file)
    assert content == []


def test_save_json_file_unsupported_type(json_test_file: str) -> None:
    """Test the save_json_file function with data of unsupported type"""
    os.remove(json_test_file)
    assert not os.path.isfile(json_test_file)
    assert not save_json_file(json_test_file, None)  # type: ignore
    assert not save_json_file(json_test_file, 42)  # type: ignore
    assert not save_json_file(json_test_file, "42")  # type: ignore


def test_load_json_file_non_exist(json_test_file: str) -> None:
    """Test the load_json_file function with non existing file"""
    assert not os.path.isfile(json_test_file)
    assert not load_json_file(json_test_file)


# Start testing the yaml file_helper functions


def test_save_yaml_file_dict(yaml_test_file: str, test_data_dict: Dict[str, Any]) -> None:
    """Test the save_yaml_file function"""
    save_yaml_file(yaml_test_file, test_data_dict)
    assert os.path.isfile(yaml_test_file)
    with open(yaml_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace(" ", "").replace("\n", "")
    expect = "key1:value1key2:-key3:value3key4:value4-key5:value5key6:value6"
    assert content == expect


def test_load_yaml_file_dict(yaml_test_file: str, test_data_dict: Dict[str, Any]) -> None:
    """Test the load_yaml_file function"""
    assert os.path.isfile(yaml_test_file)
    content = load_yaml_file(yaml_test_file)
    assert content == test_data_dict


def test_save_yaml_file_list(yaml_test_file: str, test_data_list: List[str]) -> None:
    """Test the save_yaml_file function"""
    save_yaml_file(yaml_test_file, test_data_list)
    assert os.path.isfile(yaml_test_file)
    with open(yaml_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace(" ", "").replace("\n", "")
    expect = "-value1-value2-3-4"
    expect = expect.replace(" ", "").replace("\n", "")
    assert content == expect


def test_load_yaml_file_list(yaml_test_file: str, test_data_list: List[str]) -> None:
    """Test the load_yaml_file function"""
    assert os.path.isfile(yaml_test_file)
    content = load_yaml_file(yaml_test_file)
    assert content == test_data_list


def test_save_yaml_file_empty_dict(yaml_test_file: str) -> None:
    """Test the save_yaml_file function with an empty dict"""
    os.remove(yaml_test_file)
    assert not os.path.isfile(yaml_test_file)
    save_yaml_file(yaml_test_file, {})
    assert os.path.isfile(yaml_test_file)
    assert os.path.getsize(yaml_test_file) == 3
    with open(yaml_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace("\n", "")
    assert content == "{}"


def test_load_yaml_file_empty_dict(yaml_test_file: str) -> None:
    """Test the load_yaml_file function with an empty dict"""
    assert os.path.isfile(yaml_test_file)
    content = load_yaml_file(yaml_test_file)
    assert content == {}


def test_save_yaml_file_empty_list(yaml_test_file: str) -> None:
    """Test the save_yaml_file function with an empty list"""
    os.remove(yaml_test_file)
    assert not os.path.isfile(yaml_test_file)
    save_yaml_file(yaml_test_file, [])
    assert os.path.isfile(yaml_test_file)
    assert os.path.getsize(yaml_test_file) == 3
    with open(yaml_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace(" ", "").replace("\n", "")
    assert content == "[]"


def test_load_yaml_file_empty_list(yaml_test_file: str) -> None:
    """Test the load_yaml_file function with an empty list"""
    assert os.path.isfile(yaml_test_file)
    content = load_yaml_file(yaml_test_file)
    assert content == []


def test_save_yaml_file_unsupported_type(yaml_test_file: str) -> None:
    """Test the save_yaml_file function with data of unsupported type"""
    os.remove(yaml_test_file)
    assert not os.path.isfile(yaml_test_file)
    assert not save_yaml_file(yaml_test_file, None)  # type: ignore
    assert not save_yaml_file(yaml_test_file, 42)  # type: ignore
    assert not save_yaml_file(yaml_test_file, "42")  # type: ignore


def test_load_yaml_file_non_exist(yaml_test_file: str) -> None:
    """Test the load_yaml_file function with non existing file"""
    assert not os.path.isfile(yaml_test_file)
    assert not load_yaml_file(yaml_test_file)


# Start testing the create_dir function


def test_create_dir_for_new_directory(temp_dir: str) -> None:
    """Test create_dir in an existing directory"""
    directory = os.path.join(temp_dir, "testdir_1")
    assert not os.path.isdir(directory)
    create_dir(directory)
    assert os.path.isdir(directory)


def test_create_dir_for_existing_directory(temp_dir: str) -> None:
    """Test create_dir in an existing directory when the directory to create already exists"""
    directory = os.path.join(temp_dir, "testdir_2")
    assert not os.path.isdir(directory)
    os.mkdir(directory)
    assert os.path.isdir(directory)
    create_dir(directory)
    assert os.path.isdir(directory)


def test_create_dir_for_sub_sub_directory(temp_dir: str) -> None:
    """Test create_dir when trying to create a sub, sub directory"""
    directory = os.path.join(temp_dir, "testdir_3/testdir_4")
    assert not os.path.isdir(directory)
    with pytest.raises(GeneralError, match=r"unable to create directory .*/testdir_3/testdir_4"):
        create_dir(directory)


def test_create_dir_with_os_error(monkeypatch: MonkeyPatch) -> None:
    """Test create_dir when an OSError exception is raised"""
    monkeypatch.setattr("fotoobo.helpers.files.os.mkdir", MagicMock(side_effect=OSError()))
    with pytest.raises(GeneralError, match=r"unable to create directory dummy"):
        create_dir("dummy")


# Start testing jinja2 templates


def test_save_with_template(temp_dir: str) -> None:
    """Test save_with_template"""
    output_file = os.path.join(temp_dir, "output.txt")
    save_with_template({"fotoobo": {"dummy_var": 42}}, "tests/data/dummy.j2", output_file)
    assert os.path.isfile(output_file)
    with open(output_file, "r", encoding="UTF-8") as file:
        content = file.read()
    assert "dummy" in content
    assert "42" in content
