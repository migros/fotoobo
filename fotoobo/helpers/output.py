"""
The beautiful output helper
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from rich.console import Console


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


def write_policy_to_html(data: List[Dict[str, Any]], out_file: Path) -> None:
    """
    Write a

    Args:
        data (List)   : List of Dicts with data
        out_file (Path): Filename to write the HTML output to
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

    out_file.write_text(html_header + table + html_footer, encoding="UTF-8")
