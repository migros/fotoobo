"""
Test the output helper
"""

from pathlib import Path
from typing import Any, List, Union
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralWarning
from fotoobo.helpers import cli_path
from fotoobo.helpers.output import (
    Output,
    print_datatable,
    print_dicttable,
    print_json,
    print_logo,
    write_policy_to_html,
)
from fotoobo.inventory.generic import GenericDevice


@pytest.fixture
def html_test_file(temp_dir: str) -> Path:
    """Returns the filename of a json test file"""
    return Path(temp_dir) / "test_file.html"


class TestOutput:
    """Test Output class"""

    @staticmethod
    def test_init() -> None:
        """Test the output __init__"""
        assert isinstance(Output().messages, list)

    @staticmethod
    @pytest.mark.parametrize(
        "inputs, expect",
        (
            pytest.param("test", 1, id="add a string"),
            pytest.param(["test_1", "test_2"], 2, id="add a list of strings"),
        ),
    )
    def test_add(inputs: Union[str, List[str]], expect: int) -> None:
        """Test the file_to_ftp function"""
        output = Output()
        output.add(inputs)
        assert len(output.messages) == expect

    @staticmethod
    @pytest.mark.parametrize(
        "inputs",
        (
            pytest.param({}, id="test with dict"),
            pytest.param(1, id="test with int"),
            pytest.param(1.5, id="test with float"),
            pytest.param(True, id="test with bool"),
            pytest.param(("1", "2"), id="test with tuple"),
            pytest.param({"1", "2"}, id="test with set"),
        ),
    )
    def test_add_exception(inputs: Any) -> None:
        """Test add with unsupported type"""
        with pytest.raises(GeneralWarning):
            output = Output()
            output.add(inputs)

    @staticmethod
    def test_print_raw(capsys: Any) -> None:
        """Test print_raw"""
        output = Output()
        output.add(["dummy_line_1", "dummy_line_2"])
        output.print_raw()
        out, _ = capsys.readouterr()
        assert "dummy_line_1" in out
        assert "dummy_line_2" in out

    @staticmethod
    def test_send_mail(monkeypatch: MonkeyPatch) -> None:
        """Test send_mail
        Here we do not really test something. We just run through the send_mail method to see if
        it raises any error or exception. In fact no mail is really sent.
        """
        monkeypatch.setattr(
            "fotoobo.helpers.output.smtplib.SMTP.__init__", MagicMock(return_value=None)
        )
        monkeypatch.setattr(
            "fotoobo.helpers.output.smtplib.SMTP.sendmail", MagicMock(return_value={})
        )
        output = Output()
        output.send_mail(
            GenericDevice(
                hostname="dummy.local",
                recipient="fotoobo_test@domain",
                sender="fotoobo_test@domain",
                subject="fotoobo test notification",
            )
        )
        output.add(["dummy_line_1", "dummy_line_2"])
        cli_path.append("dummy_cli_path")
        output.send_mail(
            GenericDevice(
                hostname="dummy.local",
                recipient="fotoobo_test@domain",
                sender="fotoobo_test@domain",
                subject="fotoobo test notification",
            )
        )
        assert True


def test_print_logo(capsys: Any) -> None:
    """Test print_logo"""
    print_logo()
    out, _ = capsys.readouterr()
    assert "f o t o o b o" in out


@pytest.mark.parametrize(
    "input_data",
    (
        pytest.param({"key1": "val1", "key2": "val2"}, id="test with dict"),
        pytest.param([{"key1": "val1", "key2": "val2"}], id="test with list"),
    ),
)
def test_print_datatable(input_data: Any, capsys: Any) -> None:
    """Test print_datatable"""
    print_datatable(input_data)
    out, _ = capsys.readouterr()
    assert "key1" not in out
    assert "val1" in out
    assert "key2" not in out
    assert "val2" in out


