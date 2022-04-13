"""_summary_
"""

from collections import namedtuple
from textwrap import dedent


def to_dictionary(src: str):
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
    mdata = to_dictionary(src)
    if isinstance(mdata, dict):
        return namedtuple(name, mdata.keys())(*mdata.values())


def write_hdr(src: str, /, columns: int, rows: int):
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


# TODO: return a list of META-TAG=VALUE using dictionary of snodas metadata
def meta_tags():
    pass
