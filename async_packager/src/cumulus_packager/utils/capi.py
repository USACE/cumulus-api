"""Cumulus geoprocessor utilities
"""

from collections import namedtuple
from urllib.parse import urlencode, urlsplit, urlunsplit

import httpx
from cumulus_packager.configurations import APPLICATION_KEY
from cumulus_packager import logger


# Cumulus API calls
class CumulusAPI:
    """Cumulus API class providing functionality to make requests

    asyncio implemented with httpx for HTTP/2 protocol

    """

    def __init__(self, url: str, http2: bool = False):
        # set url to env var if not provided
        self.url = url
        self.http2 = http2
        self.url_split = urlsplit(self.url)._asdict()

    def __repr__(self) -> str:
        return f"{__class__.__name__}({self.url}, {self.http2}, {self.url_split})"

    @property
    def parameters(self):
        return self.url_split

    @parameters.setter
    def parameters(self, key_val):
        self.url_split[key_val[0]] = key_val[1]
        self.build_url(self.url_split)

    def build_url(self, url_params):
        self.url = urlunsplit(namedtuple("UrlUnsplit", url_params.keys())(**url_params))

    @property
    def endpoint(self):
        return self.url_split["path"]

    @endpoint.setter
    def endpoint(self, endpoint):
        self.url_split["path"] = endpoint
        self.build_url(self.url_split)

    @property
    def query(self):
        return self.url_split["query"]

    @query.setter
    def query(self, query: dict):
        self.url_split["query"] = urlencode(query)
        self.build_url(self.url_split)

    async def post_(self, url, payload):
        try:
            client = httpx.AsyncClient(http2=self.http2)
            headers = [(b"content-type", b"application/json")]
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                return resp.json()
        except ConnectionError as ex:
            logger.warning(ex)

    async def put_(self, url, payload):
        try:
            client = httpx.AsyncClient(http2=self.http2)
            headers = [(b"content-type", b"application/json")]
            resp = await client.put(url, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                return resp.json()
        except ConnectionError as ex:
            logger.warning(ex)

    async def get_(self, url):
        try:
            async with httpx.AsyncClient(http2=self.http2) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp
        except ConnectionError as ex:
            logger.warning(ex)


class NotifyCumulus(CumulusAPI):
    """Cumulus notification class extending CumulusAPI

    Parameters
    ----------
    CumulusAPI : class
        base class
    """

    def __init__(self, url, http2=True):
        super().__init__(url, http2)
        self.endpoint = "productfiles"
        self.query = {"key": APPLICATION_KEY}

    def run(self, payload):
        self.post(self.url, payload=payload)
