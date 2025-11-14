"""Daily batch processor for BasinComps with basin-specific config and rolling totals"""
import logging
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

from basincomps_scheduler.utils.database import DatabaseClient
from basincomps_scheduler.utils.s3_client import S3Client
from basincomps_scheduler.basincomps_runner import BasinCompsRunner
from basincomps_scheduler.basincomps_runner_gdal import BasinCompsRunnerGDAL
from basincomps_scheduler.result_parser import parse_basincomps_csv
from basincomps_scheduler.rolling_totals import calculate_rolling_totals

logger = logging.getLogger(__name__)


class BasinCompsBatchProcessor:
    """Processes daily basin averages using BasinComps"""

    def __init__(self):
        self.db = DatabaseClient()
        self.s3 = S3Client()
        self.runner = BasinCompsRunnerGDAL()

        # Configuration
        self.output_format = os.getenv('BASINCOMPS_OUTPUT_FORMAT', 'csv')
        self.use_metric = os.getenv('BASINCOMPS_USE_METRIC', 'true').lower() == 'true'
        self.lookback_hours = int(os.getenv('BASINCOMPS_LOOKBACK_HOURS', '24'))
        self.lookahead_hours = int(os.getenv('BASINCOMPS_LOOKAHEAD_HOURS', '168'))  # 7 days for forecasts

    def run(self):
        """Execute daily batch job"""
        run_date = datetime.now()
        start_time = datetime.now()
        batch_id = None

        try:
            # Get shapefile configurations from database
            shapefile_configs = self.db.get_shapefile_configs()

            if len(shapefile_configs) == 0:
                logger.warning("No shapefile configurations found. Please configure shapefiles via API.")
                return

            logger.info(f"Found {len(shapefile_configs)} shapefile configuration(s)")

            # Collect all unique product slugs needed across all shapefiles
            all_product_slugs = set()
            for config in shapefile_configs:
                all_product_slugs.update(config['product_slugs'])

            all_product_slugs = list(all_product_slugs)
            logger.info(f"Processing products: {', '.join(all_product_slugs)}")

            # Check for existing triggered batch run or create new one
            batch_id = self.db.get_or_create_batch_run(
                run_date=run_date,
                start_time=start_time,
                product_slugs=all_product_slugs
            )

            logger.info(f"Batch run {batch_id} started")

            # Calculate time window (includes both past for observed and future for forecasts)
            now = datetime.now()
            start_time_data = now - timedelta(hours=self.lookback_hours)
            end_time_data = now + timedelta(hours=self.lookahead_hours)

            logger.info(f"Processing data from {start_time_data} to {end_time_data}")
            logger.info(f"  Lookback: {self.lookback_hours}h (for observed products)")
            logger.info(f"  Lookahead: {self.lookahead_hours}h (for forecast products)")

            # Get product files for the time window
            product_files = self.db.get_product_files(
                product_slugs=all_product_slugs,
                start_time=start_time_data,
                end_time=end_time_data
            )

            if len(product_files) == 0:
                logger.warning("No product files found for processing")
                self.db.update_batch_run(
                    batch_id=batch_id,
                    status='SUCCESS',
                    file_count=0,
                    result_count=0,
                    end_time=datetime.now()
                )
                return

            logger.info(f"Found {len(product_files)} product files to process")

            # Group files by product
            files_by_product = self._group_files_by_product(product_files)

            all_results = []

            # Process each shapefile configuration
            for config in shapefile_configs:
                config_name = config['config_name']
                shapefile_path = config['shapefile_path']
                config_products = config['product_slugs']

                logger.info(f"Processing shapefile config: {config_name}")
                logger.info(f"  Shapefile: {shapefile_path}")
                logger.info(f"  Products: {', '.join(config_products)}")

                # Process each product for this shapefile
                for product_slug in config_products:
                    if product_slug not in files_by_product:
                        logger.warning(f"No files found for product {product_slug}, skipping")
                        continue

                    files = files_by_product[product_slug]
                    logger.info(f"  Processing {product_slug} ({len(files)} files)")

                    # Determine if this is a forecast product (has last_forecast_version)
                    is_forecast = files[0].get('last_forecast_version') is not None if files else False

                    results = self._process_shapefile_product(
                        config_name=config_name,
                        shapefile_path=shapefile_path,
                        product_slug=product_slug,
                        product_files=files,
                        run_date=run_date,
                        is_forecast=is_forecast
                    )

                    all_results.extend(results)

            # Insert hourly results into database
            logger.info(f"Inserting {len(all_results)} hourly results into database")
            self.db.insert_results(all_results)

            # Calculate rolling totals (1-7 days)
            logger.info("Calculating rolling precipitation totals (1-7 days)")
            rolling_totals = calculate_rolling_totals(all_results, run_date)

            # Insert rolling totals
            logger.info(f"Inserting {len(rolling_totals)} rolling totals into database")
            self.db.insert_rolling_totals(rolling_totals)

            # Update batch run as complete
            self.db.update_batch_run(
                batch_id=batch_id,
                status='SUCCESS',
                file_count=len(product_files),
                result_count=len(all_results),
                end_time=datetime.now()
            )

            logger.info(f"Batch run {batch_id} completed successfully")

        except Exception as e:
            logger.error(f"Batch run failed: {e}", exc_info=True)

            if batch_id:
                self.db.update_batch_run(
                    batch_id=batch_id,
                    status='FAILED',
                    error_message=str(e),
                    end_time=datetime.now()
                )

            raise

    def _group_files_by_product(
        self,
        product_files: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group product files by product slug"""
        grouped = {}
        for pfile in product_files:
            slug = pfile['product_slug']
            if slug not in grouped:
                grouped[slug] = []
            grouped[slug].append(pfile)
        return grouped

    def _process_shapefile_product(
        self,
        config_name: str,
        shapefile_path: str,
        product_slug: str,
        product_files: List[Dict[str, Any]],
        run_date: datetime,
        is_forecast: bool = False
    ) -> List[Dict[str, Any]]:
        """Process a single product for a specific shapefile with BasinComps"""

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Download files from S3 and preserve metadata from database
            tin_dir = tmppath / 'tins'
            tin_dir.mkdir()

            logger.info(f"Downloading {len(product_files)} files from S3...")

            # Map filename -> datetime from productfile table
            # This ensures we use the database as source of truth, not filename parsing
            file_metadata = {}

            # Get temporal_duration from product table (same for all files from this product)
            temporal_duration = product_files[0].get('temporal_duration') if product_files else None

            for pfile in product_files:
                local_file = tin_dir / Path(pfile['key']).name

                # Download file
                self.s3.download_file(
                    bucket=pfile['bucket'],
                    key=pfile['key'],
                    local_path=local_file
                )

                # Store datetime from database for this file
                file_metadata[local_file.name] = pfile['datetime']

            # Prepare output directory
            output_dir = tmppath / 'output'
            output_dir.mkdir()

            # Run BasinComps
            logger.info(f"Running BasinComps for {product_slug} with {shapefile_path}...")

            # Validate shapefile exists
            shapefile = Path(shapefile_path)
            if not shapefile.exists():
                raise ValueError(f"Shapefile not found: {shapefile_path}")

            # Get first and last file times for time range
            times = [pfile['datetime'] for pfile in product_files]
            start_time = min(times)
            end_time = max(times)

            result = self.runner.run_basincomps(
                tin_dir=tin_dir,
                basin_file=shapefile,
                output_dir=output_dir,
                start_time=start_time,
                end_time=end_time,
                output_format=self.output_format,
                use_metric=self.use_metric,
                file_metadata=file_metadata,
                temporal_duration=temporal_duration
            )

            # Parse results
            logger.info(f"Parsing BasinComps output...")

            csv_results = []
            if result['text_output']:
                csv_results = parse_basincomps_csv(
                    csv_path=Path(result['text_output']),
                    product_slug=product_slug,
                    run_date=run_date,
                    is_forecast=is_forecast
                )

                # Upload CSV to S3 (organized by config and product, using date portion for folder)
                csv_key = f"cumulus/basincomps-daily/{run_date.strftime('%Y-%m-%d')}/{config_name}/{product_slug}.csv"
                self.s3.upload_file(
                    local_path=result['text_output'],
                    bucket=os.getenv('S3_BUCKET'),
                    key=csv_key
                )
                logger.info(f"Uploaded results to s3://{os.getenv('S3_BUCKET')}/{csv_key}")

            if result['dss_output']:
                # Upload DSS to S3 (organized by config and product, using date portion for folder)
                dss_key = f"cumulus/basincomps-daily/{run_date.strftime('%Y-%m-%d')}/{config_name}/{product_slug}.dss"
                self.s3.upload_file(
                    local_path=result['dss_output'],
                    bucket=os.getenv('S3_BUCKET'),
                    key=dss_key
                )
                logger.info(f"Uploaded DSS to s3://{os.getenv('S3_BUCKET')}/{dss_key}")

            return csv_results
