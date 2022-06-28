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

__all__ = ["PACKAGE_STATUS", "package_status", "handle_message"]


PACKAGE_STATUS = {
    -1: "a553101e-8c51-4ddd-ac2e-b011ed54389b",  # FAILED
    0: "94727878-7a50-41f8-99eb-a80eb82f737a",  # INITIATED
    1: "3914f0bd-2290-42b1-bc24-41479b3a846f",  # SUCCESS
}
"""dict[int, str]: Package status UUIDs for FAILED (0), INITIATED(1), and SUCCESS(-1)"""


def package_status(
    id: str = None,
    status_id: str = None,
    progress: float = 0,
    file: str = None,
):
    """Update packager status to DB

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
    """
    _progress = int(progress * 100)
    try:
        _json = {
            "id": id,
            "status_id": status_id,
            "progress": _progress,
            "file": file,
        }
        logger.debug(f"Payload: {json.dumps(_json, indent=4)}")

        resp = requests.request(
            "PUT",
            url=f"{CUMULUS_API_URL}/downloads/{id}",
            params={"key": APPLICATION_KEY},
            json=_json,
        )

        logger.debug(f"Response: {resp}")

    except Exception as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")


def handle_message(que, payload_resp: namedtuple, dst: str):
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
    result = pkg_writer(
        plugin=payload_resp.format,
        id=payload_resp.download_id,
        src=json.dumps(payload_resp.contents),
        extent=json.dumps(payload_resp.extent),
        dst=dst,
        cellsize=None,
        dst_srs=None,
    )

    que_get = que.get()
    que_get["return"] = result
    que.put(que_get)
