"""
The beautiful output helper
"""
import json
import os
import smtplib
from datetime import datetime
from typing import Any, Dict, List, Union

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from fotoobo.exceptions import GeneralWarning
from fotoobo.helpers import cli_path

ftb_theme = Theme({"var": "white", "ftb": "#FF33BB bold", "chk": "green"})
console = Console(theme=ftb_theme)


class Output:
    """Control the fotoobo output"""

    def __init__(self) -> None:
        """Initialize the output class"""
        self.messages: List[str] = []
        # self.ftb_theme = Theme({"var": "white", "ftb": "#FF33BB bold", "chk": "green"})
        # self.ftb_theme = ftb_theme
        self.console = console

    def add(self, messages: Union[str, List[str]]) -> None:
        """
        Add one or multiple message(s) to the output

        Args:
            message (str|list): Add a message or a list of messages to the output
        """
        if isinstance(messages, str):
            self.messages.append(messages)
        elif isinstance(messages, list):
            for message in messages:
                self.messages.append(message)
        else:
            raise GeneralWarning(f"cannot add input type '{type(input)}' to output")

    def print_raw(self) -> None:
        """print the output in raw format"""
        for message in self.messages:
            self.console.print(message)

    def send_mail(self, smtp_server: Any) -> None:
        """
        Send an e-mail
        """
        if not self.messages:
            return

        smtp_server.port = getattr(smtp_server, "port", 25)
        adds = "s" if len(self.messages) > 1 else ""
        self.messages.append(str(len(self.messages)) + " message" + adds + " in list")
        body = "To:" + smtp_server.recipient + "\n"
        body += "From:" + smtp_server.sender + "\n"
        body += "Subject:" + smtp_server.subject + "\n\n"

        if cli_path:
            body += "command: " + " ".join(cli_path) + "\n\n"

        for message in self.messages:
            body += message + "\n"

        with smtplib.SMTP(smtp_server.hostname, smtp_server.port) as mail_server:
            # server.set_debuglevel(1)
            mail_server.sendmail(smtp_server.sender, smtp_server.recipient, body)


def print_logo() -> None:
    """
    Print the beautiful fotoobo logo
    """
    logo_console = Console(style="#FF33BB bold")
    logo_console.print("╭───┐┌───┐┌───╮")
    logo_console.print("└───┘└───┘└───┘")
    logo_console.print(" f o t o o b o ")
    logo_console.print(" ━━━━━━━━━━━━━ ")
    logo_console.print(" make IT easy  ")
    logo_console.print("┌───┐┌───┐┌───┐")
    logo_console.print("╰───┘└───┘└───╯")


def print_datatable(
    data: Union[List[Any], Dict[str, Any]],
    title: str = "",
    auto_header: bool = False,
    headers: Union[List[str], None] = None,
) -> None:
    """
    Print a table from given data as list or dict.

    Args:
        data (Union[List[Any], Dict[str, Any]]): data to print as list
    """
    if not headers:
        headers = []

    if isinstance(data, dict):
        lst = []
        lst.append(data)
        data = lst

    if isinstance(data, list):
        table = Table(title=title, show_header=auto_header or bool(headers))
        if auto_header:
            for heading in data[0].keys():
                table.add_column(heading)

        elif headers:
            for heading in headers:
                table.add_column(heading)

        for line in data:
            values = line.values()
            # if an item in line is a dict or list it should pretty print it
            values = [json.dumps(v, indent=4) if isinstance(v, (dict, list)) else v for v in values]
            # if an item in line is a not renderable convert to string
            values = [str(v) if isinstance(v, (bool, int, list)) else v for v in values]
            table.add_row(*values)

        console.print(table)

    else:
        raise GeneralWarning("data is not a list or dict")


