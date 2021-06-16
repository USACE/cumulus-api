import logging
import os
import re
from uuid import uuid4
import numpy as np
from osgeo import gdal
from ..geoprocess.core.base import info, translate, create_overviews, write_array_to_raster
from datetime import datetime, timedelta

def process(infile, outdir):
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """
    outfile_list = list()

    # Variables and their product slug
    grid_variables = {
        "QPF": "naefs-mean-qpf-06h",
        # "QTF": "naefs-mean-qtf-06h"
    }
    
    # Each band in 'time' is a band in the variable
    time_ds = gdal.Open(f"NETCDF:{infile}:time")
    # Get the since minutes and compute band times
    time_band = time_ds.GetRasterBand(1)
    time_meta = time_band.GetMetadata_Dict()
    time_unit = time_meta["units"]
    # re pattern matching to get the start date from the 'time' units
    # yyyy-mm-dd HH:MM:SS
    pattern = re.compile(r"\d+-\d+-\d+ \d+:\d+:\d+")
    since_time_str = re.search(pattern, time_unit).group(0)
    since_time = datetime.fromisoformat(since_time_str)
    time_array = time_band.ReadAsArray().astype(np.dtype("float32"))
    date_array = [
        (lambda x: timedelta(minutes=int(x)) + since_time)(m)
        for m in time_array[0]
    ]
    print(f"Length of date array: {len(date_array)}")
    
    for grid_var, grid_slug in grid_variables.items():
        subdataset = gdal.Open(f"NETCDF:{infile}:{grid_var}")
        ds_meta = subdataset.GetMetadata_Dict()
        date_created_str = [
            re.search(pattern, v).group(0)
            for k, v in ds_meta.items()
            if "date_created" in k
        ]
        date_created = datetime.fromisoformat(date_created_str[0])
        print(f"{date_created=}")
        no_bands = subdataset.RasterCount
        print(f"RasterCount: {no_bands}")
        xsize = subdataset.RasterXSize
        ysize = subdataset.RasterYSize
        geo_transform = subdataset.GetGeoTransform()
        src_projection = subdataset.GetProjection()
        # src_spacial_ref = subdataset.GetSpatialRef()
        for b in range(1, no_bands):
            band_date = date_array[b]
            band_filename = "NAEFSmean_" + grid_var + band_date.strftime("%Y%m%d%H%M") + ".tif"
            # Get the band and process to raster
            band = subdataset.GetRasterBand(b)
            datatype = band.DataType
            nodata_value = band.GetNoDataValue()
            b_array = band.ReadAsArray(0, 0 , xsize, ysize).astype(np.dtype("float32"))
            # Create the raster
            tif = write_array_to_raster(
                b_array,
                os.path.join(outdir, f"temp-tif-{uuid4()}"),
                xsize,
                ysize,
                geo_transform,
                src_projection,
                datatype,
                nodata_value
            )
            # Create the overviews
            tif_with_overviews = create_overviews(tif)
            # COG with name based on time
            cog = translate(
                tif_with_overviews,
                os.path.join(
                    outdir,
                    band_filename
                )
            )

            outfile_list.append(
                { 
                    "filetype": grid_slug,
                    "file": cog,
                    "datetime": band_date.isoformat(),
                    "version": date_created.isoformat()
                }
            )

    return outfile_list
