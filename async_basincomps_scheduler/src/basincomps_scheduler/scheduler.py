"""BasinComps Scheduled Batch Processor"""
import logging
import os
import time
import schedule
from datetime import datetime

from basincomps_scheduler.batch_processor import BasinCompsBatchProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_daily_job():
    """Execute daily BasinComps batch job"""
    logger.info("=" * 80)
    logger.info(f"Starting BasinComps daily batch job at {datetime.now()}")
    logger.info("=" * 80)

    try:
        processor = BasinCompsBatchProcessor()
        processor.run()
        logger.info("BasinComps batch job completed successfully")
    except Exception as e:
        logger.error(f"BasinComps batch job failed: {e}", exc_info=True)


def check_for_triggered_runs():
    """Check for manually triggered runs and execute them"""
    from basincomps_scheduler.utils.database import DatabaseClient

    db = DatabaseClient()

    try:
        with db._get_connection() as conn:
            with conn.cursor() as cur:
                # Check for any runs with TRIGGERED status
                cur.execute(
                    """SELECT id, run_date
                       FROM basincomps_batch_run
                       WHERE status = 'TRIGGERED'
                       ORDER BY start_time ASC
                       LIMIT 1"""
                )

                result = cur.fetchone()

                if result:
                    batch_id, run_date = result
                    logger.info(f"Found triggered batch run {batch_id} for {run_date}, running job...")

                    # Execute the job (it will update the existing batch run)
                    run_daily_job()

    except Exception as e:
        logger.error(f"Error checking for triggered runs: {e}", exc_info=True)


def main():
    """Main scheduler loop"""

    enabled = os.getenv('BASINCOMPS_ENABLED', 'true').lower() == 'true'
    if not enabled:
        logger.info("BasinComps scheduler is disabled")
        return

    cron_schedule = os.getenv('BASINCOMPS_SCHEDULE', '0 0 * * *')

    # Parse cron to schedule format (simplified - daily at midnight)
    # For production, consider using APScheduler for full cron support
    hour, minute = 0, 0  # Default midnight
    if cron_schedule.startswith('0 0'):
        hour, minute = 0, 0

    logger.info(f"BasinComps scheduler started")
    logger.info(f"Schedule: Daily at {hour:02d}:{minute:02d}")
    logger.info(f"Shapefile: {os.getenv('BASINCOMPS_SHAPEFILE_PATH')}")
    logger.info(f"Products: {os.getenv('BASINCOMPS_PRODUCT_SLUGS')}")

    # Schedule daily job
    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(run_daily_job)

    # Optionally run immediately on startup for testing
    if os.getenv('BASINCOMPS_RUN_ON_STARTUP', 'false').lower() == 'true':
        logger.info("Running job immediately (BASINCOMPS_RUN_ON_STARTUP=true)")
        run_daily_job()

    # Main loop
    logger.info("Entering main scheduler loop (checking every 60 seconds)")
    while True:
        # Check for scheduled jobs
        schedule.run_pending()

        # Check for manually triggered runs
        check_for_triggered_runs()

        # Wait before next check
        time.sleep(60)  # Check every minute


if __name__ == '__main__':
    main()
