"""GDAL-based BasinComps alternative using Python raster masking

This runner automatically handles projection mismatches between shapefiles and rasters.
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import glob

import numpy as np
import rasterio
import geopandas as gpd
from rasterstats import zonal_stats

logger = logging.getLogger(__name__)

logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('fiona').setLevel(logging.WARNING)
logging.getLogger('rasterio').setLevel(logging.WARNING)


class BasinCompsRunnerGDAL:
    """
    GDAL-based basin averaging using Python

    Advantages over HEC-MetVue BasinComps:
    - Handles projection mismatches automatically (reprojects shapefile to raster CRS)
    - Pure Python/GDAL - no external executables needed
    - Better error handling and logging
    - May be faster for large datasets
    """

    def run_basincomps(
        self,
        tin_dir: Path,
        basin_file: Path,
        output_dir: Path,
        start_time: datetime,
        end_time: datetime,
        output_format: str = 'csv',
        use_metric: bool = True,
        file_metadata: Dict[str, datetime] = None,
        temporal_duration: int = None
    ) -> Dict[str, Any]:
        """
        Run basin averaging using GDAL

        Args:
            tin_dir: Directory containing TIFF files
            basin_file: Shapefile with basin polygons
            output_dir: Output directory
            start_time: Start time (used for filtering if needed)
            end_time: End time (used for filtering if needed)
            output_format: Output format (csv only for now)
            use_metric: Use metric units (True = mm, False = inches)
            file_metadata: Dict mapping filename -> datetime from productfile table
            temporal_duration: Accumulation interval in seconds from product table

        Returns:
            Dictionary with output paths and processing info
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get all TIFF files
        tif_files = sorted(glob.glob(str(tin_dir / '*.tif')))
        if not tif_files:
            raise ValueError(f"No TIF files found in {tin_dir}")

        logger.info(f"GDAL Runner: Processing {len(tif_files)} TIFF files")

        # Load shapefile
        logger.info(f"GDAL Runner: Loading shapefile: {basin_file}")
        try:
            basins = gpd.read_file(basin_file)
            logger.info(f"GDAL Runner: Loaded {len(basins)} basins")
            logger.info(f"GDAL Runner: Shapefile CRS: {basins.crs}")
        except Exception as e:
            raise RuntimeError(f"Failed to load shapefile {basin_file}: {e}")

        # Get basin identifier column (try common names)
        basin_id_col = self._find_basin_id_column(basins)
        logger.info(f"GDAL Runner: Using basin ID column: {basin_id_col}")

        # Determine target CRS by checking first TIFF
        # All TIFFs in a batch typically have the same projection
        with rasterio.open(tif_files[0]) as src:
            target_crs = src.crs
            logger.info(f"GDAL Runner: Target CRS from TIFFs: {target_crs}")

        # Reproject basins once (not per-TIFF)
        if basins.crs != target_crs:
            logger.info(f"GDAL Runner: Reprojecting basins from {basins.crs} to {target_crs}")
            basins_proj = basins.to_crs(target_crs)
        else:
            logger.info(f"GDAL Runner: Basins already in target CRS, no reprojection needed")
            basins_proj = basins

        # Process each TIFF file
        results = []
        processed_count = 0
        error_count = 0

        for tif_file in tif_files:
            try:
                result = self._process_tiff(
                    tif_file=Path(tif_file),
                    basins=basins_proj,  # Use pre-reprojected basins
                    basin_id_col=basin_id_col,
                    use_metric=use_metric,
                    skip_reprojection=True,  # Already reprojected
                    file_metadata=file_metadata,
                    temporal_duration=temporal_duration
                )
                results.extend(result)
                processed_count += 1
            except Exception as e:
                logger.error(f"GDAL Runner: Failed to process {tif_file}: {e}", exc_info=True)
                error_count += 1
                continue

        logger.info(f"GDAL Runner: Processed {processed_count}/{len(tif_files)} TIFFs successfully")
        logger.info(f"GDAL Runner: Generated {len(results)} basin-time records")

        if error_count > 0:
            logger.warning(f"GDAL Runner: {error_count} files failed to process")

        # Write CSV output
        text_output = None
        if output_format == 'csv' and results:
            text_output = output_dir / 'basincomps_output.csv'
            self._write_csv(results, text_output)
            logger.info(f"GDAL Runner: Wrote CSV output: {text_output}")

        return {
            'text_output': str(text_output) if text_output and text_output.exists() else None,
            'dss_output': None,  # DSS not implemented in GDAL version
            'stdout': f"GDAL: Processed {processed_count} TIFFs, generated {len(results)} records",
            'stderr': f"GDAL: {error_count} errors" if error_count > 0 else ''
        }

    def _find_basin_id_column(self, basins: gpd.GeoDataFrame) -> str:
        """Find the basin identifier column in the shapefile"""
        # Try common column names
        for col in ['NAME', 'name', 'Name', 'Id', 'ID', 'id', 'BASIN', 'basin', 'Basin', 'FID', 'OBJECTID']:
            if col in basins.columns:
                return col

        # Use first non-geometry column
        for col in basins.columns:
            if col != 'geometry':
                logger.warning(f"Using first non-geometry column as basin ID: {col}")
                return col

        # Last resort: create index-based IDs
        basins['basin_id'] = basins.index.astype(str)
        logger.warning(f"No suitable basin ID column found, using index")
        return 'basin_id'

    def _process_tiff(
        self,
        tif_file: Path,
        basins: gpd.GeoDataFrame,
        basin_id_col: str,
        use_metric: bool,
        skip_reprojection: bool = False,
        file_metadata: Dict[str, datetime] = None,
        temporal_duration: int = None
    ) -> List[Dict[str, Any]]:
        """
        Process a single TIFF file against all basins using optimized zonal statistics

        This processes ALL basins at once, which is much faster than looping.

        Args:
            skip_reprojection: If True, assumes basins are already in correct CRS
            file_metadata: Dict mapping filename -> datetime from database
            temporal_duration: Accumulation interval in seconds from product table

        Returns list of results, one per basin
        """
        results = []

        # Get timestamp from database metadata (required)
        if not file_metadata or tif_file.name not in file_metadata:
            raise ValueError(f"Missing datetime metadata for {tif_file.name}")

        timestamp = file_metadata[tif_file.name]
        logger.debug(f"GDAL Runner: Using datetime from database for {tif_file.name}: {timestamp}")

        # Get interval from database temporal_duration (required)
        if temporal_duration is None:
            raise ValueError(f"Missing temporal_duration for {tif_file.name}")

        # Convert seconds to hours
        interval_hours = temporal_duration / 3600
        interval = f"{int(interval_hours)}Hour"
        logger.debug(f"GDAL Runner: Using temporal_duration from database: {temporal_duration}s = {interval}")

        # Use rasterstats to compute zonal stats for all basins at once
        # This is MUCH faster than looping and masking individually
        try:
            # Read nodata value from TIFF metadata
            with rasterio.open(str(tif_file)) as src:
                tif_nodata = src.nodata
                logger.debug(f"GDAL Runner: TIFF nodata value for {tif_file.name}: {tif_nodata}")

            stats = zonal_stats(
                basins.geometry,
                str(tif_file),
                stats=['mean'],
                nodata=tif_nodata if tif_nodata is not None else np.nan,
                all_touched=True
            )

            # Process results for each basin
            for idx, (basin, stat) in enumerate(zip(basins.itertuples(), stats)):
                try:
                    basin_id = str(getattr(basin, basin_id_col))

                    # Check if we got valid stats
                    if stat is None or stat['mean'] is None or np.isnan(stat['mean']):
                        logger.debug(f"GDAL Runner: No valid data for basin {basin_id} in {tif_file.name}")
                        continue

                    mean_value = stat['mean']

                    # Convert units if needed (kg/m² = mm for water)
                    if use_metric:
                        value = float(mean_value)  # Already in mm
                        units = 'mm'
                    else:
                        value = float(mean_value / 25.4)  # Convert to inches
                        units = 'in'

                    results.append({
                        'Basin': basin_id,
                        'Date': timestamp.strftime('%d%b%Y').upper(),
                        'Time': timestamp.strftime('%H%M'),
                        'Interval': interval,
                        'Value': value,
                        'Units': units
                    })

                except Exception as e:
                    logger.error(f"GDAL Runner: Failed to process basin stats: {e}")
                    continue

        except Exception as e:
            logger.error(f"GDAL Runner: Failed to compute zonal stats for {tif_file.name}: {e}", exc_info=True)
            raise

        return results

    def _write_csv(self, results: List[Dict[str, Any]], output_file: Path):
        """Write results to CSV file matching BasinComps format"""
        import csv

        with open(output_file, 'w', newline='') as f:
            if not results:
                # Write header only
                writer = csv.DictWriter(f, fieldnames=['Basin', 'Date', 'Time', 'Interval', 'Value', 'Units'])
                writer.writeheader()
                return

            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
