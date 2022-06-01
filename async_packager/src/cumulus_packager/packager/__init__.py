import asyncio
import json
import os

from cumulus_packager import logger
from cumulus_packager.configurations import APPLICATION_KEY, CUMULUS_API_URL, HTTP2
from cumulus_packager.utils import capi
from cumulus_packager.writers import pkg_writer

this = os.path.basename(__file__)

PACKAGE_STATUS = {
    -1: "a553101e-8c51-4ddd-ac2e-b011ed54389b",  # FAILED
    0: "94727878-7a50-41f8-99eb-a80eb82f737a",  # INITIATED
    1: "3914f0bd-2290-42b1-bc24-41479b3a846f",  # SUCCESS
}


def package_status(id=None, status_id=None, progress=0, file=None):
    _progress = int(progress * 100)
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

        resp = asyncio.run(cumulus_api.put_(cumulus_api.url, payload=_json))

        logger.debug(f"Response: {resp}")

    except Exception as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")


def handle_message(payload_resp, dst, callback=None):
    """Converts JSON-Formatted message string to dictionary and calls package()"""
    result = pkg_writer(
        plugin=payload_resp.format,
        id=payload_resp.download_id,
        outkey=payload_resp.output_key,
        extent=payload_resp.extent,
        src=payload_resp.contents,
        dst=dst,
        cellsize=2000,
        dst_srs="EPSG:5070",
        callback=callback,
    )
    return result
