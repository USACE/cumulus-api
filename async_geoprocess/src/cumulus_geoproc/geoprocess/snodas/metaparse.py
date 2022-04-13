"""Metadata parser
"""

from collections import namedtuple
from textwrap import dedent


def to_dictionary(src: str):
    """ASCII input from SNODAS metadata to a dictionary

    all keys are psuedo-slugified

    Parameters
    ----------
    src : str
        SNODAS metadata as .txt

    Returns
    -------
    dict | None
        dictionary of metadata parameters and their values or None
    """
    try:
        with open(src, "r") as fh:
            config_dict = {}
            for line in fh.readlines():
                k, v = line.split(":")[:2]
                k = k.replace(" ", "_").replace("-", "_").lower()
                v = v.strip()
                # try make the string an int or float if a number
                try:
                    v = int(v) if v.isdigit() else float(v)
                except:
                    pass
                config_dict[k] = v
    except FileNotFoundError as ex:
        return

    return config_dict


def to_namedtuple(src: str, name: str = "Metadata"):
    """Use to_dictionary to generate a namedtuple

    Parameters
    ----------
    src : str
        SNODAS metadata as .txt
    name : str, optional
        collections.namedtuple name, by default "Metadata"

    Returns
    -------
    collections.namedtuple
        namedtuple
    """
    mdata = to_dictionary(src)
    if isinstance(mdata, dict):
        return namedtuple(name, mdata.keys())(*mdata.values())


def write_hdr(src: str, /, columns: int, rows: int):
    """Write a header file (hdr)

    Parameters
    ----------
    src : str
        SNODAS metadata as .txt
    columns: int
        number of columns from the metadata text file
    rows: int
        number of rows from the metadata text file

    Returns
    -------
    str
        FQPN to the written hdr file | None
    """
    try:
        if src.endswith(".txt"):
            with open(hdr_file := src.replace(".txt", ".hdr"), "w") as fh:
                # dedent removing common indentation and lstrip to remove first \n
                hdr = dedent(
                    f"""
                    ENVI
                    samples = {columns}
                    lines = {rows}
                    bands = 1
                    header offset = 0
                    file type = ENVI Standard
                    data type = 2
                    interleave = bsq
                    byte order = 1
                    """
                )
                fh.write(hdr.lstrip())
            return hdr_file
    except OSError as ex:
        return
