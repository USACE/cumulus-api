"""DSS7 package writer"""

import gc
import json
import logging
import os
import shutil
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

# Configure GDAL for S3 streaming
# Disable all caching - each file is processed exactly once, so caching provides
# no benefit but accumulates memory in GDAL's C memory space over hundreds of files
gdal.SetConfigOption('GDAL_HTTP_MAX_RETRY', '3')
gdal.SetConfigOption('GDAL_HTTP_RETRY_DELAY', '1')
gdal.SetConfigOption('CPL_VSIL_CURL_CHUNK_SIZE', '10485760')  # 10MB chunks
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS', '.tif,.tiff')
gdal.SetConfigOption('VSI_CACHE', 'FALSE')  # Disable VSI cache - prevents memory accumulation
gdal.SetCacheMax(0)  # Disable GDAL block cache - not needed for single-pass processing


def log_storage_status(dssfilename: str, label: str = "") -> dict:
    """
    Log disk usage and DSS file size for debugging storage issues.

    Parameters:
    -----------
    dssfilename : str
        Path to the DSS file
    label : str
        Label for the log message (e.g., "Start", "50%", etc.)

    Returns:
    --------
    dict : Storage status info
    """
    try:
        # Get disk usage for /tmp (or wherever the DSS file is located)
        dss_dir = os.path.dirname(dssfilename) or "/tmp"
        total, used, free = shutil.disk_usage(dss_dir)

        # Get DSS file size if it exists
        dss_size = 0
        if os.path.exists(dssfilename):
            dss_size = os.path.getsize(dssfilename)

        # Calculate percentages
        disk_used_pct = (used / total) * 100 if total > 0 else 0

        status = {
            "disk_total_gb": total / (1024**3),
            "disk_used_gb": used / (1024**3),
            "disk_free_gb": free / (1024**3),
            "disk_used_pct": disk_used_pct,
            "dss_size_mb": dss_size / (1024**2),
        }

        logger.info(
            f"[Storage {label}] "
            f"Disk: {status['disk_used_gb']:.2f}GB/{status['disk_total_gb']:.2f}GB "
            f"({status['disk_used_pct']:.1f}% used, {status['disk_free_gb']:.2f}GB free) | "
            f"DSS file: {status['dss_size_mb']:.1f}MB"
        )

        # Warn if disk space is getting low
        if status['disk_free_gb'] < 1.0:
            logger.warning(f"LOW DISK SPACE WARNING: Only {status['disk_free_gb']:.2f}GB free!")

        return status
    except Exception as e:
        logger.warning(f"Could not get storage status: {e}")
        return {}


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
    Uses 4x CPU cores since this is an I/O-bound workload (S3 streaming reads).

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

        # Use 4x CPU count for I/O-bound operations (S3 reads + processing)
        optimal_workers = cpu_count * 4
        logger.info(f"Using {optimal_workers} worker threads (4x CPU count)")
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
    import time

    (idx, tif, _bbox, cellsize, destination_srs, grid_type, grid_type_name,
     srs_definition, _extent_name, tz_name, tz_offset, is_interval) = args

    timings = {}  # Track timing for each step
    step_start = time.time()

    try:
        TifCfg = namedtuple("TifCfg", tif)(**tif)
        s3_path = f"/vsis3_streaming/{TifCfg.bucket}/{TifCfg.key}"

        # Step 1: Open TIFF with GDAL
        logger.debug(f"[{idx}] GDAL_OPEN: Starting for {TifCfg.key}")
        t0 = time.time()
        ds = gdal.Open(s3_path)
        timings['gdal_open'] = time.time() - t0
        logger.debug(f"[{idx}] GDAL_OPEN: Completed in {timings['gdal_open']:.3f}s")

        if ds is None:
            logger.error(f"[{idx}] GDAL_OPEN: FAILED - ds is None for {TifCfg.key}")
            return {
                'success': False,
                'index': idx,
                'error': f"Failed to open {TifCfg.key}"
            }

        # Step 2: GDAL Warp
        logger.debug(f"[{idx}] GDAL_WARP: Starting")
        t0 = time.time()
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
        timings['gdal_warp'] = time.time() - t0
        logger.debug(f"[{idx}] GDAL_WARP: Completed in {timings['gdal_warp']:.3f}s")

        if warp_ds is None:
            logger.error(f"[{idx}] GDAL_WARP: FAILED - warp_ds is None for {TifCfg.key}")
            ds = None
            return {
                'success': False,
                'index': idx,
                'error': f"Failed to warp {TifCfg.key}"
            }

        # Step 3: Read array from band
        logger.debug(f"[{idx}] READ_ARRAY: Starting")
        t0 = time.time()
        band = warp_ds.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        data = band.ReadAsArray().astype(numpy.float32, copy=False)
        timings['read_array'] = time.time() - t0
        logger.debug(f"[{idx}] READ_ARRAY: Completed in {timings['read_array']:.3f}s, shape={data.shape}")

        # Step 4: Data transformations
        logger.debug(f"[{idx}] DATA_TRANSFORM: Starting")
        t0 = time.time()
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
        timings['data_transform'] = time.time() - t0
        logger.debug(f"[{idx}] DATA_TRANSFORM: Completed in {timings['data_transform']:.3f}s")

        # Step 5: Clean up GDAL objects
        logger.debug(f"[{idx}] GDAL_CLEANUP: Starting")
        t0 = time.time()
        band = None
        warp_ds = None
        ds = None
        timings['gdal_cleanup'] = time.time() - t0
        logger.debug(f"[{idx}] GDAL_CLEANUP: Completed in {timings['gdal_cleanup']:.3f}s")

        # Step 6: Prepare data for DSS
        logger.debug(f"[{idx}] DSS_PREP: Starting")
        t0 = time.time()
        DSS_UNDEFINED_VALUE = -3.4028234663852886e+38
        data[numpy.isnan(data)] = DSS_UNDEFINED_VALUE

        # Create DSS pathname
        data_type = dssutil.data_type[TifCfg.dss_datatype]
        dsspathname = f"/{grid_type_name}/{_extent_name}/{TifCfg.dss_cpart}/{TifCfg.dss_dpart}/{TifCfg.dss_epart}/{TifCfg.dss_fpart}/"
        timings['dss_prep'] = time.time() - t0
        logger.debug(f"[{idx}] DSS_PREP: Completed in {timings['dss_prep']:.3f}s")

        # Step 7: Create GriddedData object
        logger.debug(f"[{idx}] GRIDDATA_CREATE: Starting")
        t0 = time.time()
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
        timings['griddata_create'] = time.time() - t0
        logger.debug(f"[{idx}] GRIDDATA_CREATE: Completed in {timings['griddata_create']:.3f}s")

        gd.data = None  # Free data reference in GriddedData

        # Step 8: Compress the grid data
        logger.debug(f"[{idx}] COMPRESS: Starting")
        t0 = time.time()
        # data is already float32, no need for .astype() which creates an unnecessary copy
        # Ensure C-contiguous memory layout for efficient tobytes()
        if not data.flags['C_CONTIGUOUS']:
            data = numpy.ascontiguousarray(data)
        raw_bytes = data.tobytes()
        compressed_data = zlib.compress(raw_bytes)
        del raw_bytes  # Explicitly free the raw bytes buffer
        compressed_size = len(compressed_data)
        timings['compress'] = time.time() - t0
        logger.debug(f"[{idx}] COMPRESS: Completed in {timings['compress']:.3f}s, size={compressed_size} bytes")

        # Step 9: Clean up data array to free memory before returning
        del data

        total_time = time.time() - step_start
        logger.debug(f"[{idx}] WORKER_COMPLETE: Total={total_time:.3f}s, Timings={timings}")

        return {
            'success': True,
            'index': idx,
            'tif_key': TifCfg.key,
            'gd': gd,
            'compressed_data': compressed_data,
            'compressed_size': compressed_size,
            'timings': timings
        }

    except Exception as e:
        total_time = time.time() - step_start
        logger.error(f"[{idx}] WORKER_ERROR: Error after {total_time:.3f}s processing TIFF: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'index': idx,
            'error': str(e),
            'timings': timings
        }


