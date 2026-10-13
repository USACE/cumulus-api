"""
# Arkansas-Red Basin River Forecast Center

"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pyplugs
from cumulus_geoproc import logger
from cumulus_geoproc.utils import cgdal
from osgeo import gdal


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
        dst = Path(src).parent

    try:

        data_set, src_path, dst_path = cgdal.openfileGDAL(
            str(src), dst, GDALAccess="read_only"
        )

        for subdata_set in data_set.GetSubDatasets():
            nc_path, _ = subdata_set
            _, _, nc_variable = nc_path.split(":")
            if "time" in nc_variable.lower():
                data_set = gdal.Open(nc_path)
                _, _, time_units = data_set.GetMetadataItem("time#units").split()
                since_time = datetime.strptime(
                    time_units, "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=timezone.utc)
                bounds_time = data_set.ReadAsArray()[-1]
                valid_time = since_time + timedelta(hours=float(bounds_time[-1]))

            if "precipitation" in nc_variable.lower():
                tif = Path(dst).joinpath(Path(src).stem).with_suffix(".tif").as_posix()
                cgdal.gdal_translate_w_options(
                    tif,
                    data_set := gdal.Open(nc_path, gdal.GA_ReadOnly),
                )

        if tif:
            outfile_list.append(
                {
                    "filetype": acquirable,
                    "file": tif,
                    "datetime": valid_time.isoformat(),
                    "version": None,
                }
            )

    except RuntimeError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            "filename": Path(exc_traceback.tb_frame.f_code.co_filename).name,
            "line number": exc_traceback.tb_lineno,
            "method": exc_traceback.tb_frame.f_code.co_name,
            "type": exc_type.__name__,
            "message": exc_value,
        }
        for k, v in traceback_details.items():
            logger.error("{%s}: {%s}".format(k, v))
        return outfile_list
    finally:
        data_set = None

    return outfile_list
