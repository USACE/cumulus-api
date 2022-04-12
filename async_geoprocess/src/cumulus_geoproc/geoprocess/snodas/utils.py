"""Geoprocess SNODAS utils
"""


import datetime


def metadata_date(src: str):
    """Read datetime from SNODAS metadata text file

    Parameters
    ----------
    src : str
        FQPN to metadata text file
    """
    with open(src, "r") as fh:
        content = fh.readlines()
    content_date = content[4:9]
    y, m, d, h, mi = map(lambda x: x.split(":")[-1].strip(), content_date)
    dt = datetime(y, m, d, h, mi)

    return dt


if __name__ == "__main__":
    print(
        metadata_date(
            "/tmp/SNODAS_unmasked_20100419/zz_ssmv11050lL00T0024TTNATS2010041905DP000.txt"
        )
    )
