"""
# Weather Research and Forecasting (WRF)

A next-generation mesoscale numerical weather prediction system designed for both atmospheric research and operational forecasting applications.

**details** [here](https://www.mmm.ucar.edu/weather-research-and-forecasting-model)

## WRF Columbia River Basin

**WRF Domain 3**
"""


import math
import os
import sys
from datetime import timezone

import numpy
import pyplugs
from cumulus_geoproc import logger
from netCDF4 import Dataset, date2index, num2date
from osgeo import gdal, osr
from pyresample import geometry
from pyresample.bilinear import NumpyBilinearResampler

# netCDF file "var" variable standard_name attribute
standard_name = {
    "TDP": "dewpntt",
    "TSK": "groundt",
    "GLW": "lwdown",
    "PRECIPAH": "precipah",
    "PSFC": "pstarcrs",
    "RH": "rh",
    "SWDOWN": "swdown",
    "T2": "t2",
    "U10": "u10",
    "V10": "v10",
    "EA": "vaporps",
}


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

    if dst is None:
        dst = os.path.dirname(src)

    xmin = -2304000
    ymin = 2034000
    xmax = -804000
    ymax = 3624000
    xres = 2000
    yres = 2000

    proj4_albers = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"
    srs = osr.SpatialReference()
    srs.ImportFromProj4(proj4_albers)
    wkt_albers = srs.ExportToWkt()

    ncols = math.floor((xmax - xmin) / xres)
    nrows = math.floor((ymax - ymin) / yres)
    nodata_value = -9999

    try:
        # extract the single grid from the source and create a temporary netCDF file
        with Dataset(src, "r") as ncsrc:
            nctime = ncsrc.variables["time"]
            nclat = ncsrc.variables["lat"]
            nclat_arr = nclat[1:-1, 1:-1]
            nclon = ncsrc.variables["lon"]
            nclon_arr = nclon[1:-1, 1:-1]

            # each netCDF file is a parameter and defined by the var standard_name attribute
            ncvar = ncsrc.variables["var"]
            parameter_name = standard_name[(ncvar.standard_name).strip()]
            product_slug = f"wrf-columbia-{parameter_name}"

            # pyresample uses center of lower left pixel
            xmin_pxl = xmin + (xres * 0.5)
            ymin_pxl = ymin + (yres * 0.5)

            # Make target arrays for cell centroids
            # Using "ncols" (and not ncols -1) in order to include that last pixel in np.arrange
            # These are 1d arrays
            xcoords = numpy.arange(xmin_pxl, xmin_pxl + (ncols * xres), xres)
            ycoords = numpy.arange(ymin_pxl, ymin_pxl + (nrows * yres), yres)

            # Source Geometry
            source_geometry = geometry.SwathDefinition(lons=nclon_arr, lats=nclat_arr)

            # Target Geometry
            area_extent = (
                min(xcoords) - xres * 0.5,
                min(ycoords) - yres * 0.5,
                max(xcoords) + xres * 0.5,
                max(ycoords) + yres * 0.5,
            )
            target_geometry = geometry.AreaDefinition(
                "wrf_columbia",
                "Albers Equal Area",
                "aea",
                wkt_albers,
                len(xcoords),
                len(ycoords),
                area_extent,
            )

            # 5000 left some nodata cells so going with 6000 m
            resampler = NumpyBilinearResampler(source_geometry, target_geometry, 6000)

            for dt in num2date(
                nctime[:], nctime.units, only_use_cftime_datetimes=False
            ):
                dt_valid = dt.replace(tzinfo=timezone.utc)
                idx = date2index(dt, nctime)
                ncvar = ncsrc.variables["var"][idx]
                ncvar_arr = ncvar[1:-1, 1:-1]

                # resample to target
                ncvar_arr_resampled = resampler.resample(
                    ncvar_arr, fill_value=nodata_value
                )

                tiffile = os.path.join(
                    dst,
                    ".".join(
                        [
                            product_slug,
                            dt_valid.strftime("%Y_%m_%d_%H"),
                            "tif",
                        ]
                    ),
                )
                # Create() GTiff with resampled Albers data
                raster = gdal.GetDriverByName("GTiff").Create(
                    f"/vsimem/{tiffile}",
                    xsize=ncols,
                    ysize=nrows,
                    bands=1,
                    eType=gdal.GDT_Float32,
                )
                raster.SetGeoTransform([xmin, xres, 0, ymax, 0, -yres])
                raster.SetProjection(wkt_albers)
                raster.GetRasterBand(1).SetNoDataValue(nodata_value)
                raster.GetRasterBand(1).WriteArray(ncvar_arr_resampled)

                raster = None

                # Translate newly created GTiff to COG because COG does not have Create() method
                gdal.Translate(
                    tiffile,
                    f"/vsimem/{tiffile}",
                    format="COG",
                    outputType=gdal.GDT_Float32,
                    resampleAlg="bilinear",
                    creationOptions=[
                        "COMPRESS=DEFLATE",
                        "PREDICTOR=2",
                    ],
                )

                outfile_list.append(
                    {
                        "filetype": product_slug,
                        "file": tiffile,
                        "datetime": dt_valid.isoformat(),
                        "version": None,
                    }
                )

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            "filename": os.path.basename(exc_traceback.tb_frame.f_code.co_filename),
            "line number": exc_traceback.tb_lineno,
            "method": exc_traceback.tb_frame.f_code.co_name,
            "type": exc_type.__name__,
            "message": exc_value,
        }
        for k, v in traceback_details.items():
            logger.error(f"{k}: {v}")
    return outfile_list
