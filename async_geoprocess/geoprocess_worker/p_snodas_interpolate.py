from datetime import datetime
import os
from pytz import utc
import uuid

from cumulus.snodas.core.interpolated_products import (
    create_interpolated_swe,
    create_interpolated_snowdepth,
    create_interpolated_snowtemp,
    create_interpolated_snowmelt,
    create_interpolated_coldcontent
)

import config as CONFIG

from helpers import (
    get_infile
)

import logging
logger = logging.getLogger(__name__)


def process(payload, outdir):

    dt = datetime.strptime(payload['datetime'], "%Y%m%d").replace(tzinfo=utc).replace(hour=6)
    max_distance = int(payload['max_distance'])

    # Keep track of the files that are processed
    processed_productfiles = []

    # ======
    # SWE
    # ======
    product_name = 'nohrsc-snodas-swe'
    key = f'cumulus/nohrsc-snodas-swe/zz_ssmv11034tS__T0001TTNATS{dt.strftime("%Y%m%d")}05HP001_cloud_optimized.tif'

    swe = get_infile(CONFIG.WRITE_TO_BUCKET, key, os.path.join(outdir, f'swe_{uuid.uuid4()}'))
    if not swe:
        logger.error(f'Unable to retrieve object with key: {key}')
        return None

    swe_interpolated = create_interpolated_swe(
        swe,
        dt,
        os.path.join(outdir, f'{product_name}_interpolated_{max_distance}_{dt.strftime("%Y%m%d")}.tif'),
        max_distance
    )

    processed_productfiles.append(
        {"filetype": f'{product_name}_interpolated', "file": swe_interpolated, "datetime": dt, "version": None}
    )


    # ==========
    # SNOW DEPTH
    # ==========
    product_name = "nohrsc-snodas-snowdepth"
    key = f'cumulus/nohrsc-snodas-snowdepth/zz_ssmv11036tS__T0001TTNATS{dt.strftime("%Y%m%d")}05HP001_cloud_optimized.tif'
    snowdepth = get_infile(CONFIG.WRITE_TO_BUCKET, key, os.path.join(outdir, f'snowdepth_{uuid.uuid4()}'))
    if not snowdepth:
        logger.error(f'Unable to retrieve object with key: {key}')
        return None
    
    snowdepth_interpolated = create_interpolated_snowdepth(
        snowdepth,
        dt,
        os.path.join(
            outdir, f'{product_name}-interpolated-{max_distance}-{dt.strftime("%Y%m%d")}.tif'
        ),
        max_distance
    )

    processed_productfiles.append(
        {"filetype": f'{product_name}-interpolated', "file": snowdepth_interpolated, "datetime": dt, "version": None}
    )

    # ============================
    # SNOWPACK AVERAGE TEMPERATURE
    # ============================
    product_name = 'nohrsc-snodas-snowpack-average-temperature'
    key = f'cumulus/nohrsc-snodas-snowpack-average-temperature/zz_ssmv11038wS__A0024TTNATS{dt.strftime("%Y%m%d")}05DP001_cloud_optimized.tif'
    snowtemp = get_infile(CONFIG.WRITE_TO_BUCKET, key, os.path.join(outdir, f'snowtemp_{uuid.uuid4()}'))
    if not snowtemp:
        logger.error(f'Unable to retrieve object with key: {key}')
        return None

    snowtemp_interpolated = create_interpolated_snowtemp(
        snowtemp,
        swe_interpolated,
        dt,
        max_distance,
        os.path.join(
            outdir, f'{product_name}-interpolated-{max_distance}-{dt.strftime("%Y%m%d")}.tif'
        )
    )

    processed_productfiles.append(
        {"filetype": f'{product_name}-interpolated', "file": snowtemp_interpolated, "datetime": dt, "version": None}
    )        

    # ========
    # SNOWMELT
    # ========
    product_name = 'nohrsc-snodas-snowmelt'
    key = f'cumulus/nohrsc-snodas-snowmelt/zz_snowmeltmm_{dt.strftime("%Y%m%d")}_cloud_optimized.tif'
    snowmelt = get_infile(CONFIG.WRITE_TO_BUCKET, key, os.path.join(outdir, f'snowmelt_{uuid.uuid4()}'))
    if not snowmelt:
        logger.error(f'Unable to retrieve object with key: {key}')
        return None
    
    snowmelt_interpolated = create_interpolated_snowmelt(
        snowmelt,
        swe_interpolated,
        dt,
        max_distance,
        os.path.join(
            outdir, f'{product_name}-interpolated-{max_distance}-{dt.strftime("%Y%m%d")}.tif'
        )
    )
    processed_productfiles.append(
        {"filetype": f'{product_name}-interpolated', "file": snowmelt_interpolated, "datetime": dt, "version": None}
    )

    # ============
    # COLD CONTENT
    # ============
    product_name = 'nohrsc-snodas-coldcontent'
    key = f'cumulus/nohrsc-snodas-coldcontent/zz_coldcontent_{dt.strftime("%Y%m%d")}_cloud_optimized.tif'
    coldcontent = get_infile(CONFIG.WRITE_TO_BUCKET, key, os.path.join(outdir, f'coldcontent_{uuid.uuid4()}'))
    if not coldcontent:
        logger.error(f'Unable to retrieve object with key: {key}')
        return None
    
    coldcontent_interpolated = create_interpolated_coldcontent(
        snowtemp_interpolated,
        swe_interpolated,
        os.path.join(outdir, f'{product_name}-interpolated-{max_distance}-{dt.strftime("%Y%m%d")}.tif')
    )

    processed_productfiles.append(
        {"filetype": f'{product_name}-interpolated', "file": coldcontent_interpolated, "datetime": dt, "version": None}
    )

    return processed_productfiles