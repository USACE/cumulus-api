"""Database operations"""
import logging
import os
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from typing import List, Dict, Any
from datetime import datetime, date
import uuid

logger = logging.getLogger(__name__)


class DatabaseClient:
    """PostgreSQL database client"""

    def __init__(self):
        self.conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS')
        }

    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.conn_params)

    def get_or_create_batch_run(
        self,
        run_date: datetime,
        start_time: datetime,
        product_slugs: List[str]
    ) -> str:
        """Get existing triggered batch run or create new one"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Get product IDs
                cur.execute(
                    "SELECT id FROM product WHERE slug = ANY(%s)",
                    (product_slugs,)
                )
                product_ids = [str(row[0]) for row in cur.fetchall()]

                # Check for existing TRIGGERED or RUNNING run for today (same calendar day)
                cur.execute(
                    """SELECT id FROM basincomps_batch_run
                       WHERE DATE(run_date) = DATE(%s) AND status IN ('TRIGGERED', 'RUNNING')
                       ORDER BY start_time DESC
                       LIMIT 1""",
                    (run_date,)
                )

                existing = cur.fetchone()

                if existing:
                    # Update existing triggered run with product_ids
                    batch_id = str(existing[0])
                    logger.info(f"Using existing batch run {batch_id}")

                    cur.execute(
                        """UPDATE basincomps_batch_run
                           SET status = 'RUNNING',
                               product_ids = %s::uuid[],
                               start_time = COALESCE(start_time, %s)
                           WHERE id = %s""",
                        (product_ids, start_time, batch_id)
                    )
                else:
                    # Create new batch run
                    batch_id = str(uuid.uuid4())
                    logger.info(f"Creating new batch run {batch_id}")

                    cur.execute(
                        """INSERT INTO basincomps_batch_run
                           (id, run_date, start_time, status, product_ids)
                           VALUES (%s, %s, %s, %s, %s::uuid[])""",
                        (batch_id, run_date, start_time, 'RUNNING', product_ids)
                    )

                conn.commit()
                return batch_id

    def update_batch_run(
        self,
        batch_id: str,
        status: str,
        file_count: int = None,
        result_count: int = None,
        error_message: str = None,
        end_time: datetime = None
    ):
        """Update batch run record"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE basincomps_batch_run
                       SET status = %s,
                           file_count = COALESCE(%s, file_count),
                           result_count = COALESCE(%s, result_count),
                           error_message = %s,
                           end_time = %s
                       WHERE id = %s""",
                    (status, file_count, result_count, error_message, end_time, batch_id)
                )
                conn.commit()

    def get_product_files(
        self,
        product_slugs: List[str],
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get product files for time window

        For forecast products: Returns files from the latest available forecast versions
        that cover each datetime in the window. Uses up to 3 recent forecast runs to
        ensure complete coverage (e.g., if newest forecast only goes 2 days out, older
        forecasts fill in days 3+).

        For observed products: Returns all files in the time window
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """WITH recent_versions AS (
                           -- For each product, get the 3 most recent forecast versions
                           -- that have files in our time window
                           SELECT DISTINCT
                               p.id AS product_id,
                               pf.version
                           FROM productfile pf
                           INNER JOIN product p ON p.id = pf.product_id
                           LEFT JOIN v_product vp ON vp.id = p.id
                           WHERE p.slug = ANY(%s)
                             AND pf.datetime >= %s
                             AND pf.datetime <= %s
                             AND vp.last_forecast_version IS NOT NULL  -- Only for forecast products
                             AND pf.version IS NOT NULL
                           ORDER BY p.id, pf.version DESC
                       ),
                       top_versions AS (
                           -- Limit to top 50 versions per product using window function
                           -- This ensures we get enough older forecast runs to cover the full time window
                           -- especially for products like NDFD that issue forecasts hourly
                           SELECT
                               product_id,
                               version,
                               ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY version DESC) AS version_rank
                           FROM recent_versions
                       ),
                       ranked_files AS (
                           SELECT
                               pf.id,
                               pf.datetime,
                               pf.file AS key,
                               pf.version,
                               p.id AS product_id,
                               p.slug AS product_slug,
                               p.temporal_duration,
                               vp.name AS product_name,
                               vp.last_forecast_version AS last_forecast_version,
                               u.abbreviation AS unit,
                               (SELECT config_value FROM config WHERE config_name = 'write_to_bucket') AS bucket,
                               -- For forecast products, rank by version (latest = 1) per datetime
                               CASE
                                   WHEN vp.last_forecast_version IS NOT NULL
                                   THEN ROW_NUMBER() OVER (PARTITION BY p.id, pf.datetime ORDER BY pf.version DESC NULLS LAST)
                                   ELSE 1
                               END AS version_rank
                           FROM productfile pf
                           INNER JOIN product p ON p.id = pf.product_id
                           LEFT JOIN v_product vp ON vp.id = p.id
                           LEFT JOIN unit u ON u.id = p.unit_id
                           LEFT JOIN top_versions tv ON tv.product_id = p.id AND tv.version = pf.version
                           WHERE p.slug = ANY(%s)
                             AND pf.datetime >= %s
                             AND pf.datetime <= %s
                             AND (
                                 -- Include if it's not a forecast product (observed data)
                                 vp.last_forecast_version IS NULL
                                 OR
                                 -- Include if it's from one of the top 50 recent forecast versions
                                 (tv.version_rank IS NOT NULL AND tv.version_rank <= 50)
                             )
                       )
                       SELECT
                           id,
                           datetime,
                           key,
                           product_id,
                           product_slug,
                           temporal_duration,
                           product_name,
                           last_forecast_version,
                           unit,
                           bucket
                       FROM ranked_files
                       WHERE version_rank = 1
                       ORDER BY product_slug, datetime""",
                    (product_slugs, start_time, end_time, product_slugs, start_time, end_time)
                )

                return [dict(row) for row in cur.fetchall()]

    def insert_results(self, results: List[Dict[str, Any]]):
        """Insert basin average results"""
        if not results:
            return

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Get product IDs
                product_slugs = list(set(r['product_slug'] for r in results))
                cur.execute(
                    "SELECT slug, id FROM product WHERE slug = ANY(%s)",
                    (product_slugs,)
                )
                slug_to_id = {row[0]: row[1] for row in cur.fetchall()}

                # Prepare values
                values = [
                    (
                        r['run_date'],
                        r['data_date'],
                        r['data_datetime'],
                        r['basin_id'],
                        r['basin_name'],
                        slug_to_id.get(r['product_slug']),
                        r['product_slug'],
                        r['interval_hours'],
                        r['value'],
                        r['units']
                    )
                    for r in results
                ]

                # Bulk insert
                execute_values(
                    cur,
                    """INSERT INTO basincomps_daily_result
                       (run_date, data_date, data_datetime, basin_id, basin_name,
                        product_id, product_slug, interval_hours, value, units)
                       VALUES %s""",
                    values
                )

                conn.commit()

                logger.info(f"Inserted {len(results)} results")

    def get_shapefile_configs(self) -> List[Dict[str, Any]]:
        """Get all enabled shapefile configurations"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT
                           sc.id,
                           sc.config_name,
                           sc.description,
                           sc.shapefile_path,
                           sc.product_ids,
                           array_agg(p.slug ORDER BY p.slug) AS product_slugs
                       FROM basincomps_shapefile_config sc
                       INNER JOIN product p ON p.id = ANY(sc.product_ids)
                       WHERE sc.enabled = true
                       GROUP BY sc.id, sc.config_name, sc.description, sc.shapefile_path, sc.product_ids"""
                )

                return [dict(row) for row in cur.fetchall()]

    def insert_rolling_totals(self, totals: List[Dict[str, Any]]):
        """Insert rolling precipitation totals"""
        if not totals:
            return

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Get product IDs
                product_slugs = list(set(t['product_slug'] for t in totals))
                cur.execute(
                    "SELECT slug, id FROM product WHERE slug = ANY(%s)",
                    (product_slugs,)
                )
                slug_to_id = {row[0]: row[1] for row in cur.fetchall()}

                # Prepare values
                values = [
                    (
                        t['run_date'],
                        t['data_date'],
                        t['basin_id'],
                        t['basin_name'],
                        slug_to_id.get(t['product_slug']),
                        t['product_slug'],
                        t['days'],
                        t['total_value'],
                        t['units']
                    )
                    for t in totals
                ]

                # Bulk insert with conflict handling
                execute_values(
                    cur,
                    """INSERT INTO basincomps_rolling_total
                       (run_date, data_date, basin_id, basin_name,
                        product_id, product_slug, days, total_value, units)
                       VALUES %s
                       ON CONFLICT (basin_id, product_id, data_date, days)
                       DO UPDATE SET
                           total_value = EXCLUDED.total_value,
                           run_date = EXCLUDED.run_date""",
                    values
                )

                conn.commit()

                logger.info(f"Inserted/updated {len(totals)} rolling totals")
