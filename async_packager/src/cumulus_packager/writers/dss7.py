"""DSS7 package writer"""

import json
import logging
import os
import sys
import threading
from collections import namedtuple
from pathlib import Path
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy
import psutil
import pyplugs
from codetiming import Timer
from cumulus_packager import dssutil, logger
from cumulus_packager.configurations import PACKAGER_UPDATE_INTERVAL
from cumulus_packager.packager.handler import PACKAGE_STATUS, update_status
from osgeo import gdal, osr, gdalconst

from hecdss import HecDss
from hecdss.gridded_data import GriddedData
from importlib.metadata import version, PackageNotFoundError

gdal.UseExceptions()

# Configure GDAL for optimal S3 streaming performance
gdal.SetConfigOption('GDAL_HTTP_MAX_RETRY', '3')
gdal.SetConfigOption('GDAL_HTTP_RETRY_DELAY', '1')
gdal.SetConfigOption('CPL_VSIL_CURL_CHUNK_SIZE', '10485760')  # 10MB chunks
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS', '.tif,.tiff')
gdal.SetConfigOption('VSI_CACHE', 'TRUE')
gdal.SetConfigOption('VSI_CACHE_SIZE', '100000000')  # 100MB cache
gdal.SetCacheMax(512 * 1024 * 1024)  # 512MB GDAL block cache

def get_available_memory_gb():
    """
    Get available system memory in GB, respecting Docker container limits.

    Returns:
    --------
    float : Available memory in GB
    """
    try:
        # Try to read Docker cgroup memory limit first (cgroup v2)
        cgroup_v2_path = '/sys/fs/cgroup/memory.max'
        if os.path.exists(cgroup_v2_path):
            with open(cgroup_v2_path, 'r') as f:
                limit = f.read().strip()
                if limit != 'max':
                    memory_limit_bytes = int(limit)
                    memory_limit_gb = memory_limit_bytes / (1024 ** 3)
                    logger.info(f"Detected Docker memory limit (cgroup v2): {memory_limit_gb:.2f} GB")
                    return memory_limit_gb

        # Try cgroup v1
        cgroup_v1_path = '/sys/fs/cgroup/memory/memory.limit_in_bytes'
        if os.path.exists(cgroup_v1_path):
            with open(cgroup_v1_path, 'r') as f:
                memory_limit_bytes = int(f.read().strip())
                # Check if limit is unreasonably high (indicates no limit set)
                if memory_limit_bytes < (1024 ** 4):  # Less than 1TB
                    memory_limit_gb = memory_limit_bytes / (1024 ** 3)
                    logger.info(f"Detected Docker memory limit (cgroup v1): {memory_limit_gb:.2f} GB")
                    return memory_limit_gb

        # Fall back to psutil if no cgroup limit found
        available_memory_bytes = psutil.virtual_memory().available
        available_memory_gb = available_memory_bytes / (1024 ** 3)
        logger.info(f"Detected available system memory: {available_memory_gb:.2f} GB")
        return available_memory_gb
    except Exception as e:
        logger.warning(f"Failed to detect available memory: {e}. Using default 4.0 GB")
        return 4.0

