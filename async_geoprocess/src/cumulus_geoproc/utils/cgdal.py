"""_summary_
"""

from osgeo import gdal

gdal.UseExceptions()


def gdal_translate_options(**kwargs):
    base = {
        "format": "GTiff",
        "creationOptions": ["TILED=YES", "COPY_SRC_OVERVIEWS=YES", "COMPRESS=DEFLATE"],
    }
    return {**base, **kwargs}


# def gdal_array_to_raster(
#     array, dst, transform, projection, nodata, driver="GTiff", *args, **kwargs
# ):
#     """utf8_path: str,
#     xsize: int,
#     ysize: int,
#     data_type,
#     bands: int = 1,
#     """

#     base_options = {"options": ["COMPRESS=DEFLATE", "TILED=YES"]}

#     driver = gdal.GetDriverByName(driver)
#     data_set = driver.Create(dst, *args, options={**base_options, **kwargs})

#     data_set.SetGeoTransform(transform)
#     data_set.SetProjection(projection)
#     data_set.GetRasterBand(1).SetNoDataValue(nodata)
#     data_set.GetRasterBand(1).WriteArray(array)
#     data_set.FlushCache()
#     data_set.GetRasterBand(1).GetStatistics(0, 1)


def band_generator(bands: "list[dict]"):
    pass
