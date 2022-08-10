"""
# NOHRSC SNODAS Assimilated

Inside the original assim_layers_YYYYMMDDHH.tar file:
Inside a folder that looks like: ssm1054_2022012212.20220122134004 (without the word 'east')
There is a file that looks like: ssm1054_2022012212.nc.gz
Need to uncompress that NetCDF file
"""


import os
import re
import tarfile
from datetime import datetime, timezone
import numpy

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import cgdal
from netCDF4 import Dataset
from osgeo import gdal, osr

this = os.path.basename(__file__)


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
    acquirable = "nohrsc-snodas-swe-corrections"

    try:
        filename = os.path.basename(src)
        filename_dst = utils.file_extension(filename)

        # Take the source path as the destination unless defined.
        # User defined `dst` not programatically removed unless under
        # source's temporary directory.
        if dst is None:
            dst = os.path.dirname(src)

        # extract the member from the tar using this pattern
        member_pattern = re.compile(r"ssm1054_\d+.\d+/ssm1054_\d+.nc.gz")
        with tarfile.open(src) as tar:
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

                        valid_time = datetime.fromisoformat(data.stop_date).replace(
                            tzinfo=timezone.utc
                        )

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

                        # Reference the following for reason to flip
                        # https://www.unidata.ucar.edu/support/help/MailArchives/netcdf/msg03585.html
                        # Basically, get the array sequence like other Tiffs
                        data_vals = numpy.flipud(data_vals)
                        band.WriteArray(data_vals)
                        raster.FlushCache()
                        raster = None

                        cgdal.gdal_translate_w_options(
                            tif := os.path.join(dst, filename_),
                            tmptif,
                            noData=data.no_data_value,
                        )

                        # validate COG
                        if (validate := cgdal.validate_cog("-q", tif)) == 0:
                            logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

                        # Append dictionary object to outfile list
                        outfile_list.append(
                            {
                                "filetype": "nohrsc-snodas-swe-corrections",
                                "file": tif,
                                "datetime": valid_time.isoformat(),
                                "version": None,
                            }
                        )
                        logger.debug(f"Outfile Append: {outfile_list[-1]}")
                    break

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None

    return outfile_list
