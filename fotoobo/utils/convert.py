"""
The fotoobo converter utility
"""

import logging
import os
from typing import Optional

from fotoobo.fortinet.convert import CheckpointConverter
from fotoobo.helpers.files import create_dir, load_json_file, save_json_file

log = logging.getLogger("fotoobo")


def convert_checkpoint(
    infile: str, outfile: str, obj_type: str, cache_dir: Optional[str] = None
) -> None:
    """
    This function lets you convert Checkpoint assets into Fortinet syntax.

    Args:
        infile (str): The exported Checkpoint assets file
        outfile (str): The file to write the converted Fortinet assets to
        obj_type (str): the type of asset to convert
        cache_dir (str, optional): The cache directory to use. Defaults to None.
    """
    log.info("start converting checkpoint assets of type %s", obj_type)
    checkpoint_assets = load_json_file(infile)
    if cache_dir:
        create_dir(cache_dir)

    cache_file = os.path.join(cache_dir, os.path.basename(outfile)) if cache_dir else None
    converter = CheckpointConverter(checkpoint_assets, cache_file)
    fortinet_assets = converter.convert(obj_type)
    save_json_file(outfile, fortinet_assets)
