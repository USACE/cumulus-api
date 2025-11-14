"""Calculate rolling precipitation totals from hourly data"""
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


def calculate_rolling_totals(
    hourly_results: List[Dict[str, Any]],
    run_date: datetime
) -> List[Dict[str, Any]]:
    """
    Calculate rolling precipitation totals (1-10 days) from hourly data

    For observed products (is_forecast=False): calculates backward-looking totals (past N days)
    For forecast products (is_forecast=True): calculates forward-looking totals (next N days)

    Args:
        hourly_results: List of hourly basin average results
        run_date: Timestamp of the batch run with timezone

    Returns:
        List of rolling total dictionaries
    """
    # Group by basin and product
    grouped = defaultdict(list)
    for result in hourly_results:
        key = (result['basin_id'], result['product_slug'], result['is_forecast'])
        grouped[key].append(result)

    rolling_totals = []

    # For each basin/product combination
    for (basin_id, product_slug, is_forecast), results in grouped.items():
        # Sort by datetime
        sorted_results = sorted(results, key=lambda x: x['data_datetime'])

        if len(sorted_results) == 0:
            continue

        # Group by date and sum to get daily totals
        daily_totals = _calculate_daily_totals(sorted_results)

        # Calculate rolling sums for 1-10 days
        rolling = _calculate_rolling_sums(daily_totals, run_date, is_forecast)

        rolling_totals.extend(rolling)

    logger.info(f"Calculated {len(rolling_totals)} rolling totals")

    return rolling_totals


def _calculate_daily_totals(hourly_results: List[Dict[str, Any]]) -> Dict[datetime.date, Dict[str, Any]]:
    """Calculate daily precipitation totals from hourly data"""
    daily = defaultdict(lambda: {
        'total': 0.0,
        'count': 0,
        'basin_id': None,
        'basin_name': None,
        'product_slug': None,
        'units': None
    })

    for result in hourly_results:
        date = result['data_datetime'].date()

        daily[date]['total'] += result['value']
        daily[date]['count'] += 1
        daily[date]['basin_id'] = result['basin_id']
        daily[date]['basin_name'] = result['basin_name']
        daily[date]['product_slug'] = result['product_slug']
        daily[date]['units'] = result['units']

    return daily


def _calculate_rolling_sums(
    daily_totals: Dict[datetime.date, Dict[str, Any]],
    run_date: datetime,
    is_forecast: bool = False
) -> List[Dict[str, Any]]:
    """
    Calculate rolling sums for 1-10 days (only creates complete periods)

    For observed products: backward-looking (past N days from latest date)
    For forecast products: forward-looking (next N days from earliest date)

    Only creates rolling totals when complete data is available:
    - A 7-day total is only created if 7 full days of data exist
    - A 3-day forecast will only produce 1, 2, and 3-day rolling totals
    - Missing days in sequence will prevent rolling totals that span the gap

    This ensures API consumers receive only accurate, complete rolling totals
    """
    if not daily_totals:
        return []

    # Get sorted dates
    sorted_dates = sorted(daily_totals.keys())

    if len(sorted_dates) == 0:
        return []

    # Determine reference date based on product type
    if is_forecast:
        # For forecasts, use earliest date as reference (looking forward)
        reference_date = sorted_dates[0]
    else:
        # For observed, use latest date as reference (looking backward)
        reference_date = sorted_dates[-1]

    # Get metadata from reference day
    ref_data = daily_totals[reference_date]
    basin_id = ref_data['basin_id']
    basin_name = ref_data['basin_name']
    product_slug = ref_data['product_slug']
    units = ref_data['units']

    rolling_totals = []

    # Calculate rolling totals for 1-10 days
    for days in range(1, 11):
        if is_forecast:
            # Forward-looking: from reference_date to reference_date + (days - 1)
            start_date = reference_date
            end_date = reference_date + timedelta(days=days - 1)
        else:
            # Backward-looking: from reference_date - (days - 1) to reference_date
            end_date = reference_date
            start_date = reference_date - timedelta(days=days - 1)

        # Sum values in range (only for dates that have data)
        total = 0.0
        days_with_data = 0

        for date in sorted_dates:
            if start_date <= date <= end_date:
                total += daily_totals[date]['total']
                days_with_data += 1

        # Only create rolling total if we have COMPLETE data for the full period
        # This ensures partial forecasts don't create misleading rolling totals
        # (e.g., a 3-day forecast won't create a "7-day" total with only 3 days of data)
        if days_with_data == days:
            rolling_totals.append({
                'run_date': run_date,
                'data_date': end_date if not is_forecast else start_date,  # Reference date for the period
                'basin_id': basin_id,
                'basin_name': basin_name,
                'product_slug': product_slug,
                'days': days,
                'total_value': total,
                'units': units
            })

    logger.info(f"Calculated {len(rolling_totals)} rolling totals for {product_slug} "
                f"({'forecast' if is_forecast else 'observed'})")

    return rolling_totals
