"""NAEFS Mean 6 hour
"""


import os
import re
from datetime import datetime, timedelta, timezone

import numpy as np
import pyplugs
from cumulus_geoproc import logger
from cumulus_geoproc import utils
from cumulus_geoproc.utils import cgdal
from osgeo import gdal


this = os.path.basename(__file__)


@pyplugs.register
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
    outfile_list = []

    try:
        filename = os.path.basename(src)
        #
        # Variables and their product slug
        #
        nc_variables = {"QPF": "naefs-mean-qpf-06h", "QTF": "naefs-mean-qtf-06h"}

        # bucket, key = src.split("/", maxsplit=1)
        # logger.debug(f"s3_download_file({bucket=}, {key=})")

        # src_ = boto.s3_download_file(bucket=bucket, key=key, dst=dst)
        # logger.debug(f"S3 Downloaded File: {src_}")

        src_ = src

        since_pattern = re.compile(r"\w+ \w+ (?P<since>\d{4}-\d{2}-\d{2})")
        create_pattern = re.compile(r"\d+-\d+-\d+ \d+:\d+:\d+")

        ds = gdal.Open(src_)

        create_str = ds.GetMetadataItem("NC_GLOBAL#date_created")
        m = create_pattern.match(create_str)
        create_date = datetime.fromisoformat(m.group(0)).replace(tzinfo=timezone.utc)

        for subset in ds.GetSubDatasets():
            subset_name, _ = subset
            if (parameter_name := subset_name.split(":")[-1]) in nc_variables:
                # dataset in the nc file
                subdataset = gdal.Open(subset_name)

                # get the since time each band will reference
                # "time#units": "minutes since 1970-01-01 00:00:00.0 +0000",
                # yyyy-mm-dd HH:MM:SS
                since_time_str = subdataset.GetMetadataItem("analysis_time#units")

                m = since_pattern.match(since_time_str)
                since_time = datetime.fromisoformat(m.group("since")).replace(
                    tzinfo=timezone.utc
                )

                product_name = nc_variables[parameter_name]

                # loop through each band
                for b in range(1, subdataset.RasterCount + 1):
                    raster = subdataset.GetRasterBand(b)
                    nodata = raster.GetNoDataValue()
                    dim_time = raster.GetMetadataItem("NETCDF_DIM_time")
                    ref_time = since_time + timedelta(minutes=int(dim_time))

                    filename_ = utils.file_extension(
                        filename,
                        suffix=f"_{product_name}_{ref_time.strftime('%Y%m%d%H%M')}.tif",
                    )

                    # Extract Band; Convert to COG
                    translate_options = cgdal.gdal_translate_options(noData=nodata)
                    gdal.Translate(
                        tif := os.path.join(dst, filename_),
                        raster.GetDataset(),
                        **translate_options,
                    )

                    outfile_list.append(
                        {
                            "filetype": product_name,
                            "file": tif,
                            "datetime": ref_time.isoformat(),
                            "version": create_date.isoformat(),
                        }
                    )

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None
        subdataset = None
        raster = None

    return outfile_list


if __name__ == "__main__":
    srcfile = "/Users/rdcrljsg/projects/cumulus-products/data/cumulus/acquirables/naefs-mean-06h/NAEFSmean_netcdf2021111112.nc"
    dstdir = "/Users/rdcrljsg/Desktop/products"
    results = process(srcfile, dstdir)
    for result in results:
        print(result)
