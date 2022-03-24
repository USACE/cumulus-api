import logging
import os
import re
from uuid import uuid4
import numpy as np
from osgeo import gdal
from ..geoprocess.core.base import (
    info,
    translate,
    create_overviews,
    write_array_to_raster,
)
from datetime import datetime, timedelta, timezone
import pyplugs


@pyplugs.register
def process(infile, outdir):
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """
    outfile_list = list()

    # Variables and their product slug
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
                "NAEFSmean_" + nc_variable + band_date.strftime("%Y%m%d%H%M") + ".tif"
            )
            # Get the band and process to raster
            band = subdataset.GetRasterBand(b)
            xsize = band.XSize
            ysize = band.YSize
            datatype = band.DataType
            nodata_value = band.GetNoDataValue()
            b_array = band.ReadAsArray(0, 0, xsize, ysize).astype(np.dtype("float32"))
            # Create the raster
            tif = write_array_to_raster(
                b_array,
                os.path.join(outdir, f"temp-tif-{uuid4()}"),
                xsize,
                ysize,
                geo_transform,
                src_projection,
                datatype,
                nodata_value,
            )
            # Create the overviews
            tif_with_overviews = create_overviews(tif)
            # COG with name based on time
            cog = translate(tif_with_overviews, os.path.join(outdir, band_filename))

            outfile_list.append(
                {
                    "filetype": nc_slug,
                    "file": cog,
                    "datetime": band_date.replace(tzinfo=timezone.utc).isoformat(),
                    "version": date_created.replace(tzinfo=timezone.utc).isoformat(),
                }
            )

    return outfile_list