def get_optimal_workers():
    """
    Get optimal number of worker threads based on available CPU cores,
    respecting Docker container limits.
    Uses 2x CPU cores since this is an I/O-bound workload (S3 streaming reads).

    Returns:
    --------
    int : Optimal number of worker threads
    """
    try:
        cpu_count = None

        # Try to read Docker cgroup CPU quota (cgroup v2)
        cgroup_v2_max = '/sys/fs/cgroup/cpu.max'
        if os.path.exists(cgroup_v2_max):
            with open(cgroup_v2_max, 'r') as f:
                content = f.read().strip().split()
                if len(content) == 2 and content[0] != 'max':
                    quota = int(content[0])
                    period = int(content[1])
                    cpu_count = max(1, int(quota / period))
                    logger.info(f"Detected Docker CPU limit (cgroup v2): {cpu_count} CPU(s)")

        # Try cgroup v1
        if cpu_count is None:
            cgroup_v1_quota = '/sys/fs/cgroup/cpu/cpu.cfs_quota_us'
            cgroup_v1_period = '/sys/fs/cgroup/cpu/cpu.cfs_period_us'
            if os.path.exists(cgroup_v1_quota) and os.path.exists(cgroup_v1_period):
                with open(cgroup_v1_quota, 'r') as f:
                    quota = int(f.read().strip())
                with open(cgroup_v1_period, 'r') as f:
                    period = int(f.read().strip())
                if quota > 0:
                    cpu_count = max(1, int(quota / period))
                    logger.info(f"Detected Docker CPU limit (cgroup v1): {cpu_count} CPU(s)")

        # Fall back to system CPU count
        if cpu_count is None:
            cpu_count = os.cpu_count()
            if cpu_count is None:
                logger.warning("Could not detect CPU count. Using default 8 workers")
                return 8
            logger.info(f"Detected {cpu_count} CPU cores (no container limit)")

        # Use 2x CPU count for I/O-bound operations (S3 reads + processing)
        optimal_workers = cpu_count * 2
        logger.info(f"Using {optimal_workers} worker threads (2x CPU count)")
        return optimal_workers
    except Exception as e:
        logger.warning(f"Failed to detect CPU count: {e}. Using default 8 workers")
        return 8

def calculate_optimal_queue_size(bbox_width, bbox_height, available_memory_gb=None, max_queue_memory_percent=0.5):
    """
    Calculate optimal bounded queue size based on bbox dimensions and available memory.

    Parameters:
    -----------
    bbox_width : int
        Width of bounding box in pixels
    bbox_height : int
        Height of bounding box in pixels
    available_memory_gb : float, optional
        Available RAM in GB (default: None, auto-detects system memory)
    max_queue_memory_percent : float
        Maximum percentage of available memory to use for queue (default: 0.5 = 50%)

    Returns:
    --------
    int : Recommended queue size
    """
    # Auto-detect available memory if not provided
    if available_memory_gb is None:
        available_memory_gb = get_available_memory_gb()

    # Double type (float64) = 8 bytes per element
    bytes_per_element = 8

    # Calculate size of one result
    pixels_per_result = bbox_width * bbox_height
    bytes_per_result = pixels_per_result * bytes_per_element
    mb_per_result = bytes_per_result / (1024 * 1024)

    # Calculate memory budget for queue
    available_memory_bytes = available_memory_gb * 1024 * 1024 * 1024
    queue_memory_budget_bytes = available_memory_bytes * max_queue_memory_percent

    # Calculate optimal queue size
    optimal_queue_size = int(queue_memory_budget_bytes / bytes_per_result)

    # Apply practical limits (min: 10, max: 1000)
    optimal_queue_size = max(10, min(1000, optimal_queue_size))

    logger.debug(
        f"Queue size calculated: {optimal_queue_size} "
        f"(bbox: {bbox_width}x{bbox_height}, "
        f"{mb_per_result:.2f}MB per result, "
        f"~{optimal_queue_size * mb_per_result:.1f}MB total queue memory)"
    )

    return optimal_queue_size


