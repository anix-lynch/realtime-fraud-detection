"""Validation utilities for event data."""

import re
from typing import Dict, Any, List, Optional


REQUIRED_EVENT_FIELDS = [
    'user_id', 'transaction_id', 'amount', 'timestamp'
]

OPTIONAL_EVENT_FIELDS = [
    'merchant', 'location', 'payment_method'
]


def validate_event(event: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate event structure and required fields."""
    if not isinstance(event, dict):
        return False, "Event must be a dictionary"

    # Check required fields
    for field in REQUIRED_EVENT_FIELDS:
        if field not in event:
            return False, f"Missing required field: {field}"

    # Validate field types and values
    if not isinstance(event['user_id'], str) or not event['user_id'].strip():
        return False, "user_id must be a non-empty string"

    if not isinstance(event['transaction_id'], str) or not event['transaction_id'].strip():
        return False, "transaction_id must be a non-empty string"

    if not isinstance(event['amount'], (int, float)) or event['amount'] < 0:
        return False, "amount must be a non-negative number"

    if not isinstance(event['timestamp'], str):
        return False, "timestamp must be a string"

    # Validate optional fields if present
    if 'merchant' in event and not isinstance(event['merchant'], str):
        return False, "merchant must be a string"

    if 'location' in event and not isinstance(event['location'], str):
        return False, "location must be a string"

    if 'payment_method' in event and not isinstance(event['payment_method'], str):
        return False, "payment_method must be a string"

    return True, None


def validate_user_id(user_id: str) -> bool:
    """Validate user ID format."""
    if not user_id or not isinstance(user_id, str):
        return False
    # Allow alphanumeric, underscores, hyphens
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', user_id))


def sanitize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize and normalize event data."""
    sanitized = {}

    # Copy and sanitize required fields
    for field in REQUIRED_EVENT_FIELDS + OPTIONAL_EVENT_FIELDS:
        if field in event:
            value = event[field]
            if isinstance(value, str):
                sanitized[field] = value.strip()
            else:
                sanitized[field] = value

    # Add timestamp_unix for internal use
    if 'timestamp' in sanitized:
        from .time_utils import parse_timestamp
        sanitized['timestamp_unix'] = parse_timestamp(sanitized['timestamp'])

    return sanitized


def validate_feature_vector(features: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate feature vector structure."""
    required_features = [
        'transaction_velocity_1h',
        'amount_zscore',
        'location_anomaly',
        'time_pattern_score'
    ]

    for feature in required_features:
        if feature not in features:
            return False, f"Missing required feature: {feature}"

        if not isinstance(features[feature], (int, float)):
            return False, f"Feature {feature} must be numeric"

    return True, None
