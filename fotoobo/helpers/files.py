"""
Some helper functions for file manipulation.
"""
import json
import logging
import re
from ftplib import FTP, FTP_TLS
from pathlib import Path
from typing import Any, Dict, List, Union
from zipfile import ZIP_DEFLATED, ZipFile

import yaml


from fotoobo.exceptions import GeneralError

log = logging.getLogger("fotoobo")


def create_dir(directory: Path) -> None:
    """
    Try to create a given directory if it does not exist.

    Args:
        directory: The directory to create (in case it not already exists)

    Raises:
        OSError: Error with message
    """
    if not directory.is_dir():
        try:
            directory.mkdir(parents=True)
        except OSError as err:
            raise GeneralError(f"Unable to create directory {directory}") from err


def file_to_ftp(file: Path, server: Any) -> int:
    """
    Upload a file to a ftp server.

    Args:
        file (Path): The source file to upload

        server (dict): the ftp sever definition dict containing the following keys:

            * hostname
            * directory
            * username
            * password
            * protocol (default="sftp")

    Returns:
        int: return code
    """
    return_code = 0
    if file.is_file():
        if hasattr(server, "protocol"):
            protocol = server.protocol
        else:
            protocol = "sftp"

        if protocol == "sftp":
            with FTP_TLS(server.hostname) as ftp:
                log.debug("SFTP transfer for '%s'", server.hostname)
                ftp.sendcmd(f"USER {server.username}")
                ftp.sendcmd(f"PASS {server.password}")
                ftp.cwd(server.directory)
                with file.open("rb") as ftp_file:
                    response = ftp.storbinary(f"STOR {file.name}", ftp_file)
                    if response != "226 Transfer complete.":
                        if code := re.search(r"^([0-9]{0,3})\s", response):
                            return_code = int(code[1])

        elif protocol == "ftp":
            with FTP(server.hostname, server.username, server.password) as ftp:
                log.debug("FTP transfer for '%s'", server.hostname)
                ftp.cwd(server.directory)
                with file.open("rb") as ftp_file:
                    response = ftp.storbinary(f"STOR {file.name}", ftp_file)
                    if response != "226 Transfer complete.":
                        if code := re.search(r"^([0-9]{0,3})\s", response):
                            return_code = int(code[1])

        else:
            raise GeneralError(f'Unknown FTP protocol "{protocol}" for server "{server.hostname}"')

    else:
        return_code = 666

    return return_code


def file_to_zip(src: Path, dst: Path, level: int = 9) -> None:
    """
    Zip (compress) a file.

    Args:
        src (Path): the source file

        dst (Path): the destination file (zipfile). If the dst file ends with extension '.zip'
        the inner file will omit the '.zip' extension.

        level (int): compression level, as accepted by `zipfile.ZipFile`

    Returns:
        int: return code
    """
    if level < 0 or level > 9:
        raise GeneralError("zip level must between 0 and 9")

    inner_file = dst if not dst.suffix == ".zip" else Path(dst.name[0:-4])
    if src.is_file():
        with ZipFile(dst, "w", ZIP_DEFLATED, compresslevel=level) as archive:
            archive.write(src, arcname=inner_file.name)


def load_json_file(json_file: Path) -> Union[List[Any], Dict[str, Any], None]:
    """
    Loads the content of a json file into a list or dict.

    Args:
        json_file (Path): The path to the json file to load

    Returns:
        list|dict|None: list or dict with json data from filename or None if file is not found
    """
    content = None
    if json_file.is_file():
        with json_file.open(encoding="UTF-8") as in_file:
            content = json.load(in_file)

    return content


def load_yaml_file(yaml_file: Path) -> Union[List[Any], Dict[str, Any], None]:
    """
    Loads the content of a yaml file into a list or dict.

    Args:
        yaml_file (Path): The file of the yaml file to load

    Returns:
        list|dict: yaml data from filename
    """
    content = None
    if yaml_file.is_file():
        content = yaml.safe_load(yaml_file.read_text(encoding="UTF-8"))

    return content


def save_json_file(json_file: Path, data: Union[List[Any], Dict[Any, Any]]) -> bool:
    """
    Saves the content of a list or dict to a json file.

    Args:
        json_file (Path): The file to write the json dato into
        data (list|dict): data to save
    """
    status = True
    if isinstance(data, (list, dict)):
        with json_file.open("w", encoding="UTF-8") as out_file:
            json.dump(data, out_file, indent=4)

    else:
        status = False

    return status


def save_yaml_file(yaml_file: Path, data: Union[List[Any], Dict[str, Any]]) -> bool:
    """
    Saves the content of a list or dict to a yaml file.

    Args:
        yaml_file (Path): the file to write the yaml data into

        data (list|dict): data to save

    Returns:
        bool: returns true if data was valid
    """
    status = True
    if isinstance(data, (list, dict)):
        with open(yaml_file, "w", encoding="UTF-8") as out_file:
            yaml.dump(data, out_file)

    else:
        status = False

    return status
