"""Logging utilities for the fraud detection system."""

import logging
import sys
from typing import Dict, Any


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup structured logging."""
    logger = logging.getLogger("fraud_detection")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


def log_event_processing(event: Dict[str, Any], user_id: str, logger: logging.Logger) -> None:
    """Log event processing with key details."""
    logger.info(
        f"Processing event for user {user_id}: "
        f"transaction={event.get('transaction_id', 'unknown')}, "
        f"amount=${event.get('amount', 0):.2f}, "
        f"merchant={event.get('merchant', 'unknown')}"
    )


def log_feature_update(user_id: str, features: Dict[str, Any], logger: logging.Logger) -> None:
    """Log feature vector updates."""
    logger.debug(
        f"Updated features for user {user_id}: "
        f"velocity={features.get('transaction_velocity_1h', 0):.2f}, "
        f"zscore={features.get('amount_zscore', 0):.2f}, "
        f"anomaly={features.get('location_anomaly', 0)}"
    )


def log_api_request(endpoint: str, method: str, status_code: int, logger: logging.Logger) -> None:
    """Log API request completion."""
    logger.info(f"API {method} {endpoint} - Status: {status_code}")


def log_error(error: Exception, context: str, logger: logging.Logger) -> None:
    """Log error with context."""
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)
