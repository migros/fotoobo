"""
The fotoobo converter utility
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fotoobo.fortinet.convert import CheckpointConverter
from fotoobo.helpers.files import create_dir
from fotoobo.helpers.result import Result

log = logging.getLogger("fotoobo")


def checkpoint(
    checkpoint_assets: Union[List[Any], Dict[str, Any], None],
    obj_type: str,
    conversion_id: str,
    cache_dir: Optional[Path] = None,
) -> Result[List[Any]]:
    """
    This function lets you convert Checkpoint assets into Fortinet syntax.

    Args:
        checkpoint_assets: The assets to convert
        obj_type (str): the type of asset to convert
        conversion_id: An ID to the conversion. This is needed to cache different conversion tasks
        cache_dir (str, optional): The cache directory to use. Defaults to None.
    """
    log.info("start converting checkpoint assets of type %s", obj_type)

    result = Result[List[Any]]()

    if cache_dir:
        create_dir(cache_dir)
        cache_file = Path(cache_dir, conversion_id)
    else:
        cache_file = None

    converter = CheckpointConverter(checkpoint_assets, cache_file)

    result.push_result("fortinet_assets", converter.convert(obj_type))

    return result
