"""NAEFS Mean 6 hour
"""


import os
import re
from datetime import datetime, timedelta, timezone
from tempfile import NamedTemporaryFile, TemporaryDirectory, TemporaryFile

import numpy as np
import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import cgdal
from osgeo import gdal


# @pyplugs.register
def process(src: str, dst: str, acquirable: str = None):
    """Grid processor

    Parameters
    ----------
    src : str
        path to input file for processing
    dst : str
        path to temporary directory created from worker thread
    acquirable: str
        acquirable slug

    Returns
    -------
    List[dict]
        {
            "filetype": str,         Matching database acquirable
            "file": str,             Converted file
            "datetime": str,         Valid Time, ISO format with timezone
            "version": str           Reference Time (forecast), ISO format with timezone
        }
    """
    outfile_list = list()

    try:
        with TemporaryDirectory(dir=dst) as temp_dir:
            bucket, key = src.split("/", maxsplit=1)
            logger.debug(f"s3_download_file({bucket=}, {key=})")

            infile = utils.s3_download_file(bucket=bucket, key=key, dst=temp_dir)
            logger.debug(f"S3 Downloaded File: {infile}")

            #
            # Variables and their product slug
            #
            nc_variables = {"QPF": "naefs-mean-qpf-06h", "QTF": "naefs-mean-qtf-06h"}

            # Each band in 'time' is a band in the variable
            src_time_ds = gdal.Open(f"NETCDF:{infile}:time")
            # Get the since minutes and compute band times
            time_band = src_time_ds.GetRasterBand(1)
            time_meta = time_band.GetMetadata_Dict()
            time_unit = time_meta["units"]
            # re pattern matching to get the start date from the 'time' units
            # yyyy-mm-dd HH:MM:SS
            pattern = re.compile(r"\d+-\d+-\d+ \d+:\d+:\d+")
            since_time_str = re.search(pattern, time_unit).group(0)
            since_time = datetime.fromisoformat(since_time_str)
            time_array = time_band.ReadAsArray().astype(np.dtype("float32"))

            min2date = lambda x: timedelta(minutes=int(x)) + since_time
            for nc_variable, nc_slug in nc_variables.items():
                subdataset = gdal.Open(f"NETCDF:{infile}:{nc_variable}")
                ds_meta = subdataset.GetMetadata_Dict()
                date_created_str = [
                    re.search(pattern, v).group(0)
                    for k, v in ds_meta.items()
                    if "date_created" in k
                ]
                date_created = datetime.fromisoformat(date_created_str[0])

                no_bands = subdataset.RasterCount

                geo_transform = subdataset.GetGeoTransform()
                src_projection = subdataset.GetProjection()

                for b in range(1, no_bands + 1):
                    band_date = min2date(time_array[0][b])
                    band_filename = (
                        "NAEFSmean_"
                        + nc_variable
                        + band_date.strftime("%Y%m%d%H%M")
                        + ".tif"
                    )
                    # Get the band and process to raster
                    band = subdataset.GetRasterBand(b)
                    xsize = band.XSize
                    ysize = band.YSize
                    datatype = band.DataType
                    nodata_value = band.GetNoDataValue()
                    b_array = band.ReadAsArray(0, 0, xsize, ysize).astype(
                        np.dtype("float32")
                    )
                    # Create at temporary raster and then translate it to the temporary directory
                    tif = cgdal.gdal_array_to_raster(
                        b_array,
                        NamedTemporaryFile("w+b", encoding="utf-8", suffix=".tif").name,
                        xsize,
                        ysize,
                        geo_transform,
                        src_projection,
                        datatype,
                        nodata_value,
                    )

                    # COG with name based on time
                    cog = translate(
                        tif_with_overviews, os.path.join(outdir, band_filename)
                    )

                    outfile_list.append(
                        {
                            "filetype": nc_slug,
                            "file": cog,
                            "datetime": band_date.replace(
                                tzinfo=timezone.utc
                            ).isoformat(),
                            "version": date_created.replace(
                                tzinfo=timezone.utc
                            ).isoformat(),
                        }
                    )

    except RuntimeError as ex:
        logger.error(f"RuntimeError: {os.path.basename(__file__)}: {ex}")
    except KeyError as ex:
        logger.error(f"KeyError: {os.path.basename(__file__)}: {ex}")

    return outfile_list
