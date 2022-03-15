from datetime import datetime
import os
from pytz import utc
import uuid
import importlib

import config as CONFIG

from helpers import (
    get_infile
)

import logging
logger = logging.getLogger(__name__)


def get_infile_processor(name):
    """Import library for processing a given product_name"""
    
    processor = importlib.import_module(name)
    
    return processor


def process(payload, outdir):

    bucket, key = payload['bucket'], payload['key']
    
    # Filename and product_name
    pathparts = key.split('/')
    pathparts[0] = "cumulus"
    pathparts[1] = "processors"
    acquirable_name = ".".join(pathparts[:-1])
    filename = pathparts[-1]

    if _file := get_infile(bucket, key, os.path.join(outdir, filename)):

        processor = get_infile_processor(acquirable_name)

        logger.debug(f'Using processor: {processor}')
        
        # Process the file and return a list of files
        outfiles = processor.process(_file, outdir)
        
        return outfiles

    return []