"""packager module init
    
"""

import asyncio
import json
import os
from collections import namedtuple

from cumulus_packager import logger
from cumulus_packager.configurations import APPLICATION_KEY, CUMULUS_API_URL, HTTP2
from cumulus_packager.utils import capi
from cumulus_packager.writers import pkg_writer

this = os.path.basename(__file__)

__all__ = ["PACKAGE_STATUS", "package_status", "handle_message"]


PACKAGE_STATUS = {
    -1: "a553101e-8c51-4ddd-ac2e-b011ed54389b",  # FAILED
    0: "94727878-7a50-41f8-99eb-a80eb82f737a",  # INITIATED
    1: "3914f0bd-2290-42b1-bc24-41479b3a846f",  # SUCCESS
}


def package_status(
    id: str = None,
    status_id: str = None,
    progress: float = 0,
    file: str = None,
    precision: float = 0.5,
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
    _progress = round(progress * 100, 2)
    if _progress % precision == 0:
        try:
            _json = {
                "id": id,
                "status_id": status_id,
                "progress": _progress,
                "file": file,
            }
            logger.debug(f"Payload: {json.dumps(_json, indent=4)}")

            cumulus_api = capi.CumulusAPI(CUMULUS_API_URL, HTTP2)
            cumulus_api.endpoint = f"downloads/{id}"
            cumulus_api.query = {"key": APPLICATION_KEY}

            logger.debug(f"API endpoint URL: {cumulus_api.url}")

            resp = asyncio.run(cumulus_api.put_(cumulus_api.url, _json))

            logger.debug(f"Response: {resp}")
            logger.debug(f"Response: {resp.http_version}")

        except Exception as ex:
            logger.error(f"{type(ex).__name__}: {this}: {ex}")


def handle_message(payload_resp: namedtuple, dst: str, callback=None):
    """Converts JSON-Formatted message string to dictionary and calls package()

    Parameters
    ----------
    payload_resp : namedtuple
        Packager request payload as namedtuple
    dst : str
        Temporary directory name
    callback : callable, optional
        callback function sending message to the DB, by default None

    Returns
    -------
    str
        FQPN to file
    """
    result = pkg_writer(
        plugin=payload_resp.format,
        id=payload_resp.download_id,
        extent=payload_resp.extent,
        src=payload_resp.contents,
        dst=dst,
        cellsize=None,
        dst_srs="EPSG:5070",
        callback=callback,
    )
    return result
