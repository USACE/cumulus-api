"""NSIDC SWE v1
"""

# TODO: Refactor to new geoprocess package

import os
import re
from datetime import datetime, timedelta

import numpy as np
import pyplugs
from osgeo import gdal

this = os.path.basename(__file__)

# plugin not available when decorator commented out
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

    # Variables and their product slug
    nc_variables = {"SWE": "nsidc-ua-swe-v1", "DEPTH": "nsidc-ua-snowdepth-v1"}

    day_since_pattern = re.compile(r"\d+-\d+-\d+")
    day2date = lambda m, t: timedelta(days=int(m)) + t
    for nc_variable, nc_slug in nc_variables.items():
        subdataset = gdal.Open(f"NETCDF:{src}:{nc_variable}")
        subset_meta_dict = subdataset.GetMetadata_Dict()
        # Band last time, since time, and date created as last time
        subset_times = subset_meta_dict["NETCDF_DIM_time_VALUES"]
        subset_last_time = list(eval(subset_times))[-1]
        subset_time_unit = subset_meta_dict["time#units"]
        subset_since_str = re.search(day_since_pattern, subset_time_unit).group(0)
        subset_since_time = datetime.fromisoformat(subset_since_str)
        date_created = day2date(subset_last_time, subset_since_time)
        # Define some geo
        geo_transform = subdataset.GetGeoTransform()
        src_projection = subdataset.GetProjection()

        for b in range(1, subdataset.RasterCount + 1):
            band = subdataset.GetRasterBand(b)
            # Band metadata
            band_meta_dict = band.GetMetadata_Dict()
            # Band time in minutes and compute the date for the band's filename
            band_time_day = band_meta_dict["NETCDF_DIM_time"]
            band_date = day2date(band_time_day, subset_since_time)
            band_filename = nc_slug + "_" + band_date.strftime("%Y%m%d") + ".tif"

            # Get the band and process to raster
            xsize = band.XSize
            ysize = band.YSize
            datatype = band.DataType
            nodata_value = band.GetNoDataValue()
            b_array = band.ReadAsArray(0, 0, xsize, ysize).astype(np.dtype("float32"))
            # Create the raster
            # tif = write_array_to_raster(
            #     b_array,
            #     os.path.join(outdir, f"temp-tif-{uuid4()}"),
            #     xsize,
            #     ysize,
            #     geo_transform,
            #     src_projection,
            #     datatype,
            #     nodata_value,
            # )
            # # Create the overviews
            # tif_with_overviews = create_overviews(tif)
            # # COG with name based on time
            # cog = translate(tif_with_overviews, os.path.join(outdir, band_filename))

            # outfile_list.append(
            #     {
            #         "filetype": nc_slug,
            #         "file": cog,
            #         "datetime": band_date.replace(tzinfo=timezone.utc).isoformat(),
            #         "version": None,
            #     }
            # )

    return outfile_list
