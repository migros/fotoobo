"""
test_file_helper
"""
# pylint: disable=redefined-outer-name

import os
from pathlib import Path
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
    save_yaml_file,
)
from fotoobo.helpers.result import Result
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
def json_test_file(temp_dir: Path) -> Path:
    """Returns the filename of a json test file"""
    return temp_dir / "test_file.json"


@pytest.fixture
def yaml_test_file(temp_dir: Path) -> Path:
    """Returns the filename of a yaml test file"""
    return temp_dir / "test_file.yaml"


@pytest.mark.parametrize(
    "file, mock, expected",
    (
        pytest.param(
            Path("tests/data/fortigate_config_empty.conf"),
            MagicMock(return_value="226 Transfer complete."),
            0,
            id="file to ftp ok",
        ),
        pytest.param(
            Path("tests/data/dummy"),
            MagicMock(),
            666,
            id="file to ftp with inexistent file",
        ),
        pytest.param(
            Path("tests/data/fortigate_config_empty.conf"),
            MagicMock(return_value="222 Some unknown error"),
            222,
            id="file to ftp with unknown error",
        ),
    ),
)
def test_file_to_ftp(file: Path, mock: MagicMock, expected: int, monkeypatch: MonkeyPatch) -> None:
    """Test the file_to_ftp function"""
    monkeypatch.setattr("fotoobo.helpers.files.FTP.cwd", MagicMock(return_value=""))
    monkeypatch.setattr("fotoobo.helpers.files.FTP.sendcmd", MagicMock(return_value=""))
    monkeypatch.setattr("fotoobo.helpers.files.FTP.storbinary", mock)
    assert file_to_ftp(file, GenericDevice(username="", password="", directory="")) == expected


def test_file_to_zip(json_test_file: Path, temp_dir: Path) -> None:
    """Test the file_to_zip function"""
    assert not json_test_file.is_file()
    json_test_file.write_text("Test", encoding="UTF-8")
    assert json_test_file.is_file()
    dst = temp_dir / "test.zip"
    assert not dst.is_file()
    file_to_zip(json_test_file, dst, 9)
    assert dst.is_file()


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
        file_to_zip(Path(""), Path(""), zip_level)


# Start testing the json file_helper functions


def test_save_json_file_dict(json_test_file: Path, test_data_dict: Dict[str, Any]) -> None:
    """Test the save_json_file function"""
    save_json_file(json_test_file, test_data_dict)
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


def test_load_json_file_dict(json_test_file: Path, test_data_dict: Dict[str, Any]) -> None:
    """Test the load_json_file function"""
    assert json_test_file.is_file()
    content = load_json_file(json_test_file)
    assert content == test_data_dict


def test_save_json_file_list(json_test_file: Path, test_data_list: List[str]) -> None:
    """Test the save_json_file function"""
    save_json_file(json_test_file, test_data_list)
    assert json_test_file.is_file()
    content = json_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    expect = """["value1", "value2", 3, 4]"""
    expect = expect.replace(" ", "").replace("\n", "")
    assert content == expect


def test_load_json_file_list(json_test_file: Path, test_data_list: List[str]) -> None:
    """Test the load_json_file function"""
    assert json_test_file.is_file()
    content = load_json_file(json_test_file)
    assert content == test_data_list


def test_save_json_file_empty_dict(json_test_file: Path) -> None:
    """Test the save_json_file function with an empty dict"""
    os.remove(json_test_file)
    assert not json_test_file.is_file()
    save_json_file(json_test_file, {})
    assert json_test_file.is_file()
    assert json_test_file.stat().st_size == 2
    with open(json_test_file, "r", encoding="UTF-8") as file:
        content = file.read().replace(" ", "").replace("\n", "")
    assert content == "{}"


def test_load_json_file_empty_dict(json_test_file: Path) -> None:
    """Test the load_json_file function with an empty dict"""
    assert json_test_file.is_file()
    content = load_json_file(json_test_file)
    assert content == {}


def test_save_json_file_empty_list(json_test_file: Path) -> None:
    """Test the save_json_file function with an empty list"""
    os.remove(json_test_file)
    assert not json_test_file.is_file()
    save_json_file(json_test_file, [])
    assert json_test_file.is_file()
    assert json_test_file.stat().st_size == 2
    content = json_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    assert content == "[]"


def test_load_json_file_empty_list(json_test_file: Path) -> None:
    """Test the load_json_file function with an empty list"""
    assert json_test_file.is_file()
    content = load_json_file(json_test_file)
    assert content == []


def test_save_json_file_unsupported_type(json_test_file: Path) -> None:
    """Test the save_json_file function with data of unsupported type"""
    os.remove(json_test_file)
    assert not json_test_file.is_file()
    assert not save_json_file(json_test_file, None)  # type: ignore
    assert not save_json_file(json_test_file, 42)  # type: ignore
    assert not save_json_file(json_test_file, "42")  # type: ignore


def test_load_json_file_non_exist(json_test_file: Path) -> None:
    """Test the load_json_file function with not existing file"""
    assert not json_test_file.is_file()
    assert not load_json_file(json_test_file)


# Start testing the yaml file_helper functions


