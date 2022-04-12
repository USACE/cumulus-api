"""Incoming files transformed to COG

    {
        "geoprocess": "incoming-file-to-cogs",
        "geoprocess_config": {
            "acquirablefile_id": "11a69c52-3a59-4c50-81a6-eba26e6573d4",
            "acquirable_id": "2429db9a-9872-488a-b7e3-de37afc52ca4",
            "acquirable_slug": "cbrfc-mpe",
            "bucket": "castle-data-develop",
            "key": "cumulus/acquirables/cbrfc-mpe/xmrg0322202216z.grb"
        }
    }

"""

import os
from typing import List

from cumulus_geoproc.processors import geo_proc
from cumulus_geoproc.processors.ldm import geo_proc as ldm_proc

from cumulus_geoproc import logger


def process(bucket, key, plugin):
    """_summary_

    Parameters
    ----------
    bucket : str
        _description_
    key : str
        _description_
    plugin : str
        _description_

    Returns
    -------
    List[dict]
        _description_
    """
    # Filename and product_name
    key_parts = key.split("/")
    filename = key_parts[-1]

    if "ldm" in key_parts:
        return ldm_proc(plugin=plugin, bucket=bucket, key=key)
    else:
        return geo_proc(plugin=plugin, bucket=bucket, key=key)