def process_tiffs_with_bounded_queue(src, _bbox, cellsize, destination_srs, dss,
                                     grid_type, grid_type_name, srs_definition,
                                     _extent_name, tz_name, tz_offset, is_interval,
                                     id, gridcount, dssfilename, max_workers=None):
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
    import time

    # Shared state for watchdog
    watchdog_state = {
        'phase': 'INIT',
        'last_activity': time.time(),
        'processed_count': 0,
        'current_file': None,
        'current_step': None,
        'stop_watchdog': False,
    }

    def watchdog():
        """Periodically log state to help diagnose hangs."""
        import time
        while not watchdog_state['stop_watchdog']:
            time.sleep(30)  # Log every 30 seconds
            if watchdog_state['stop_watchdog']:
                break

            idle_time = time.time() - watchdog_state['last_activity']
            mem = psutil.virtual_memory()
            mem_used_gb = mem.used / (1024**3)
            mem_total_gb = mem.total / (1024**3)
            mem_pct = mem.percent

            logger.info(
                f"[WATCHDOG] Phase: {watchdog_state['phase']} | "
                f"Processed: {watchdog_state['processed_count']}/{gridcount} | "
                f"Current: {watchdog_state['current_file']} | "
                f"Step: {watchdog_state['current_step']} | "
                f"Idle: {idle_time:.1f}s | "
                f"Memory: {mem_used_gb:.1f}GB/{mem_total_gb:.1f}GB ({mem_pct:.1f}%)"
            )

            if idle_time > 120:  # Warn if no activity for 2 minutes
                logger.warning(f"[WATCHDOG] No activity for {idle_time:.1f}s - possible hang!")
                # Log thread info
                import sys
                logger.warning(f"[WATCHDOG] Active threads: {threading.active_count()}")
                for t in threading.enumerate():
                    logger.warning(f"[WATCHDOG]   Thread: {t.name} (alive={t.is_alive()}, daemon={t.daemon})")

    # Start watchdog thread
    watchdog_thread = threading.Thread(target=watchdog, name="Watchdog", daemon=True)
    watchdog_thread.start()
    logger.info("[MAIN] Watchdog thread started")

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
            import time
            logger.info(f"[PRODUCER] Starting with {max_workers} workers for {len(src)} files")
            producer_start = time.time()
            completed_count = 0

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Prepare arguments for parallel processing (includes all GriddedData parameters)
                tasks = [
                    (idx, tif, _bbox, cellsize, destination_srs, grid_type, grid_type_name,
                     srs_definition, _extent_name, tz_name, tz_offset, is_interval)
                    for idx, tif in enumerate(src)
                ]

                # Submit all tasks and process as they complete
                logger.info(f"[PRODUCER] Submitting {len(tasks)} tasks to executor")
                future_to_idx = {
                    executor.submit(process_single_tiff_gdal, task): task[0]
                    for task in tasks
                }
                logger.info(f"[PRODUCER] All tasks submitted, waiting for completion")

                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        logger.debug(f"[PRODUCER] Waiting for result from worker {idx}")
                        t0 = time.time()
                        result = future.result(timeout=300)  # 5 minute timeout per file
                        wait_time = time.time() - t0
                        logger.debug(f"[PRODUCER] Got result from worker {idx} in {wait_time:.3f}s")

                        logger.debug(f"[PRODUCER] Putting result {idx} into queue (queue size: {result_queue.qsize()}/{queue_size})")
                        t0 = time.time()
                        result_queue.put(result)
                        put_time = time.time() - t0
                        logger.debug(f"[PRODUCER] Put result {idx} into queue in {put_time:.3f}s")

                        completed_count += 1
                        if completed_count % 50 == 0:
                            elapsed = time.time() - producer_start
                            logger.info(f"[PRODUCER] Progress: {completed_count}/{len(src)} tasks completed in {elapsed:.1f}s")

                    except Exception as e:
                        logger.error(f"[PRODUCER] Worker timeout or error for file {idx}: {e}")
                        result_queue.put({
                            'success': False,
                            'index': idx,
                            'error': f'Worker timeout or exception: {str(e)}'
                        })

            # Signal completion
            producer_elapsed = time.time() - producer_start
            logger.info(f"[PRODUCER] All workers completed in {producer_elapsed:.1f}s, sending completion signal")
            result_queue.put(None)
            logger.info(f"[PRODUCER] Thread exiting")

        # Start producer thread
        logger.info("[CONSUMER] Starting producer thread")
        producer_thread = threading.Thread(target=producer)
        producer_thread.start()

        # Consumer (main thread): write pre-created, precompressed GriddedData objects to DSS
        logger.info(f"[CONSUMER] Processing {len(src)} files with parallel compression and precompressed writes (queue size: {queue_size}, workers: {max_workers})")

        import time
        consumer_start = time.time()
        last_activity = time.time()
        watchdog_state['phase'] = 'CONSUMING'

        while True:
            try:
                watchdog_state['current_step'] = 'QUEUE_WAIT'
                watchdog_state['last_activity'] = time.time()
                queue_wait_start = time.time()
                logger.debug(f"[CONSUMER] Waiting for result from queue (processed: {processed_count}, queue size: ~{result_queue.qsize()})")
                result = result_queue.get(timeout=300)  # 5 minute timeout
                queue_wait_time = time.time() - queue_wait_start
                last_activity = time.time()
                watchdog_state['last_activity'] = last_activity

                if queue_wait_time > 10:
                    logger.warning(f"[CONSUMER] Long queue wait: {queue_wait_time:.1f}s")
                else:
                    logger.debug(f"[CONSUMER] Got result from queue in {queue_wait_time:.3f}s")

                # None signals completion
                if result is None:
                    logger.info("[CONSUMER] Received completion signal from producer")
                    break

                result_idx = result.get('index', 'unknown')
                watchdog_state['current_file'] = f"idx={result_idx}"

                if result['success']:
                    try:
                        # Extract pre-created GriddedData and compressed data from worker
                        gd = result['gd']
                        compressed_data = result['compressed_data']
                        compressed_size = result['compressed_size']
                        tif_key = result['tif_key']
                        watchdog_state['current_file'] = tif_key

                        logger.debug(f"[CONSUMER] [{result_idx}] Starting DSS write for {tif_key}")
                        watchdog_state['current_step'] = 'DSS_WRITE'

                        # Write precompressed data to DSS with timeout protection
                        t = Timer(name="accumuluated", logger=None)
                        t.start()

                        # Wrap DSS write in thread with timeout (DSS operations can hang)
                        logger.debug(f"[CONSUMER] [{result_idx}] Creating write executor")
                        write_executor_start = time.time()
                        with ThreadPoolExecutor(max_workers=1) as write_executor:
                            logger.debug(f"[CONSUMER] [{result_idx}] Submitting writePrecompressedGrid")
                            write_future = write_executor.submit(
                                dss.writePrecompressedGrid, gd, compressed_data, compressed_size
                            )
                            try:
                                logger.debug(f"[CONSUMER] [{result_idx}] Waiting for DSS write result (timeout=300s)")
                                dss_write_start = time.time()
                                dss_result = write_future.result(timeout=300)  # 5 minute timeout for DSS write
                                dss_write_time = time.time() - dss_write_start
                                elapsed_time = t.stop()

                                if dss_write_time > 5:
                                    logger.warning(f"[CONSUMER] [{result_idx}] Slow DSS write: {dss_write_time:.2f}s for {tif_key}")
                                else:
                                    logger.debug(f"[CONSUMER] [{result_idx}] DSS write completed in {dss_write_time:.3f}s")

                                if dss_result != 0:
                                    logger.warning(f'[CONSUMER] [{result_idx}] HEC-DSS-PY write record failed for "{tif_key}": {dss_result}')
                                elif logger.isEnabledFor(logging.DEBUG):
                                    logger.debug(f'[CONSUMER] [{result_idx}] DSS writePrecompressedGrid processed "{tif_key}" in {elapsed_time:.4f}s')
                            except Exception as write_error:
                                elapsed_time = t.stop()
                                logger.error(f'[CONSUMER] [{result_idx}] DSS write timeout or error for "{tif_key}" after {elapsed_time:.2f}s: {write_error}')
                                import traceback
                                logger.error(traceback.format_exc())
                                # Continue processing remaining files
                                gd = None
                                compressed_data = None
                                continue

                        write_executor_time = time.time() - write_executor_start
                        logger.debug(f"[CONSUMER] [{result_idx}] Write executor completed in {write_executor_time:.3f}s")

                        processed_count += 1
                        watchdog_state['processed_count'] = processed_count
                        watchdog_state['last_activity'] = time.time()

                        # Update progress
                        _progress = int((processed_count / gridcount) * 100)
                        if processed_count % PACKAGER_UPDATE_INTERVAL == 0 or processed_count == gridcount:
                            watchdog_state['current_step'] = 'STATUS_UPDATE'
                            logger.debug(f"[CONSUMER] [{result_idx}] Updating status: {_progress}%")
                            status_update_start = time.time()
                            update_status(id=id, status_id=PACKAGE_STATUS["INITIATED"], progress=_progress)
                            status_update_time = time.time() - status_update_start
                            watchdog_state['last_activity'] = time.time()
                            if status_update_time > 2:
                                logger.warning(f"[CONSUMER] [{result_idx}] Slow status update: {status_update_time:.2f}s")

                            if _progress % PACKAGER_UPDATE_INTERVAL == 0:
                                consumer_elapsed = time.time() - consumer_start
                                logger.info(f'[CONSUMER] Download ID "{id}" progress: {_progress}% (queue: ~{result_queue.qsize()}/{queue_size}, elapsed: {consumer_elapsed:.1f}s)')
                                # Log storage status every 10% progress
                                if _progress % 10 == 0:
                                    log_storage_status(dssfilename, f"{_progress}%")

                        # Explicitly free memory after writing to DSS
                        compressed_data = None
                        gd = None

                        # Periodic garbage collection to return memory to OS
                        # Important for large grids (like APRFC) that use significant memory per iteration
                        if processed_count % 50 == 0:
                            gc.collect()

                        watchdog_state['current_step'] = 'COMPLETE'
                        logger.debug(f"[CONSUMER] [{result_idx}] Processing complete")

                    except Exception as e:
                        logger.error(f"[CONSUMER] Error writing to DSS for file {result_idx}: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        continue
                else:
                    logger.error(f"[CONSUMER] Error processing file {result_idx}: {result.get('error', 'Unknown error')}")

            except Empty:
                idle_time = time.time() - last_activity
                logger.error(f"[CONSUMER] TIMEOUT waiting for results from queue after {idle_time:.1f}s idle")
                logger.error(f"[CONSUMER] Producer thread alive: {producer_thread.is_alive()}")
                logger.error(f"[CONSUMER] Queue size: {result_queue.qsize()}")
                break

        watchdog_state['phase'] = 'JOINING'
        logger.info(f"[CONSUMER] Waiting for producer thread to join")
        join_start = time.time()
        producer_thread.join(timeout=60)
        join_time = time.time() - join_start
        if producer_thread.is_alive():
            logger.error(f"[CONSUMER] Producer thread did not terminate after {join_time:.1f}s")
        else:
            logger.info(f"[CONSUMER] Producer thread joined in {join_time:.3f}s")

        # Stop watchdog
        watchdog_state['stop_watchdog'] = True
        watchdog_state['phase'] = 'COMPLETE'
        logger.info("[MAIN] Stopping watchdog thread")

        # Log final storage status
        log_storage_status(dssfilename, "END")

        total_elapsed = time.time() - consumer_start
        logger.info(f"Parallel GDAL with compression: Successfully processed {processed_count}/{len(src)} files in {total_elapsed:.1f}s")
        return processed_count

    except Exception as e:
        watchdog_state['stop_watchdog'] = True
        watchdog_state['phase'] = 'ERROR'
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
        # Log initial storage status
        log_storage_status(dssfilename, "START")

        # Use parallel GDAL processing with compression and precompressed writes for multiple files
        if len(src) > 1:
            logger.info("Using parallel GDAL processing with compression and precompressed writes")
            processed_count = process_tiffs_with_bounded_queue(
                src, _bbox, cellsize, destination_srs, dss,
                grid_type, grid_type_name, srs_definition,
                _extent_name, tz_name, tz_offset, is_interval,
                id, gridcount, dssfilename
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

    # Log final storage status before returning
    log_storage_status(dssfilename, "COMPLETE")

    logger.info(
        f'Total processing time for download ID "{id}" in {total_time:.4f} seconds'
    )

    return dssfilename