def test_print_datatable_with_dict(capsys: Any) -> None:
    """Test print_datatable when a dict is given"""
    print_datatable({"key1": "val1", "key2": "val2"})
    out, _ = capsys.readouterr()
    assert "key1" not in out
    assert "val1" in out
    assert "key2" not in out
    assert "val2" in out


def test_print_datatable_auto_header(capsys: Any) -> None:
    """Test print_datatable with auto_header"""
    print_datatable([{"key1": "val1", "key2": "val2"}], auto_header=True)
    out, _ = capsys.readouterr()
    assert "key1" in out
    assert "val1" in out


def test_print_datatable_with_headers(capsys: Any) -> None:
    """Test print_datatable with headers given"""
    print_datatable([{"key1": "val1", "key2": "val2"}], headers=["keys", "values"])
    out, _ = capsys.readouterr()
    assert "keys" in out
    assert "key1" not in out
    assert "val1" in out


def test_print_datatable_with_title(capsys: Any) -> None:
    """Test print_datatable with title given"""
    print_datatable([{"key1": "val1", "key2": "val2"}], title="title")
    out, _ = capsys.readouterr()
    assert "title" in out


@pytest.mark.parametrize(
    "input_data",
    (
        pytest.param(("1", "2"), id="test with tuple"),
        pytest.param({"1", "2"}, id="test with set"),
        pytest.param("dummy", id="test with str"),
        pytest.param(42, id="test with int"),
        pytest.param(4.2, id="test with float"),
        pytest.param(True, id="test with bool"),
        pytest.param(None, id="test with NoneType"),
    ),
)
def test_print_datatable_unsupported_type(input_data: Any) -> None:
    """Test print_datatable when data given is unsupported"""
    with pytest.raises(GeneralWarning, match=r"data is not a list or dict"):
        print_datatable(input_data)


def test_print_dicttable(capsys: Any) -> None:
    """Test print_dicttable"""
    print_dicttable({"key1": "val1", "key2": "val2"})
    out, _ = capsys.readouterr()
    assert "key1" in out
    assert "val1" in out
    assert "key2" in out
    assert "val2" in out


@pytest.mark.parametrize(
    "input_data",
    (
        pytest.param(["1", "2"], id="test with list"),
        pytest.param(("1", "2"), id="test with tuple"),
        pytest.param({"1", "2"}, id="test with set"),
        pytest.param("dummy", id="test with str"),
        pytest.param(42, id="test with int"),
        pytest.param(4.2, id="test with float"),
        pytest.param(True, id="test with bool"),
        pytest.param(None, id="test with NoneType"),
    ),
)
def test_print_dicttable_unsupported_type(input_data: Any) -> None:
    """Test print_dicttable when data given is unsupported"""
    with pytest.raises(GeneralWarning, match=r"data is not a dict"):
        print_dicttable(input_data)


@pytest.mark.parametrize(
    "input_data, expect",
    (
        pytest.param("dummy", "dummy", id="test with str"),
        pytest.param(["dummy"], "dummy", id="test with list"),
        pytest.param({"dummy": 42}, "dummy", id="test with dict"),
        pytest.param(42, "42", id="test with int"),
        pytest.param(4.2, "4.2", id="test with float"),
    ),
)
def test_print_json(input_data: Any, expect: str, capsys: Any) -> None:
    """Test print_json"""
    print_json(input_data)
    out, _ = capsys.readouterr()
    assert expect in out


def test_write_policy_to_html(html_test_file: Path) -> None:  # pylint: disable=redefined-outer-name
    """Test write_policy_to_html"""
    assert not html_test_file.is_file()
    write_policy_to_html(
        [
            {"h1": "h1", "h2": "h2", "h3": "h3"},
            {"global-label": "dummy", "groups": "dummy"},
            {"_hitcount": 0, "status": 0, "_last_hit": 0, "action": 0, "send-deny-packet": 0},
            {"_hitcount": 1, "status": 1, "_last_hit": 1, "action": 1},
        ],
        html_test_file,
    )
    assert html_test_file.is_file()
