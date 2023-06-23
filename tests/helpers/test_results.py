"""
Test the results helper class
"""


from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from fotoobo.exceptions import GeneralWarning
from fotoobo.helpers import cli_path
from fotoobo.helpers.result import Result
from fotoobo.inventory import GenericDevice


class TestResults:
    """Test the results class"""

    @staticmethod
    def test_init() -> None:
        """Test the result __init__"""
        result = Result[str]()
        assert isinstance(result.messages, dict)
        assert isinstance(result.results, dict)

    @staticmethod
    @pytest.mark.parametrize(
        "inputs,successful,expected_result",
        (
            pytest.param("test", None, {"test_host": "test"}, id="add a string"),
            pytest.param(
                ["test_1", "test_2"],
                True,
                {"test_host": ["test_1", "test_2"]},
                id="add a list of strings",
            ),
            pytest.param("test", False, {"test_host": "test"}, id="unsuccessful"),
        ),
    )
    def test_push_result(
        inputs: Union[str, List[str]],
        successful: Union[bool, None],
        expected_result: Dict[str, Any],
    ) -> None:
        """Test the push_result() method"""
        result = Result[Any]()
        if successful is None:
            result.push_result("test_host", inputs)
        else:
            result.push_result("test_host", inputs, successful=successful)

        assert result.results == expected_result

        if successful in [None, True]:
            assert "test_host" in result.successful
            assert len(result.successful) == 1
            assert len(result.failed) == 0

        else:
            assert "test_host" in result.failed
            assert len(result.successful) == 0
            assert len(result.failed) == 1

    @staticmethod
    @pytest.mark.parametrize(
        "message,level",
        (
            pytest.param("test message", None, id="default level"),
            pytest.param("test message", "blabla", id="some custom level"),
        ),
    )
    def test_push_message(message: str, level: Union[None, str]) -> None:
        """Test the push_message() method"""

        result = Result[Any]()
        if level is None:
            result.push_message("test_host", message)
        else:
            result.push_message("test_host", message, level)

        assert "test_host" in result.messages
        assert isinstance(result.messages["test_host"], list)
        assert result.messages["test_host"][0] == {"message": message, "level": level or "info"}

    @staticmethod
    def test_get_messages() -> None:
        """Test the get_messages()  method"""

        result = Result[Any]()
        result.push_message("test_host", "test message 1")
        result.push_message("test_host", "test message 2", level="warning")

        # Check the messages got from get_messages()
        messages = result.get_messages("test_host")

        assert len(messages) == 2
        assert {"message": "test message 1", "level": "info"} in messages
        assert {"message": "test message 2", "level": "warning"} in messages

        # Non-existing host should return empty list
        assert len(result.get_messages("nonexisting_host")) == 0

    @staticmethod
    @pytest.mark.parametrize(
        "messages,only_host,expected_outputs",
        (
            pytest.param(
                [("test_host", "dummy_line_1"), ("test_host", "dummy_line_2")],
                None,
                ["dummy_line_1", "dummy_line_2"],
                id="default messages",
            ),
            pytest.param(
                [("test_host", "dummy_line_1"), ("test_host", "dummy_line_2", "warning")],
                None,
                ["dummy_line_1", "dummy_line_2"],
                id="message with level 'warning",
            ),
            pytest.param(
                [("test_host", "dummy_line_1"), ("test_host1", "dummy_line_2", "warning")],
                "test_host",
                ["dummy_line_1"],
                id="print only messages for one host",
            ),
        ),
    )
    def test_print_messages(
        messages: List[Tuple[str]],
        only_host: Union[str, None],
        expected_outputs: List[str],
        capsys: Any,
    ) -> None:
        """Test print_messages() method"""
        result = Result[Any]()
        for message in messages:
            result.push_message(*message)  # type: ignore

        result.print_messages(only_host)
        out, _ = capsys.readouterr()

        for out_message in expected_outputs:
            assert out_message in out

    @staticmethod
    def test_get_result() -> None:
        """Test the get_result() method"""
        result = Result[str]()
        result.push_result("test_host", "test_result")

        assert result.get_result("test_host") == "test_result"
        with pytest.raises(GeneralWarning, match=r"Host nonexisting_host is not in results."):
            result.get_result("nonexisting_host")

    @staticmethod
    def test_all_results() -> None:
        """Test the all_result() method"""
        result = Result[str]()
        result.push_result("test_host", "test_result")

        assert result.all_results() == {"test_host": "test_result"}

    @staticmethod
    @pytest.mark.parametrize(
        "input_data",
        (
            pytest.param({"key1": "val1", "key2": "val2"}, id="test with dict"),
            pytest.param([{"key1": "val1", "key2": "val2"}], id="test with list"),
        ),
    )
    def test_print_result_as_table(input_data: Any, capsys: Any) -> None:
        """Test print_result_as_table() with default values for one host"""
        result = Result[Any]()
        result.push_result("test_host", input_data)

        result.print_result_as_table("test_host")

        out, _ = capsys.readouterr()
        assert "key1" not in out
        assert "val1" in out
        assert "key2" not in out
        assert "val2" in out

    @staticmethod
    def test_print_result_as_table_auto_header(capsys: Any) -> None:
        """Test print_result_as_table() method with auto_header=True"""
        result = Result[Dict[str, str]]()
        result.push_result("test_host", {"key1": "val1", "key2": "val2"})

        result.print_result_as_table("test_host", auto_header=True)

        out, _ = capsys.readouterr()
        assert "key1" in out
        assert "val1" in out

    @staticmethod
    def test_print_result_as_table_with_headers(capsys: Any) -> None:
        """Test print_result_as_table() method with headers given"""
        result = Result[Dict[str, str]]()
        result.push_result("test_host", {"key1": "val1", "key2": "val2"})

        result.print_result_as_table("test_host", headers=["keys", "values"])

        out, _ = capsys.readouterr()
        assert "keys" in out
        assert "key1" not in out
        assert "val1" in out

    @staticmethod
    def test_print_result_as_table_with_title(capsys: Any) -> None:
        """Test print_result_as_table() method with title given"""
        result = Result[Dict[str, str]]()
        result.push_result("test_host", {"key1": "val1", "key2": "val2"})

        result.print_result_as_table("test_host", title="title")

        out, _ = capsys.readouterr()
        assert "title" in out

    @staticmethod
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
    def test_print_table_raw_with_unsupported_data(input_data: Any) -> None:
        """Test print_table_raw() when data given is unsupported"""
        result = Result[Any]()

        with pytest.raises(GeneralWarning, match=r"must be a list of dicts"):
            result.print_table_raw(input_data, [])

    @staticmethod
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
    def test_print_raw(input_data: Any, expect: str, capsys: Any) -> None:
        """Test print_raw() method"""
        result = Result[Any]()
        result.push_result("test_host", input_data)

        result.print_raw("test_host")

        out, _ = capsys.readouterr()
        assert expect in out

    @staticmethod
    def test_save_with_template(temp_dir: Path) -> None:
        """Test save_with_template"""
        result = Result[Dict[str, Dict[str, int]]]()
        result.push_result("dummy_ems", {"fotoobo": {"dummy_var": 42}})
        output_file = temp_dir / "output.txt"
        result.save_with_template("dummy_ems", Path("tests/data/dummy.j2"), output_file)
        assert output_file.is_file()
        content = output_file.read_text(encoding="UTF-8")
        assert "dummy" in content
        assert "42" in content

    @staticmethod
    def test_send_messages_as_mail(monkeypatch: MonkeyPatch) -> None:
        """Test send_messages_as_mail
        Here we do not really test something. We just run through the send_mail method to see if
        it raises any error or exception. In fact no mail is really sent.
        """
        sendmail_mock = MagicMock()

        monkeypatch.setattr(
            "fotoobo.helpers.result.smtplib.SMTP.__init__", MagicMock(return_value=None)
        )
        monkeypatch.setattr(
            "fotoobo.helpers.result.smtplib.SMTP.__enter__", MagicMock(return_value=sendmail_mock)
        )
        cli_path.append("dummy_cli_path")

        # Prepare result
        result = Result[Any]()
        result.push_message("test_host", "dummy line 1")
        result.push_message("test_host", "dummy line 2")

        result.send_messages_as_mail(
            GenericDevice(
                hostname="dummy.local",
                recipient="fotoobo_recipient@domain",
                sender="fotoobo_sender@domain",
                subject="fotoobo test notification",
            )
        )

        mail = (
            "To:fotoobo_recipient@domain\n"
            "From:fotoobo_sender@domain\n"
            "Subject:fotoobo test notification\n"
            "\n"
            "test_host: dummy line 1\n"
            "test_host: dummy line 2\n"
        )

        sendmail_mock.sendmail.assert_called_with(
            "fotoobo_sender@domain", "fotoobo_recipient@domain", mail
        )