def process_single_tiff_gdal(args):
    """
    Process a single TIFF file with GDAL, create GriddedData object, and compress - all in parallel.

    Parameters:
    -----------
    args : tuple
        (idx, tif_config, _bbox, cellsize, destination_srs, grid_type, grid_type_name,
         srs_definition, _extent_name, tz_name, tz_offset, is_interval)

    Returns:
    --------
    dict : Result dictionary with success status, GriddedData object, and compressed data
    """
    import zlib

    (idx, tif, _bbox, cellsize, destination_srs, grid_type, grid_type_name,
     srs_definition, _extent_name, tz_name, tz_offset, is_interval) = args

    try:
        TifCfg = namedtuple("TifCfg", tif)(**tif)
        s3_path = f"/vsis3_streaming/{TifCfg.bucket}/{TifCfg.key}"

        # Open and warp the TIFF with GDAL
        ds = gdal.Open(s3_path)
        if ds is None:
            return {
                'success': False,
                'index': idx,
                'error': f"Failed to open {TifCfg.key}"
            }

        # GDAL Warp the Tiff to what we need for DSS
        warp_ds = gdal.Warp(
            '',  # empty string => no filename, return a Dataset
            ds,
            format='MEM',  # in-RAM driver
            outputBounds=_bbox,
            xRes=cellsize,
            yRes=cellsize,
            targetAlignedPixels=True,
            dstSRS=destination_srs.ExportToWkt(),
            resampleAlg=gdalconst.GRA_Bilinear,
            copyMetadata=False,
        )

        if warp_ds is None:
            ds = None
            return {
                'success': False,
                'index': idx,
                'error': f"Failed to warp {TifCfg.key}"
            }

        # Read the warped data
        band = warp_ds.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        data = band.ReadAsArray().astype(numpy.float32, copy=False)

        # Flip the dataset up/down because tif and dss have different origins
        data = numpy.flipud(data)

        # Replace nodata with NaN
        if nodata is not None:
            data[data == nodata] = numpy.nan

        # Get geotransform for lower left coordinates
        xsize = warp_ds.RasterXSize
        ysize = warp_ds.RasterYSize
        adfGeoTransform = warp_ds.GetGeoTransform()
        llx = int(adfGeoTransform[0] / adfGeoTransform[1])
        lly = int((adfGeoTransform[5] * ysize + adfGeoTransform[3]) / adfGeoTransform[1])

        # Clean up GDAL objects
        band = None
        warp_ds = None
        ds = None

        # Prepare data for DSS
        DSS_UNDEFINED_VALUE = -3.4028234663852886e+38
        data[numpy.isnan(data)] = DSS_UNDEFINED_VALUE

        # Create DSS pathname
        data_type = dssutil.data_type[TifCfg.dss_datatype]
        dsspathname = f"/{grid_type_name}/{_extent_name}/{TifCfg.dss_cpart}/{TifCfg.dss_dpart}/{TifCfg.dss_epart}/{TifCfg.dss_fpart}/"

        # Create GriddedData object (in parallel worker)
        gd = GriddedData.create(
            path=dsspathname,
            type=grid_type,
            dataType=data_type,
            lowerLeftCellX=llx,
            lowerLeftCellY=lly,
            numberOfCellsX=xsize,
            numberOfCellsY=ysize,
            srsName=grid_type_name,
            srsDefinitionType=1,
            srsDefinition=srs_definition,
            dataUnits=TifCfg.dss_unit,
            dataSource="INTERNAL",
            timeZoneID=tz_name,
            timeZoneRawOffset=tz_offset,
            isInterval=is_interval,
            isTimeStamped=1,
            cellSize=cellsize,
            xCoordOfGridCellZero=0.0,
            yCoordOfGridCellZero=0.0,
            nullValue=DSS_UNDEFINED_VALUE,
            data=data,
        )

        gd.data = None  # Free data reference in GriddedData

        # Compress the grid data (parallel compression in worker process)
        raw_bytes = data.astype(numpy.float32).tobytes()
        compressed_data = zlib.compress(raw_bytes)
        compressed_size = len(compressed_data)

        return {
            'success': True,
            'index': idx,
            'tif_key': TifCfg.key,
            'gd': gd,
            'compressed_data': compressed_data,
            'compressed_size': compressed_size
        }

    except Exception as e:
        logger.error(f"Error processing TIFF {idx}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'index': idx,
            'error': str(e)
        }


