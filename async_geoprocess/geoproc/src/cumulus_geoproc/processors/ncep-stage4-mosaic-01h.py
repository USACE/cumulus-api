"""
# NCEP Stage IV Mosaic
"""


import os
import re
from datetime import datetime, timezone

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import cgdal
from osgeo import gdal

gdal.UseExceptions()


this = os.path.basename(__file__)

def find_band1(data_set: "gdal.Dataset", attr: dict = {}, regex_enabled: bool = False):
    """Return the band number

    Parameters
    ----------
    data_set : gdal.Dataset
        gdal dataset
    attr : dict, optional
        attributes matching those in the metadata, by default {}

    Returns
    -------
    int
        band number
    """
    count = data_set.RasterCount
    for b in range(1, count + 1):
        has_attr = 0
        # try:
        raster = data_set.GetRasterBand(b)
        meta = raster.GetMetadata_Dict()
        print(meta)
        for key, val in attr.items():
            if key in meta:
                print(key)
                # Many grib values include regex special characters. e.g. [C] (degrees celsius)
                # Function escapes special characters by default to avoid breaking changes by introducing re.search().
                # Escaping special characters by default will cause this helper function to behave the same way
                # it did previously when looking for a substring using "in".
                _val = val
                if not regex_enabled:
                    _val = re.escape(_val)
                if re.search(_val, raster.GetMetadataItem(key)) is not None:
                    has_attr += 1
        if has_attr == len(attr):
            logger.debug(f"{has_attr=}")
            return b

        # except RuntimeError as ex:
        #     logger.error(f"{type(ex).__name__}: {this}: {ex}")
        #     continue
        # finally:
            raster = None

    return None
@pyplugs.register
def process(*, src: str, dst: str = None, acquirable: str = None):
    """
    # Grid processor

    __Requires keyword only arguments (*)__

    Parameters
    ----------
    src : str
        path to input file for processing
    dst : str, optional
        path to temporary directory
    acquirable: str, optional
        acquirable slug

    Returns
    -------
    List[dict]
    ```
    {
        "filetype": str,         Matching database acquirable
        "file": str,             Converted file
        "datetime": str,         Valid Time, ISO format with timezone
        "version": str           Reference Time (forecast), ISO format with timezone
    }
    ```
    """
    outfile_list = []

    try:
        attr = {"GRIB_ELEMENT": "APCP01"}

        filename = os.path.basename(src)
        filename_dst = utils.file_extension(filename)

        # Take the source path as the destination unless defined.
        # User defined `dst` not programatically removed unless under
        # source's temporary directory.
        if dst is None:
            dst = os.path.dirname(src)

        ds = gdal.Open(src)
        print(find_band1(ds, attr))
        band_number = find_band1(ds, attr)
        band_number = 1
        print(band_number)

        # if (band_number := find_band1(ds, attr)) is None:
        #     raise Exception("Band number not found for attributes: {attr}")

        logger.debug(f"Band number '{band_number}' found for attributes {attr}")

        raster = ds.GetRasterBand(band_number)

        # Get Datetime from String Like "1599008400 sec UTC"
        time_pattern = re.compile(r"\d+")
        valid_time_match = time_pattern.match(raster.GetMetadataItem("GRIB_VALID_TIME"))
        dt_valid = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)

        cgdal.gdal_translate_w_options(
            tif := os.path.join(dst, filename_dst), ds, bandList=[band_number]
        )

        # validate COG
        if (validate := cgdal.validate_cog("-q", tif)) == 0:
            logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

        outfile_list = [
            {
                "filetype": acquirable,
                "file": tif,
                "datetime": dt_valid.isoformat(),
                "version": None,
            },
        ]

    except (RuntimeError, KeyError) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        # closing the data source
        ds = None
        raster = None

    return outfile_list
