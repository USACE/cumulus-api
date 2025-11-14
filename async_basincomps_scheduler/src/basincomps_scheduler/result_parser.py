"""Parse BasinComps CSV output"""
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, date, timezone
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def parse_basincomps_csv(
    csv_path: Path,
    product_slug: str,
    run_date: datetime,
    is_forecast: bool = False
) -> List[Dict[str, Any]]:
    """
    Parse BasinComps CSV output

    Expected CSV format:
    Basin,Date,Time,Interval,Value,Units
    UPPER_RUSSIAN,01JAN2024,0000,1Hour,12.5,mm

    Args:
        csv_path: Path to CSV file
        product_slug: Product slug
        run_date: Timestamp of the batch run with timezone
        is_forecast: Whether this is a forecast product (True) or observed (False)

    Returns:
        List of result dictionaries
    """
    logger.info(f"Parsing CSV: {csv_path}")

    # Read CSV with Time column as string to preserve leading zeros
    df = pd.read_csv(csv_path, dtype={'Time': str})

    logger.info(f"Loaded {len(df)} rows from CSV")
    logger.info(f"CSV columns: {list(df.columns)}")

    if len(df) > 0:
        logger.info(f"First row: {df.iloc[0].to_dict()}")
    else:
        logger.warning("CSV is empty!")

    results = []

    for _, row in df.iterrows():
        try:
            # Parse date and time
            date_str = row['Date']
            time_str = str(row['Time']).strip()

            # Ensure time string is 4 digits (pad with zeros if needed)
            # This handles cases where pandas converts '0000' to 0
            time_str = time_str.zfill(4)

            # Convert from format like "01JAN2024" and "0000"
            # Create timezone-aware datetime in UTC (matching productfile.datetime timezone)
            dt = datetime.strptime(f"{date_str} {time_str}", "%d%b%Y %H%M").replace(tzinfo=timezone.utc)

            # Parse interval (e.g., "1Hour")
            interval_str = row['Interval']
            interval_hours = _parse_interval(interval_str)

            result = {
                'run_date': run_date,
                'data_date': dt.date(),
                'data_datetime': dt,
                'basin_id': str(row['Basin']),
                'basin_name': str(row['Basin']),  # Can be enriched from shapefile
                'product_slug': product_slug,
                'is_forecast': is_forecast,
                'interval_hours': interval_hours,
                'value': float(row['Value']),
                'units': str(row['Units'])
            }

            results.append(result)

        except Exception as e:
            logger.warning(f"Failed to parse row: {row.to_dict()}, error: {e}")
            continue

    logger.info(f"Parsed {len(results)} results")

    return results


def _parse_interval(interval_str: str) -> int:
    """Parse interval string like '1Hour', '6Hour', '1Day' to hours"""
    interval_str = interval_str.lower()

    if 'hour' in interval_str:
        return int(interval_str.replace('hour', ''))
    elif 'day' in interval_str:
        days = int(interval_str.replace('day', ''))
        return days * 24
    else:
        logger.warning(f"Unknown interval format: {interval_str}, defaulting to 1 hour")
        return 1
