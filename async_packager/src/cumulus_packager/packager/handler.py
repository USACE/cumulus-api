"""packager module init
    
"""

import json
import os
from collections import namedtuple

import requests

from cumulus_packager import logger
from cumulus_packager.configurations import APPLICATION_KEY, CUMULUS_API_URL, HTTP2
from cumulus_packager.utils import capi
from cumulus_packager.writers import pkg_writer

this = os.path.basename(__file__)
"""str: Path to the module"""

__all__ = [
    "PACKAGE_STATUS",
    "update_status",
    "handle_message",
]

"""dict[str, str]: Package status UUIDs for FAILED, INITIATED, and SUCCESS"""
PACKAGE_STATUS = {
    "FAILED": "a553101e-8c51-4ddd-ac2e-b011ed54389b",
    "INITIATED": "94727878-7a50-41f8-99eb-a80eb82f737a",
    "SUCCESS": "3914f0bd-2290-42b1-bc24-41479b3a846f",
}


def update_status(
    id: str, status_id: str, progress: int, file: str = None, manifest: dict = None
):
    """Update packager status to Cumulus API

    TODO: Check Documentation for accuracy

    Parameters
    ----------
    id : str, optional
        Download ID, by default None
    status_id : str, optional
        Package Status ID, by default None
    progress : float, optional
        progress percentage as a decimal, by default 0
    file : str, optional
        S3 key to dss file, by default None
    manifest : dict, optional
        Dictionary with any information about the download
    """
    try:
        _json_payload = {
            "id": id,
            "status_id": status_id,
            "progress": int(progress),
            "file": file,
            "manifest": manifest,
        }
        r = requests.put(
            f"{CUMULUS_API_URL}/downloads/{id}",
            params={"key": APPLICATION_KEY},
            json=_json_payload,
        )

    except Exception as e:
        logger.error(e)

    return


# def handle_message(que, payload_resp: namedtuple, dst: str):
def handle_message(payload_resp: namedtuple, dst: str):
    """Converts JSON-Formatted message string to dictionary and calls package()

    Parameters
    ----------
    que : multiprocessing.Queue
        queue used to return pkg_writer result to the handler
    payload_resp : namedtuple
        Packager request payload as namedtuple
    dst : str
        Temporary directory name

    """
    logger.info(f"Handle message with plugin '{payload_resp.format}'")
    result = pkg_writer(
        plugin=payload_resp.format,
        id=payload_resp.download_id,
        src=json.dumps(payload_resp.contents),
        extent=json.dumps(payload_resp.extent),
        dst=dst,
        cellsize=2000,
        dst_srs="EPSG:5070",
    )

    return result