def print_dicttable(
    data: Dict[Any, Any],
    title: str = "",
    auto_header: bool = False,
    headers: Union[List[str], None] = None,
) -> None:
    """Print a table from a given dict. Each key will be a new line"""
    if not isinstance(data, dict):
        raise GeneralWarning("data is not a dict")

    data_list = []
    for key, val in data.items():
        data_list.append({"key": key, "value": val})

    print_datatable(data_list, title=title, auto_header=auto_header, headers=headers)


def print_json(data: Any, indent: int = 4) -> None:
    """
    Print a data structure as pretty json

    Args:
        data (Any): Any data structure
        indent (int): indentation spaces
    """
    print(json.dumps(data, indent=indent))


def write_policy_to_html(  # pylint: disable=too-many-locals
    data: List[Dict[str, Any]], filename: str
) -> None:
    """
    Write a

    Args:
        data (List)   : List of Dicts with data
        filename (str): Filename to write the HTML output to
    """
    ignored_rows = ["status", "global-label", "send-deny-packet"]
    table = '<table class="table table-bordered">\n'
    cols = len(data[0]) - len(ignored_rows)

    # Create the table's column headers
    table += "<thead><tr>\n"
    headers = list(data[0])
    for header in headers:
        if header not in ignored_rows:
            table += f"<th>{header}</th>\n"
    table += '</tr><thead><tbody id="myTable">\n'

    # Create the table's row data
    label = ""
    for line in data:
        if "global-label" in line and line["global-label"] and line["global-label"] != label:
            table += f'<tr><th colspan="{cols}" style="text-align: center;">'
            table += line["global-label"]
            table += f'<span style="display: none">{line["groups"]}</span>'
            table += "</th></tr>\n"
            label = line["global-label"]

        style = ""
        if "_hitcount" in line:
            style = ' style="background-color:#EEE"' if int(line["_hitcount"]) == 0 else ""

        if "status" in line:
            style = ' style="background-color:#FCC"' if int(line["status"]) == 0 else style

        table += f"<tr{style}>"
        for key, value in line.items():
            if key not in ignored_rows:
                if key == "_last_hit":
                    value = datetime.fromtimestamp(value).strftime("%d.%m.%Y") if value > 0 else 0

                if key == "action":
                    value = ["deny", "accept", "ipsec", "ssl-vpn", "redirect", "isolate"][value]
                    if value == "deny" and "send-deny-packet" in line:
                        value += f" ({['drop', 'reset'][line['send-deny-packet']]})"

                value = "<br />".join(value) if isinstance(value, list) else str(value)
                table += f"<td>{value}</td>"

        table += "</tr>\n"

    table += "</tbody></table>"

    html_header = """
        <!DOCTYPE html>
        <html lang="de">
        <head>
        <title>Firewall-Policies</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="description" content="script from fotoobo">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <style type="text/css">
            @media print {
                @page { size: A4 landscape; }
                body { zoom: 80%;}
                .noprint { display: none; }
            }
            body { margin-bottom: 10px; }
        </style>
        </head>
        <body>
        <div class="container-fluid mt-3">
        <h2>Firewall-Policies</h2>
        <div class="noprint">Type something in the input field to filter the table</div>
        <div class="noprint">
            <input class="form-control" id="myInput" type="text" placeholder="Search..">
            <br />
        </div>
        <div>
            <!--<span style="color:#EEE">&#9632;</span> : nohits | -->
            <span style="color:#FCC">&#9632;</span> : disabled
        </div>
        """

    html_footer = """
        <script>
        $(document).ready(function(){
            $("#myInput").on("keyup", function() {
                var value = $(this).val().toLowerCase();
                $("#myTable tr").filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
                });
            });
        });
        </script>
        """
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    html_footer += '<div class="container-fluid text-center">'
    html_footer += f"created {now} on {os.uname().nodename} ({os.uname().sysname})"
    html_footer += "</div>"
    html_footer += """
    </body>
    </html>
    """

    with open(filename, "w", encoding="UTF-8") as file:
        file.writelines(html_header)
        file.writelines(table)
        file.writelines(html_footer)