def process_tiffs_with_bounded_queue(src, _bbox, cellsize, destination_srs, dss,
                                     grid_type, grid_type_name, srs_definition,
                                     _extent_name, tz_name, tz_offset, is_interval,
                                     id, gridcount, max_workers=None):
    """
    Process TIFF files using GDAL in parallel with compression and bounded queue.
    Uses parallel compression + precompressed writes for optimal performance.

    Workers perform GDAL processing, GriddedData creation, and compression in parallel.
    The main thread simply writes precompressed GriddedData objects to DSS using
    writePrecompressedGrid for maximum efficiency.

    Parameters:
    -----------
    src : list
        List of TIFF file configurations
    _bbox : list
        Bounding box [minX, minY, maxX, maxY] in geographic coordinates
    cellsize : float
        Cell size in destination SRS units
    destination_srs : osr.SpatialReference
        Destination spatial reference system
    dss : HecDss
        Open DSS file handle to write to
    grid_type : int
        DSS grid type
    grid_type_name : str
        DSS grid type name
    srs_definition : str
        Spatial reference definition
    _extent_name : str
        Extent name for DSS path
    tz_name : str
        Timezone name
    tz_offset : int
        Timezone offset
    is_interval : int
        Is interval flag
    id : str
        Download ID for progress tracking
    gridcount : int
        Total number of grids for progress calculation
    max_workers : int, optional
        Number of parallel worker threads (default: None, auto-detects CPU cores)

    Returns:
    --------
    int : Number of successfully processed files
    """
    # Auto-detect optimal number of workers if not provided
    if max_workers is None:
        max_workers = get_optimal_workers()

    try:
        # Estimate bbox dimensions for queue sizing
        first_tif = src[0]
        test_path = f"/vsis3_streaming/{first_tif['bucket']}/{first_tif['key']}"

        ds = gdal.Open(test_path)
        if ds is None:
            logger.warning("Cannot open first file for parallel processing")
            return 0

        # Estimate dimensions based on bbox and cellsize
        bbox_width = int((_bbox[2] - _bbox[0]) / cellsize)
        bbox_height = int((_bbox[3] - _bbox[1]) / cellsize)

        ds = None

        if bbox_width <= 0 or bbox_height <= 0:
            logger.warning(f"Invalid bbox dimensions: {bbox_width}x{bbox_height}")
            return 0

        logger.info(f"Using parallel GDAL processing with compression for {len(src)} files with estimated bbox {bbox_width}x{bbox_height} pixels")

        # Calculate optimal queue size
        queue_size = calculate_optimal_queue_size(bbox_width, bbox_height)

        # Create bounded queue (maxsize limits memory usage)
        result_queue = Queue(maxsize=queue_size)

        processed_count = 0
        _progress = 0

        # Producer function: reads TIFFs in parallel and puts results in queue
        def producer():
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Prepare arguments for parallel processing (includes all GriddedData parameters)
                tasks = [
                    (idx, tif, _bbox, cellsize, destination_srs, grid_type, grid_type_name,
                     srs_definition, _extent_name, tz_name, tz_offset, is_interval)
                    for idx, tif in enumerate(src)
                ]

                # Submit all tasks and process as they complete
                future_to_idx = {
                    executor.submit(process_single_tiff_gdal, task): task[0]
                    for task in tasks
                }

                for future in as_completed(future_to_idx):
                    result = future.result()
                    result_queue.put(result)

            # Signal completion
            result_queue.put(None)

        # Start producer thread
        producer_thread = threading.Thread(target=producer)
        producer_thread.start()

        # Consumer (main thread): write pre-created, precompressed GriddedData objects to DSS
        logger.info(f"Processing {len(src)} files with parallel compression and precompressed writes (queue size: {queue_size}, workers: {max_workers})")

        while True:
            try:
                result = result_queue.get(timeout=300)  # 5 minute timeout

                # None signals completion
                if result is None:
                    break

                if result['success']:
                    try:
                        # Extract pre-created GriddedData and compressed data from worker
                        gd = result['gd']
                        compressed_data = result['compressed_data']
                        compressed_size = result['compressed_size']
                        tif_key = result['tif_key']

                        # Write precompressed data to DSS (GriddedData already created in worker)
                        t = Timer(name="accumuluated", logger=None)
                        t.start()
                        dss_result = dss.writePrecompressedGrid(gd, compressed_data, compressed_size)
                        elapsed_time = t.stop()

                        if dss_result != 0:
                            logger.warning(f'HEC-DSS-PY write record failed for "{tif_key}": {dss_result}')
                        elif logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f'DSS writePrecompressedGrid processed "{tif_key}" in {elapsed_time:.4f}s')

                        processed_count += 1

                        # Update progress
                        _progress = int((processed_count / gridcount) * 100)
                        if processed_count % PACKAGER_UPDATE_INTERVAL == 0 or processed_count == gridcount:
                            update_status(id=id, status_id=PACKAGE_STATUS["INITIATED"], progress=_progress)
                            if _progress % PACKAGER_UPDATE_INTERVAL == 0:
                                logger.info(f'Download ID "{id}" progress: {_progress}% (queue: ~{result_queue.qsize()}/{queue_size})')

                        # Explicitly free memory after writing to DSS
                        compressed_data = None
                        gd = None

                    except Exception as e:
                        logger.error(f"Error writing to DSS for file {result['index']}: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        continue
                else:
                    logger.error(f"Error processing file {result['index']}: {result.get('error', 'Unknown error')}")

            except Empty:
                logger.error("Timeout waiting for results from queue")
                break

        producer_thread.join()

        logger.info(f"Parallel GDAL with compression: Successfully processed {processed_count}/{len(src)} files")
        return processed_count

    except Exception as e:
        logger.error(f"Parallel GDAL processing failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 0


@pyplugs.register
def writer(
    id: str,
    src: str,
    extent: str,
    dst: str,
    cellsize: float,
    dst_srs: str = "EPSG:5070",
):
    """Packager writer plugin

    Parameters
    ----------
    id : str
        Download ID
    src : list
        List of objects describing the GeoTiff (COG)
    extent : dict
        Object with watershed name and bounding box
    dst : str
        Temporary directory
    cellsize : float
        Grid resolution
    dst_srs : str, optional
        Destination Spacial Reference, by default "EPSG:5070"

    Returns
    -------
    str
        FQPN to dss file
    """

    try:
        pkg_version = version("hecdss")
    except Exception:
        pkg_version = "unknown"
    logger.info(
        f"Write Records to DSS using hecdss {pkg_version}",
    )

    # convert the strings back to json objects; needed for pyplugs
    src = json.loads(src)
    gridcount = len(src)
    extent = json.loads(extent)
    _extent_name = extent["name"]
    _bbox = extent["bbox"]
    _progress = 0

    # assuming destination spacial references are all EPSG
    destination_srs = osr.SpatialReference()
    epsg_code = dst_srs.split(":")[-1]
    destination_srs.ImportFromEPSG(int(epsg_code))

    ###### this can go away when the payload has the resolution ######
    if epsg_code == "26906":
        grid_type_name = "UTM6N"
        grid_type = 430
    else:
        grid_type_name = "SHG"
        grid_type = dssutil.dss_grid_type[grid_type_name]
    logger.info(
        f"grid type name {grid_type_name}",
    )
    srs_definition = dssutil.spatial_reference_definition[grid_type_name]
    tz_name = "GMT"
    tz_offset = dssutil.time_zone[tz_name]
    is_interval = 1

    dssfilename = Path(dst).joinpath(id).with_suffix(".dss").as_posix()

    with HecDss(dssfilename) as dss:
        # Use parallel GDAL processing with compression and precompressed writes for multiple files
        if len(src) > 1:
            logger.info("Using parallel GDAL processing with compression and precompressed writes")
            processed_count = process_tiffs_with_bounded_queue(
                src, _bbox, cellsize, destination_srs, dss,
                grid_type, grid_type_name, srs_definition,
                _extent_name, tz_name, tz_offset, is_interval,
                id, gridcount
            )
            _progress = int((processed_count / gridcount) * 100) if processed_count > 0 else 0
        # Single file - process sequentially
        else:
            logger.info("Processing single file with GDAL")
            for idx, tif in enumerate(src):
                TifCfg = namedtuple("TifCfg", tif)(**tif)
                dsspathname = f"/{grid_type_name}/{_extent_name}/{TifCfg.dss_cpart}/{TifCfg.dss_dpart}/{TifCfg.dss_epart}/{TifCfg.dss_fpart}/"

                try:
                    data_type = dssutil.data_type[TifCfg.dss_datatype]
                    ds = gdal.Open(f"/vsis3_streaming/{TifCfg.bucket}/{TifCfg.key}")

                    # GDAL Warp the Tiff to what we need for DSS
                    warp_ds = gdal.Warp(
                        '',            # empty string => no filename, return a Dataset
                        ds,
                        format='MEM',  # in‐RAM driver
                        outputBounds=_bbox,
                        xRes=cellsize,
                        yRes=cellsize,
                        targetAlignedPixels=True,
                        dstSRS=destination_srs.ExportToWkt(),
                        resampleAlg=gdalconst.GRA_Bilinear,
                        copyMetadata=False,
                    )

                    # Now read your band straight out of memory:
                    band = warp_ds.GetRasterBand(1)
                    nodata = band.GetNoDataValue()
                    data = band.ReadAsArray()
                    # Flip the dataset up/down because tif and dss have different origins
                    data = numpy.flipud(data)
                    DSS_UNDEFINED_VALUE = -3.4028234663852886e+38
                    data[data == nodata] = numpy.nan # Replace nodata with NaN for processing
                    # GeoTransforma and lower X Y
                    xsize = warp_ds.RasterXSize
                    ysize = warp_ds.RasterYSize
                    adfGeoTransform = warp_ds.GetGeoTransform()
                    llx = int(adfGeoTransform[0] / adfGeoTransform[1])
                    lly = int(
                        (adfGeoTransform[5] * ysize + adfGeoTransform[3])
                        / adfGeoTransform[1]
                    )

                    gd = GriddedData.create(
                        path=dsspathname,
                        type=grid_type,
                        dataType=data_type,
                        lowerLeftCellX=llx,
                        lowerLeftCellY=lly,
                        numberOfCellsX=xsize,
                        numberOfCellsY=ysize,
                        srsName=grid_type_name,
                        srsDefinitionType=1,
                        srsDefinition=srs_definition,
                        dataUnits=TifCfg.dss_unit,
                        dataSource="INTERNAL",
                        timeZoneID=tz_name,
                        timeZoneRawOffset=tz_offset,
                        isInterval=is_interval,
                        isTimeStamped=1,
                        cellSize=cellsize,
                        xCoordOfGridCellZero=0.0,
                        yCoordOfGridCellZero=0.0,
                        nullValue=DSS_UNDEFINED_VALUE,
                        data=data,
                    )

                    # Call HecDss.put() in different process space to release memory after each iteration
                    t = Timer(name="accumuluated", logger=None)
                    t.start()
                    result = dss.put(gd)
                    elapsed_time = t.stop()
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f'DSS put Processed "{TifCfg.key}" in {elapsed_time:.4f} seconds'
                        )
                    if result != 0:
                        logger.info(
                            f'HEC-DSS-PY write record failed for "{TifCfg.key}": {result}'
                        )

                    _progress = int(((idx + 1) / gridcount) * 100)
                    # Update progress at predefined interval
                    if idx % PACKAGER_UPDATE_INTERVAL == 0 or idx == gridcount - 1:
                        update_status(
                            id=id, status_id=PACKAGE_STATUS["INITIATED"], progress=_progress
                        )
                        if _progress % PACKAGER_UPDATE_INTERVAL == 0:
                            logger.info(f'Download ID "{id}" progress: {_progress}%')

                except (RuntimeError, Exception):
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback_details = {
                        "filename": Path(exc_traceback.tb_frame.f_code.co_filename).name,
                        "line number": exc_traceback.tb_lineno,
                        "method": exc_traceback.tb_frame.f_code.co_name,
                        "type": exc_type.__name__,
                        "message": exc_value,
                    }
                    logger.error(traceback_details)

                    continue

                finally:
                    data = None
                    warp_ds = None
                    ds = None

    # If no progress was made for any items in the payload (ex: all tifs could not be projected properly),
    # don't return a dssfilename
    if _progress == 0:
        logger.error(f'No files processed for download ID "{id}"- Progress:{_progress}')
        update_status(id=id, status_id=PACKAGE_STATUS["FAILED"], progress=_progress)
        return None

    total_time = Timer.timers["accumuluated"]
    logger.info(
        f'Total processing time for download ID "{id}" in {total_time:.4f} seconds'
    )

    return dssfilename
