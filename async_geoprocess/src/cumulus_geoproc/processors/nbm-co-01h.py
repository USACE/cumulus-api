import os
from collections import namedtuple
from uuid import uuid4
from datetime import datetime, timezone
from cumulus_geoproc.geoprocess.core.base import info, translate, create_overviews
from cumulus_geoproc.handyutils.core import change_final_file_extension
import pyplugs


@pyplugs.register
def process(infile, outdir):
    """National Blend of Models: Hourly air temperature and QPF

    Parameters
    ----------
    infile : String
        FQPN to file to process
    outdir : String
        Path to directory to save processed file

    Returns
    -------
    List of objects
        {
            "filetype": acquirable slug,
            "file": GeoTiff from processor,
            "datetime": datetime.isoformat(),
            "version": version.isoformat()
        }

    """

    outfile_list = list()

    # Process the gdal information
    fileinfo: dict = info(infile)
    all_bands = fileinfo["bands"]

    for band in all_bands:
        band_number = band["band"]
        metadata = band["metadata"][""]
        metadata_ = namedtuple("metadata_", metadata.keys())(**metadata)
        if (
            "temperature" in metadata_.GRIB_COMMENT.lower()
            and metadata_.GRIB_SHORT_NAME == "0-SFC"
        ):
            filetype = "nbm-co-airtemp"
        elif (
            "total precipitation" in metadata_.GRIB_COMMENT.lower()
            and metadata_.GRIB_ELEMENT == "QPF01"
        ):
            filetype = "nbm-co-qpf"
        else:
            continue

        # fromtimestamp with utc assignment gives proper iso format
        r_time = datetime.fromtimestamp(int(metadata_.GRIB_REF_TIME), timezone.utc)
        v_time = datetime.fromtimestamp(int(metadata_.GRIB_VALID_TIME), timezone.utc)

        tif = translate(
            infile,
            os.path.join(outdir, f"temp-tif-{uuid4()}"),
            extra_args=["-b", str(band_number)],
        )
        tif_with_overviews = create_overviews(tif)
        cog = translate(
            tif_with_overviews,
            os.path.join(
                outdir, change_final_file_extension(os.path.basename(infile), "tif")
            ),
        )

        outfile_list.append(
            {
                "filetype": filetype,
                "file": cog,
                "datetime": v_time.isoformat(),
                "version": r_time.isoformat(),
            }
        )

    return outfile_list
