"""
The FotooboResult class
"""
import json
from typing import Any, Dict, List, Union

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from fotoobo.exceptions import GeneralWarning

ftb_theme = Theme({"var": "white", "ftb": "#FF33BB bold", "chk": "green"})


class Result:
    """
    This class represents a Result of an operation in fotoobo.

    This dataset is meant to be the generic result structure for any tool inside fotoobo.
    It can then be rendered to some commandline output (CLI) or JSON response (REST API).
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
        self.messages: Dict[str, List[str]] = {}

        # The results for each device
        self.results: Dict[str, Any] = {}

        # Console object for rich output
        self.console = Console(theme=ftb_theme)

    def push_result(self, host: str, data: Any, successful: bool = True) -> None:
        """
        Add a result for the host

        Args:
            host:       The host to push the results for
            data:       The output data for this host
            successful: Whether the call has been successful or not [default: True]

        Returns:

        """

        self.results[host] = data

        if successful:
            self.successful.append(host)

        else:
            self.failed.append(host)

    def push_message(self, host: str, message: str) -> None:
        """
        Add a message for the host

        Args:
            host:       The host to add the message for
            message:    The message to add

        Returns:

        """

        if host not in self.messages:
            self.messages[host] = []

        self.messages[host].append(message)

    def get_result(self, host: str) -> Any:
        """
        Return the result pushed by this
        Args:
            host:

        Returns:
            The results stored before with push_results

        """

        return self.results[host]

    def print_result_as_table(
        self,
        only_host: Union[str, None] = None,
        title: str = "",
        auto_header: bool = False,
        headers: Union[List[str], None] = None,
    ) -> None:
        """
        Print a table from given data as list or dict.

        Args:
            only_host (Union[str, None]): Print only the result for the host given
                                          (default: print all results)
            title (str): set the preferred title for the table
            auto_header (bool): whether to show the headers (default: off)
            headers (List[str]): Set the headers (if needed)

        Raises:
            GeneralWarning: If the data cannot be interpreted as a table
        """
        if not headers:
            headers = []

        if only_host:
            data = self.results[only_host]
        else:
            data = self.results

        if isinstance(data, dict):
            data = [data]

        if isinstance(data, list):
            self.print_table_raw(data, headers, auto_header, title)

        else:
            raise GeneralWarning("data is not a list or dict")

    def print_table_raw(
        self, data: List[Dict[str, Any]], headers: List[str], auto_header: bool, title: str
    ) -> None:
        """
        Print the data given as a rich table to the console

        Args:
            data:       The data to print formatted as rich.table.Table will expect it
            headers:    The headers for the table
            auto_header: Whether to show the headers or not
            title:      The title for the table

        Returns:
            Nothing
        """
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
            values = [
                json.dumps(v, indent=4) if isinstance(v, (dict, list)) else v for v in _values
            ]
            # If an item in line is a not render-able convert to string
            values += [str(v) if isinstance(v, (bool, int, list)) else v for v in _values]

            table.add_row(*values)

        self.console.print(table)
