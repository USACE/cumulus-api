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

import geoprocess_worker.helpers as helpers
from geoprocess_worker import logger


def process(bucket, key, plugin, outdir):
    """_summary_

    Parameters
    ----------
    bucket : str
        _description_
    key : str
        _description_
    plugin : str
        _description_
    outdir : str
        _description_

    Returns
    -------
    List[dict]
        _description_
    """
    # Filename and product_name
    key_parts = key.split("/")
    filename = key_parts[-1]

    if infile := helpers.get_infile(bucket, key, os.path.join(outdir, filename)):
        if "ldm" in key_parts:
            return ldm_proc(plugin=plugin, infile=infile, outdir=outdir)
        else:
            return geo_proc(plugin=plugin, infile=infile, outdir=outdir)
