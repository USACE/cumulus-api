"""Cumulus geoprocessor utilities
"""

from collections import namedtuple
from email.mime import base
from urllib.parse import urlencode, urlsplit, urlunsplit

import httpx
from cumulus_geoproc.configurations import APPLICATION_KEY


# Cumulus API calls
class CumulusAPI:
    """Cumulus API class providing functionality to make requests"""

    def __init__(self, url, http2=True):
        # set url to env var if not provided
        self.url = url
        self.http2 = http2
        self.url_split = urlsplit(self.url)._asdict()

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

    async def post(self, url, payload):
        try:
            with httpx.AsyncClient(http2=self.http2) as client:
                headers = [(b"content-type", b"application/json")]
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 201:
                    return resp.json()
        except ConnectionError as ex:
            # logger.warning(ex)
            print(ex)

    async def get(self, url):
        try:
            async with httpx.AsyncClient(http2=self.http2) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp
        except ConnectionError as ex:
            # logger.warning(ex)
            print(ex)


class NotifyCumulus(CumulusAPI):
    def __init__(self, url, http2=True):
        super().__init__(url, http2)
        self.endpoint = "productfiles"
        self.query = {"key": APPLICATION_KEY}

    def run(self, payload):
        self.post(self.url, payload=payload)
