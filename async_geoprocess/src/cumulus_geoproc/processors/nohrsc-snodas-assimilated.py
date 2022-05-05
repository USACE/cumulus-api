"""NOHRSC SNODAS Assimilated

Inside the original assim_layers_YYYYMMDDHH.tar file:
Inside a folder that looks like: ssm1054_2022012212.20220122134004 (without the word 'east')
There is a file that looks like: ssm1054_2022012212.nc.gz
Need to uncompress that NetCDF file
"""


import os
import re
import tarfile
from datetime import datetime

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import boto, cgdal
from netCDF4 import Dataset
from osgeo import gdal, osr

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
    acquirable = "nohrsc-snodas-swe-corrections"

    try:
        bucket, key = src.split("/", maxsplit=1)
        logger.debug(f"s3_download_file({bucket=}, {key=})")

        src_ = boto.s3_download_file(bucket=bucket, key=key, dst=dst)
        logger.debug(f"S3 Downloaded File: {src_}")

        # extract the member from the tar using this pattern
        member_pattern = re.compile(r"ssm1054_\d+.\d+/ssm1054_\d+.nc.gz")
        with tarfile.open(src_) as tar:
            for member in tar.getmembers():
                if member_pattern.match(member.name):
                    tar.extract(member, path=dst)

                    filename = os.path.join(dst, member.name)

                    # decompress the extracted member
                    snodas_assim = utils.decompress(filename, dst)
                    logger.debug(f"{snodas_assim=}")

                    filename_ = utils.file_extension(snodas_assim)

                    with Dataset(snodas_assim, "r") as ncds:
                        lon = ncds.variables["lon"][:]
                        lat = ncds.variables["lat"][:]
                        data = ncds.variables["Data"]
                        crs = ncds.variables["crs"]
                        data_vals = data[:]

                        valid_time = datetime.fromisoformat(data.stop_date)

                        xmin, ymin, xmax, ymax = (
                            lon.min(),
                            lat.min(),
                            lon.max(),
                            lat.max(),
                        )
                        nrows, ncols = data.shape
                        xres = (xmax - xmin) / float(ncols)
                        yres = (ymax - ymin) / float(nrows)

                        geotransform = (xmin, xres, 0, ymax, 0, -yres)

                        raster = gdal.GetDriverByName("GTiff").Create(
                            tmptif := os.path.join(dst, snodas_assim + ".tmp.tif"),
                            xsize=ncols,
                            ysize=nrows,
                            bands=1,
                            eType=gdal.GDT_Float32,
                        )

                        raster.SetGeoTransform(geotransform)
                        srs = osr.SpatialReference()

                        # srs.ImportFromEPSG(4326)
                        srs.SetWellKnownGeogCS(crs.horizontal_datum)

                        raster.SetProjection(srs.ExportToWkt())
                        band = raster.GetRasterBand(1)
                        band.WriteArray(data_vals)
                        raster.FlushCache()
                        raster = None

                        gdal.Translate(
                            tif := os.path.join(dst, filename_),
                            tmptif,
                            format="COG",
                            bandList=[1],
                            noData=data.no_data_value,
                            creationOptions=[
                                "RESAMPLING=AVERAGE",
                                "OVERVIEWS=IGNORE_EXISTING",
                                "OVERVIEW_RESAMPLING=AVERAGE",
                                "NUM_THREADS=ALL_CPUS",
                            ],
                        )

                        # validate COG
                        if (validate := cgdal.validate_cog("-q", tif)) == 0:
                            logger.info(f"Validate COG = {validate}\t{tif} is a COG")

                        # Append dictionary object to outfile list
                        outfile_list.append(
                            {
                                "filetype": acquirable,
                                "file": tif,
                                "datetime": valid_time.isoformat(),
                                "version": None,
                            }
                        )
                    break

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None

    return outfile_list


if __name__ == "__main__":
    pass
