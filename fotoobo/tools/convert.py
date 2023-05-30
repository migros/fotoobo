"""
The fotoobo converter utility
"""

import logging
from pathlib import Path
from typing import Optional

from fotoobo.fortinet.convert import CheckpointConverter
from fotoobo.helpers.files import create_dir, load_json_file, save_json_file

log = logging.getLogger("fotoobo")


def checkpoint(
    infile: Path, outfile: Path, obj_type: str, cache_dir: Optional[Path] = None
) -> None:
    """
    This function lets you convert Checkpoint assets into Fortinet syntax.

    Args:
        infile (Path): The exported Checkpoint assets file
        outfile (Path): The file to write the converted Fortinet assets to
        obj_type (str): the type of asset to convert
        cache_dir (str, optional): The cache directory to use. Defaults to None.
    """
    log.info("start converting checkpoint assets of type %s", obj_type)
    checkpoint_assets = load_json_file(infile)
    if cache_dir:
        create_dir(cache_dir)

    cache_file = Path(cache_dir, Path(outfile).name) if cache_dir else None
    converter = CheckpointConverter(checkpoint_assets, cache_file)
    fortinet_assets = converter.convert(obj_type)
    save_json_file(outfile, fortinet_assets)