def test_save_yaml_file_dict(yaml_test_file: Path, test_data_dict: Dict[str, Any]) -> None:
    """Test the save_yaml_file function"""
    save_yaml_file(yaml_test_file, test_data_dict)
    assert yaml_test_file.is_file()
    content = yaml_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    expect = "key1:value1key2:-key3:value3key4:value4-key5:value5key6:value6"
    assert content == expect


def test_load_yaml_file_dict(yaml_test_file: Path, test_data_dict: Dict[str, Any]) -> None:
    """Test the load_yaml_file function"""
    assert yaml_test_file.is_file()
    content = load_yaml_file(yaml_test_file)
    assert content == test_data_dict


def test_save_yaml_file_list(yaml_test_file: Path, test_data_list: List[str]) -> None:
    """Test the save_yaml_file function"""
    save_yaml_file(yaml_test_file, test_data_list)
    assert yaml_test_file.is_file()
    content = yaml_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    expect = "-value1-value2-3-4"
    expect = expect.replace(" ", "").replace("\n", "")
    assert content == expect


def test_load_yaml_file_list(yaml_test_file: Path, test_data_list: List[str]) -> None:
    """Test the load_yaml_file function"""
    assert yaml_test_file.is_file()
    content = load_yaml_file(yaml_test_file)
    assert content == test_data_list


def test_save_yaml_file_empty_dict(yaml_test_file: Path) -> None:
    """Test the save_yaml_file function with an empty dict"""
    os.remove(yaml_test_file)
    assert not yaml_test_file.is_file()
    save_yaml_file(yaml_test_file, {})
    assert yaml_test_file.is_file()
    assert yaml_test_file.stat().st_size == 3
    content = yaml_test_file.read_text(encoding="UTF-8").replace("\n", "")
    assert content == "{}"


def test_load_yaml_file_empty_dict(yaml_test_file: Path) -> None:
    """Test the load_yaml_file function with an empty dict"""
    assert yaml_test_file.is_file()
    content = load_yaml_file(yaml_test_file)
    assert content == {}


def test_save_yaml_file_empty_list(yaml_test_file: Path) -> None:
    """Test the save_yaml_file function with an empty list"""
    os.remove(yaml_test_file)
    assert not yaml_test_file.is_file()
    save_yaml_file(yaml_test_file, [])
    assert yaml_test_file.is_file()
    assert yaml_test_file.stat().st_size == 3
    content = yaml_test_file.read_text(encoding="UTF-8").replace(" ", "").replace("\n", "")
    assert content == "[]"


def test_load_yaml_file_empty_list(yaml_test_file: Path) -> None:
    """Test the load_yaml_file function with an empty list"""
    assert yaml_test_file.is_file()
    content = load_yaml_file(yaml_test_file)
    assert content == []


def test_save_yaml_file_unsupported_type(yaml_test_file: Path) -> None:
    """Test the save_yaml_file function with data of unsupported type"""
    os.remove(yaml_test_file)
    assert not yaml_test_file.is_file()
    assert not save_yaml_file(yaml_test_file, None)  # type: ignore
    assert not save_yaml_file(yaml_test_file, 42)  # type: ignore
    assert not save_yaml_file(yaml_test_file, "42")  # type: ignore


def test_load_yaml_file_non_exist(yaml_test_file: Path) -> None:
    """Test the load_yaml_file function with not existing file"""
    assert not yaml_test_file.is_file()
    assert not load_yaml_file(yaml_test_file)


# Start testing the create_dir function


def test_create_dir_for_new_directory(temp_dir: Path) -> None:
    """Test create_dir in an existing directory"""
    directory = temp_dir / "test_dir_1"
    assert not directory.is_dir()
    create_dir(directory)
    assert directory.is_dir()


def test_create_dir_for_existing_directory(temp_dir: Path) -> None:
    """Test create_dir in an existing directory when the directory to create already exists"""
    directory = temp_dir / "test_dir_2"
    assert not directory.is_dir()
    directory.mkdir()
    assert directory.is_dir()
    create_dir(directory)
    assert directory.is_dir()


def test_create_dir_for_sub_sub_directory(temp_dir: Path) -> None:
    """Test create_dir when trying to create a sub, subdirectory"""
    directory = temp_dir / "test_dir_3" / "test_dir_4"
    assert not directory.is_dir()
    with pytest.raises(GeneralError, match=r"Unable to create directory .*/test_dir_3/test_dir_4"):
        create_dir(directory)


def test_create_dir_with_os_error(monkeypatch: MonkeyPatch) -> None:
    """Test create_dir when an OSError exception is raised"""
    monkeypatch.setattr("fotoobo.helpers.files.Path.mkdir", MagicMock(side_effect=OSError()))
    with pytest.raises(GeneralError, match=r"Unable to create directory dummy"):
        create_dir(Path("dummy"))


# Start testing jinja2 templates


def test_save_with_template(temp_dir: Path) -> None:
    """Test save_with_template"""
    result = Result()
    result.push_result("dummy_ems", {"fotoobo": {"dummy_var": 42}})
    output_file = temp_dir / "output.txt"
    result.save_with_template("dummy_ems", Path("tests/data/dummy.j2"), output_file)
    assert output_file.is_file()
    content = output_file.read_text(encoding="UTF-8")
    assert "dummy" in content
    assert "42" in content
