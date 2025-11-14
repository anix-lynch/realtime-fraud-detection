"""Time utilities for real-time feature engineering."""

import time
from datetime import datetime, timedelta
from typing import Optional, Tuple


def parse_timestamp(timestamp_str: str) -> float:
    """Parse ISO timestamp string to unix timestamp."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.timestamp()
    except (ValueError, AttributeError):
        # Fallback to current time if parsing fails
        return time.time()


def get_current_unix_timestamp() -> float:
    """Get current unix timestamp."""
    return time.time()


def is_within_window(timestamp: float, window_minutes: int) -> bool:
    """Check if timestamp is within the specified window from now."""
    current_time = time.time()
    window_seconds = window_minutes * 60
    return current_time - timestamp <= window_seconds


def get_time_features(timestamp: float) -> dict:
    """Extract time-based features from timestamp."""
    dt = datetime.fromtimestamp(timestamp)

    return {
        'hour_of_day': dt.hour,
        'day_of_week': dt.weekday(),  # 0=Monday, 6=Sunday
        'is_weekend': 1 if dt.weekday() >= 5 else 0,
        'is_business_hours': 1 if 9 <= dt.hour <= 17 else 0,
        'month': dt.month,
        'day_of_month': dt.day
    }


def calculate_time_diff_minutes(timestamp1: float, timestamp2: float) -> float:
    """Calculate difference between two timestamps in minutes."""
    return abs(timestamp1 - timestamp2) / 60


def get_hour_window(timestamp: float) -> Tuple[int, int]:
    """Get the start and end hour for a timestamp (for grouping)."""
    dt = datetime.fromtimestamp(timestamp)
    start_hour = dt.replace(minute=0, second=0, microsecond=0)
    end_hour = start_hour + timedelta(hours=1)

    return int(start_hour.timestamp()), int(end_hour.timestamp())
