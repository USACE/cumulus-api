"""
Integration test methods to support testing
"""

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import requests

REPO_ROOT = Path(os.getenv("GEOPROC"))
GEOPROC_TEST_DATA = REPO_ROOT / "fixtures"
TEST_PRODUCTS = (
    Path(__file__).parent.joinpath("integration/fixtures/test_products.json").resolve()
)

OUTPUT_PRODUCTS = []


@pytest.fixture(scope="module")
def products() -> list:
    """gen_product_list provides dynamic fixture based on the test products

    Returns
    -------
    list
        json objects defining the test product attributes
    """
    _products = []
    for dirname, _, filenames in os.walk(GEOPROC_TEST_DATA):
        for filename in filenames:
            if filename.endswith(".json"):
                filepath = Path(dirname).joinpath(filename)
                with filepath.open("r", encoding="utf-8") as fptr:
                    objs = json.load(fptr)
                    if isinstance(objs, list):
                        for obj in objs:
                            _products.append(obj)

    return _products


@pytest.fixture(scope="session")
def tiff_files(tmpdir_factory):
    """tiff_files

    Parameters
    ----------
    tmpdir_factory : TempdirFactory
        temp directory factor

    Returns
    -------
    py.path.local
        path object
    """
    return tmpdir_factory.mktemp("tiffs", numbered=True)


def request_product(
    url: str, name_pattern: str, date_time: datetime = datetime.now(timezone.utc)
) -> str:
    """request_product from provided url and save as a temporary file

    Parameters
    ----------
    url : str
        base url
    name_pattern : str
        filename datetime pattern
    date_time : datetime, optional
        datetime dependent part of the filename, by default datetime.now(timezone.utc)

    Returns
    -------
    str
        FQPN to temporary file
    """
    filename = date_time.strftime(name_pattern)

    sep = "/"
    if url.endswith("/"):
        sep = ""
    _url = "".join([url, sep, filename])

    with requests.get(_url, timeout=10, stream=True) as req:
        if req.status_code != 200:
            return "/tmp/file/does/not/exist"
        with NamedTemporaryFile(
            delete=False,
        ) as fpt:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    fpt.write(chunk)

    return fpt.name
