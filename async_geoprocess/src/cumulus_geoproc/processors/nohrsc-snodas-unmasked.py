"""NOHRSC SNODAS Unmasked
"""

import os
from datetime import datetime, timezone

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.geoprocess import snodas
from cumulus_geoproc.geoprocess.snodas import metaparse
from cumulus_geoproc.utils import boto, cgdal, file_extension

from osgeo import gdal

gdal.UseExceptions()

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

    paramater_codes = ["1034", "1036", "1038", "1044"]

    try:
        # download tar to destination (temporary directory)
        bucket, key = src.split("/", maxsplit=1)
        logger.debug(f"s3_download_file({bucket=}, {key=})")

        src_ = boto.s3_download_file(bucket=bucket, key=key, dst=dst)
        logger.debug(f"S3 Downloaded File: {src_}")

        # decompress the tar and gzip files in the tar
        decompressed_files = utils.decompress(src_, dst, recursive=True)
        if not os.path.isdir(decompressed_files):
            raise Exception(f"Not a directory: {decompressed_files}")

        # generator for only the files ending with .txt
        txt_files = (f for f in os.listdir(decompressed_files) if f.endswith(".txt"))

        translate_to_tif = {}
        # create tif files for only the files needed
        for txt_file in txt_files:
            snodas_product_code = txt_file[8:12]
            if snodas_product_code in paramater_codes:
                fqpn = os.path.join(decompressed_files, txt_file)
                meta_ntuple = metaparse.to_namedtuple(fqpn)
                data_filename = meta_ntuple.data_file_pathname
                region = txt_file[:2]
                stop_date = datetime(
                    meta_ntuple.stop_year,
                    meta_ntuple.stop_month,
                    meta_ntuple.stop_day,
                    meta_ntuple.stop_hour,
                    meta_ntuple.stop_minute,
                    meta_ntuple.stop_second,
                    tzinfo=timezone.utc,
                )

                # FQPN to data file
                datafile_pathname = os.path.join(decompressed_files, data_filename)
                logger.debug(f"Data File Path: {datafile_pathname}")

                # write hdr so gdal can tranlate
                hdr_file = metaparse.write_hdr(
                    fqpn, meta_ntuple.number_of_columns, meta_ntuple.number_of_rows
                )
                # translate to tif
                if hdr_file is not None:
                    # set translate options
                    translate_options = cgdal.gdal_translate_options(
                        format="COG",
                        bandList=[1],
                        outputSRS=f"+proj=longlat +ellps={meta_ntuple.horizontal_datum} +datum={meta_ntuple.horizontal_datum} +no_defs",
                        noData=int(meta_ntuple.no_data_value),
                        outputBounds=[
                            meta_ntuple.minimum_x_axis_coordinate,
                            meta_ntuple.maximum_y_axis_coordinate,
                            meta_ntuple.maximum_x_axis_coordinate,
                            meta_ntuple.minimum_y_axis_coordinate,
                        ],
                    )
                    ds = gdal.Open(datafile_pathname, gdal.GA_ReadOnly)
                    gdal.Translate(
                        tif := file_extension(datafile_pathname, suffix=".tif"),
                        ds,
                        **translate_options,
                    )
                    ds = None

                    # set metadata to band 1
                    tif_ds = gdal.Open(datafile_pathname, gdal.GA_ReadOnly)
                    metadata_options = [
                        f"{field_.upper()}={str(getattr(meta_ntuple, field_))}"
                        for field_ in meta_ntuple._fields
                    ]
                    tif_ds.GetRasterBand(1).SetMetadata(metadata_options)
                    tif_ds = None

                    # add tif dictionary to compute cold content
                    translate_to_tif[snodas_product_code] = {
                        "file": tif,
                        "filetype": snodas.product_code[snodas_product_code]["product"],
                        "datetime": stop_date.isoformat(),
                        "version": None,
                    }
                    logger.debug(f"Update Tif: {translate_to_tif[snodas_product_code]}")

        # cold content = swe * 2114 * snowtemp (degc) / 333000
        translate_to_tif.update(snodas.cold_content(translate_to_tif))

        # convert snow melt to mm
        translate_to_tif.update(snodas.snow_melt_mm(translate_to_tif))

        outfile_list.extend(list(translate_to_tif.values()))

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None

    return outfile_list


if __name__ == "__main__":
    pass
