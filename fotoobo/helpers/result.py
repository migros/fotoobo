"""
The fotoobo Result class
"""
import json
import smtplib
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

import jinja2
from rich.console import Console
from rich.pretty import pprint
from rich.table import Table
from rich.theme import Theme

from fotoobo.exceptions import GeneralWarning
from fotoobo.helpers import cli_path

ftb_theme = Theme({"var": "white", "ftb": "#FF33BB bold", "chk": "green"})

T = TypeVar("T")


class Result(Generic[T]):
    """
    This class represents a Result of an operation in fotoobo.

    This dataset is meant to be the generic result structure for any tool inside fotoobo.
    It can then be rendered to some command line output (CLI) or JSON response (REST API).
    """

    def __init__(self) -> None:
        """
        Create the FotooboResult object
        """
        # The devices where the processing has been successful
        self.successful: List[str] = []

        # The devices where the processing gave an error
        self.failed: List[str] = []

        # The total number of devices processed
        self.total: int = 0

        # Add messages for each device
        self.messages: Dict[str, List[Dict[str, str]]] = {}

        # The results for each device
        self.results: Dict[str, T] = {}

        # Console object for rich output
        self.console = Console(theme=ftb_theme)

    def push_result(self, key: str, data: T, successful: bool = True) -> None:
        """
        Add a result for the given key

        Args:
            key:        The key to push the results for
            data:       The output data for this key
            successful: Whether the call has been successful or not [default: True]
        """

        self.results[key] = data

        if successful:
            self.successful.append(key)

        else:
            self.failed.append(key)

    def push_message(self, host: str, message: str, level: str = "info") -> None:
        """
        Add a message for the host

        Args:
            host:       The host to add the message for
            message:    The message to add
            level:      The level to assign to this message, used for later filtering
                        (use for example "info", "warning", "error")
        """

        if host not in self.messages:
            self.messages[host] = []

        self.messages[host].append({"message": message, "level": level})

    def get_messages(self, host: str) -> List[Dict[str, str]]:
        """
        Return all the messages for the host given

        Args:
            host:   The host to get the messages for

        Returns:
            A list of the messages pushed for this host. If there are no messages for this host, it
            will return an empty list.
        """

        if host not in self.messages:
            return []

        return self.messages[host]

    def print_messages(self, only_host: Union[str, None] = None) -> None:
        """
        Print the messages to the console

        Args:
            only_host:  Only print the messages for host only_host. If None is given, print all
                        messages.
        """

        out_messages = []

        for host, _messages in self.messages.items():
            if only_host and host != only_host:
                continue

            out_messages += [f"[hst]{host}[/]: {message['message']}" for message in _messages]

        for message in out_messages:
            self.console.print(message)

    def get_result(self, host: str) -> T:
        """
        Return the result pushed by this
        Args:
            host:   The name of the host to retrieve the result for

        Returns:
            The results stored before with push_results, or None if the host does not exist

        Raises:
            GeneralWarning: If there is no result for host
        """

        if host not in self.results:
            raise GeneralWarning(f"Host {host} is not in results.")

        return self.results[host]

    def all_results(self) -> Dict[str, T]:
        """
        Return all results

        Returns:
            The results as a dictionary of the following form::

                {
                    '<name of the host>': <data>
                }

            where `<data>` may be of any type
        """
        return self.results

    def print_result_as_table(
        self,
        title: str = "",
        auto_header: bool = False,
        headers: Optional[List[str]] = None,
    ) -> None:
        """
        Print a table from given data as list or dict.

        Args:
            title:          Set the preferred title for the table
            auto_header:    Whether to show the headers (default: off)
            headers:        Set the headers (if needed)

        Raises:
            GeneralWarning: If the data cannot be interpreted as a table
        """
        if not headers:
            headers = []

        data: List[Dict[str, Any]] = []
        for host, result in self.results.items():
            if isinstance(result, dict):
                data.append({"key": host, **result})

            else:
                data.append({"key": host, "value": result})

        self.print_table_raw(data, headers, auto_header, title)

    def print_table_raw(
        self,
        data: List[Dict[str, Any]],
        headers: Optional[List[str]] = None,
        auto_header: bool = False,
        title: str = "",
    ) -> None:
        """
        Print the data given as a rich table to the console

        Args:
            data:           The data to print formatted as rich.table.Table will expect it
            headers:        The headers for the table
            auto_header:    Whether to show the headers or not
            title:          The title for the table
        """
        if not isinstance(data, list):
            raise GeneralWarning("data for print_table_raw must be a list of dicts.")

        table = Table(title=title, show_header=auto_header or bool(headers))
        if auto_header:
            for heading in data[0].keys():
                table.add_column(heading)

        elif headers:
            for heading in headers:
                table.add_column(heading)

        for line in data:
            _values = line.values()

            # If an item in line is a dict or list we should pretty print it
            values: List[str] = []

            for entry in _values:
                if isinstance(entry, (dict, list)):
                    values.append(json.dumps(entry, indent=4))
                else:
                    values.append(str(entry))

            table.add_row(*values)

        self.console.print(table)

    def print_raw(self, key: Union[str, None] = None) -> None:
        """
        Print the raw data from Result() in pretty format.

        Args:
            key:    Print only the result for the host given
                    (default: print all results)
        """
        if key:
            data = {key: self.get_result(key)}

        else:
            data = {}
            for host in self.all_results():
                data[host] = self.results[host]

        pprint(data, expand_all=True)

    def save_with_template(self, host: str, template_file: Path, output_file: Path) -> None:
        """
        Saves a data structure to a file with a given Jinja2 template. The data structure and the
        variables you can use in the template file depend on the utility the data comes from. See
        the docs of the used utility to see what variables you're intended to use.

        Args:
            data: The data used in the template
            template_file: Filename of the Jinja2 template file
            output_file: The file to write the output to
        """
        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_file.parent), trim_blocks=True, autoescape=True
        )
        template = template_env.get_template(template_file.name)
        output = template.render(self.results[host])
        output_file.write_text(output, encoding="UTF-8")

    def send_messages_as_mail(
        self,
        smtp_server: Any,
        levels: Union[List[str], str, None] = None,
        count: bool = False,
        command: bool = False,
    ) -> None:
        """
        Send an e-mail with the messages collected up until the call

        Args:
            command:        Whether to write the issued command into the message (default: false)
            count:          Whether to write the message count into the message (default: false)
            smtp_server:    The smtp server from inventory to use
            levels:         The levels to output:
                            - None means all messages will be output (default)
                            - 'level' means only messages with level='level' will be output
                            - ['level1', 'level2'] like 2nd option, but all levels given will get
                            output
        """
        out_messages: List[str] = []

        for host, messages in self.messages.items():
            for message in messages:
                if not levels or message["level"] in levels:
                    out_messages.append(f"{host}: {message['message']}")

        if out_messages:
            body = "To:" + smtp_server.recipient + "\n"
            body += "From:" + smtp_server.sender + "\n"
            body += "Subject:" + smtp_server.subject + "\n\n"

            for message_line in out_messages:
                body += message_line + "\n"

            if command and cli_path:
                body += "\ncommand: " + " ".join(cli_path) + "\n"

            if count:
                adds = "s" if len(out_messages) > 1 else ""
                body += "\n" + str(len(out_messages)) + " message" + adds + " in list"

            # Prepare server connection and send mail
            smtp_server.port = getattr(smtp_server, "port", 25)
            with smtplib.SMTP(smtp_server.hostname, smtp_server.port) as mail_server:
                # server.set_debuglevel(1)
                mail_server.sendmail(smtp_server.sender, smtp_server.recipient, body)
