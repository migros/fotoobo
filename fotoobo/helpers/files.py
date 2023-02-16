"""
Some helper functions for file manipulation.
"""

import json
import logging
import os
import re
from ftplib import FTP
from typing import Any, Dict, List, Union
from zipfile import ZIP_DEFLATED, ZipFile

import jinja2
import yaml

from fotoobo.exceptions import GeneralError

log = logging.getLogger("fotoobo")


def create_dir(directory: str) -> None:
    """
    Try to create a given directory if it does not exist.

    Args:
        directory (str): directory to create (in case it not already exists)

    Raises:
        DirectoryError: Error with message
    """
    if not os.path.isdir(directory):
        try:
            os.mkdir(directory)
        except OSError as err:
            raise GeneralError(f"unable to create directory {directory}") from err


def file_to_ftp(file: str, server: Any) -> int:
    """
    Upload a file to an ftp server.

    Args:
        file (str): the source file to upload

        server (dict): the ftp sever definition dict containing the following keys:

            * hostname
            * directory
            * username
            * password

    Returns:
        int: return code
    """
    retcode = 0
    if os.path.isfile(file):
        with FTP(server.hostname, server.username, server.password) as ftp:
            ftp.cwd(server.directory)
            with open(file, "rb") as ftp_file:
                response = ftp.storbinary(f"STOR {os.path.basename(file)}", ftp_file)
                if response != "226 Transfer complete.":
                    if code := re.search(r"^([0-9]{0,3})\s", response):
                        retcode = int(code[1])

    else:
        retcode = 666

    return retcode


def file_to_zip(src: str, dst: str, level: int = 9) -> None:
    """
    Zip (compress) a file.

    Args:
        src (str): the source file

        dst (str): the destination file (zipfile). If the dst file ends with extension '.zip'
        the inner file will omit the '.zip' extension.

        level (int): compresslevel

    Returns:
        int: return code
    """
    if level < 0 or level > 9:
        raise GeneralError("zip level must between 0 and 9")

    inner_file = dst if not dst.endswith(".zip") else dst[0:-4]
    if os.path.isfile(src):
        with ZipFile(dst, "w", ZIP_DEFLATED, compresslevel=level) as archive:
            archive.write(src, arcname=os.path.basename(inner_file))


def load_json_file(filename: str) -> Union[List[Any], Dict[str, Any], None]:
    """
    Loads the content of a json file into a list or dict.

    Args:
        filename (str): filename of the json file to load

    Returns:
        list|dict|None: list or dict with json data from filename or None if file is not found
    """
    content = None
    if os.path.isfile(filename):
        with open(filename, "r", encoding="UTF-8") as json_file:
            content = json.load(json_file)

    return content


def load_yaml_file(filename: str) -> Union[List[Any], Dict[str, Any], None]:
    """
    Loads the content of a yaml file into a list or dict.

    Args:
        filename (str): filename of the yaml file to load

    Returns:
        list|dict: yaml data from filename
    """
    content = None
    if os.path.isfile(filename):
        with open(filename, "r", encoding="UTF-8") as yaml_file:
            content = yaml.safe_load(yaml_file)

    return content


def save_json_file(filename: str, data: Union[List[Any], Dict[Any, Any]]) -> bool:
    """
    Saves the content of a list or dict to a json file.

    Args:
        filename (str): the filename to write the json dato into
        data (list|dict): data to save
    """
    status = True
    if isinstance(data, (list, dict)):
        with open(filename, "w", encoding="UTF-8") as json_file:
            json.dump(data, json_file, indent=4)

    else:
        status = False

    return status


def save_with_template(data: Dict[Any, Any], template_file: str, output_file: str) -> None:
    """
    Saves a data structure to a file with a given Jinja2 template. The data structure and the
    variables you can use in the template file depend on the utility the data comes from. See the
    docs of the used utility to see what variables you're intended to use.

    Args:
        data (Dict[Any, Any]): The data used in the template

        template_file (str): Filename of the Jinja2 template file. The path to the template_file
        is always a relative path (at the moment). Absolute paths are not supported.

        output_file (str): The file to write the output to
    """
    log.debug("template_file is: %s", template_file)
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader("./"), trim_blocks=True)
    template = template_env.get_template(template_file)
    output = template.render(data)
    with open(output_file, "w", encoding="UTF-8") as file:
        file.write(output)


def save_yaml_file(filename: str, data: Union[List[Any], Dict[str, Any]]) -> bool:
    """
    Saves the content of a list or dict to a yaml file.

    Args:
        filename (str): the filename to write the yaml data into

        data (list|dict): data to save

    Returns:
        bool: returns true if data was valid
    """
    status = True
    if isinstance(data, (list, dict)):
        with open(filename, "w", encoding="UTF-8") as yaml_file:
            yaml.dump(data, yaml_file)

    else:
        status = False

    return status
