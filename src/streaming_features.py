"""Real-time feature engineering engine for fraud detection."""

import statistics
from collections import defaultdict
from typing import Dict, Any, List, Optional

from .utils.state_store import StateStore
from .utils.time_utils import (
    is_within_window, get_time_features, calculate_time_diff_minutes,
    get_hour_window
)
from .utils.validation_utils import validate_feature_vector
from .utils.logging_utils import setup_logging


class RealTimeFeatureEngine:
    """Real-time feature engineering engine for fraud detection."""

    def __init__(self, state_store: Optional[StateStore] = None):
        self.state_store = state_store or StateStore()
        self.logger = setup_logging()

        # Feature configuration
        self.velocity_window_hours = 1
        self.amount_history_window_hours = 24
        self.location_history_window_hours = 168  # 1 week

    def process_event(self, event: Dict[str, Any]) -> bool:
        """Process a transaction event and update user features."""
        try:
            # Ensure event has timestamp_unix field
            if 'timestamp_unix' not in event and 'timestamp' in event:
                from .utils.time_utils import parse_timestamp
                event = event.copy()  # Don't modify original
                event['timestamp_unix'] = parse_timestamp(event['timestamp'])

            # Update user's event history
            user_id = event['user_id']
            self.state_store.update_user_events(user_id, event)

            # Calculate and update features
            features = self._calculate_features(user_id)
            self.state_store.update_user_features(user_id, features)

            # Periodic cleanup
            if self.state_store.should_cleanup():
                cleared = self.state_store.clear_old_entries()
                if cleared > 0:
                    self.logger.info(f"Cleared {cleared} old user entries")

            return True

        except Exception as e:
            self.logger.error(f"Failed to process event: {e}")
            return False

    def get_features(self, user_id: str) -> Dict[str, Any]:
        """Get latest feature vector for user."""
        features = self.state_store.get_user_features(user_id)

        # Ensure all required features are present with defaults
        default_features = {
            'transaction_velocity_1h': 0.0,
            'amount_zscore': 0.0,
            'location_anomaly': 0,
            'time_pattern_score': 0.0,
            'merchant_diversity': 0.0,
            'payment_method_consistency': 1.0,
            'amount_volatility': 0.0,
            'location_consistency': 1.0
        }

        # Merge with existing features
        for key, default_value in default_features.items():
            if key not in features:
                features[key] = default_value

        return features

    def _calculate_features(self, user_id: str) -> Dict[str, Any]:
        """Calculate all features for a user."""
        features = {}

        # Get recent events
        recent_events_1h = self.state_store.get_recent_events(user_id, 60)  # 1 hour
        recent_events_24h = self.state_store.get_recent_events(user_id, 1440)  # 24 hours
        recent_events_1w = self.state_store.get_recent_events(user_id, 10080)  # 1 week

        # Transaction velocity (transactions per hour in last hour)
        features['transaction_velocity_1h'] = len(recent_events_1h)

        # Amount-based features
        if recent_events_24h:
            features.update(self._calculate_amount_features(recent_events_24h))

        # Location-based features
        if recent_events_1w:
            features.update(self._calculate_location_features(recent_events_1w))

        # Time-based features
        if recent_events_1w:
            features.update(self._calculate_time_features(recent_events_1w))

        # Merchant and payment method diversity
        if recent_events_1w:
            features.update(self._calculate_behavioral_features(recent_events_1w))

        return features

    def _calculate_amount_features(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate amount-related features."""
        amounts = [e.get('amount', 0) for e in events]

        if len(amounts) < 2:
            return {
                'amount_zscore': 0.0,
                'amount_volatility': 0.0
            }

        # Calculate z-score for the most recent amount
        recent_amount = amounts[-1]
        historical_amounts = amounts[:-1]

        if not historical_amounts:
            return {
                'amount_zscore': 0.0,
                'amount_volatility': 0.0
            }

        mean_amount = statistics.mean(historical_amounts)

        # Handle case where all historical amounts are the same
        if len(historical_amounts) == 1:
            # If only one historical amount, use a small default std dev
            std_amount = abs(mean_amount) * 0.1 if mean_amount != 0 else 1.0
        else:
            try:
                std_amount = statistics.stdev(historical_amounts)
                # If std dev is very small or zero, use a minimum threshold
                if std_amount == 0:
                    std_amount = abs(mean_amount) * 0.1 if mean_amount != 0 else 1.0
            except statistics.StatisticsError:
                std_amount = abs(mean_amount) * 0.1 if mean_amount != 0 else 1.0

        zscore = (recent_amount - mean_amount) / std_amount

        # Amount volatility (coefficient of variation)
        volatility = std_amount / mean_amount if mean_amount > 0 else 0

        return {
            'amount_zscore': zscore,
            'amount_volatility': volatility
        }

    def _calculate_location_features(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate location-based features."""
        locations = [e.get('location', '') for e in events if e.get('location')]
        recent_location = events[-1].get('location', '') if events else ''

        if not locations:
            return {
                'location_anomaly': 0,
                'location_consistency': 1.0
            }

        # Simple anomaly detection: flag if recent location is rare
        location_counts = defaultdict(int)
        for loc in locations:
            location_counts[loc] += 1

        total_locations = len(locations)
        recent_count = location_counts.get(recent_location, 0)

        # Anomaly if this location appears in <= 10% of transactions
        anomaly = 1 if recent_count / total_locations <= 0.1 and total_locations > 5 else 0

        # Location consistency (ratio of primary location)
        primary_location_count = max(location_counts.values()) if location_counts else 0
        consistency = primary_location_count / total_locations if total_locations > 0 else 1.0

        return {
            'location_anomaly': anomaly,
            'location_consistency': consistency
        }

    def _calculate_time_features(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate time-based features."""
        if not events:
            return {'time_pattern_score': 0.0}

        # Analyze transaction timing patterns
        hours = []
        weekdays = []

        for event in events:
            timestamp = event.get('timestamp_unix', 0)
            if timestamp > 0:
                time_features = get_time_features(timestamp)
                hours.append(time_features['hour_of_day'])
                weekdays.append(time_features['day_of_week'])

        if not hours:
            return {'time_pattern_score': 0.0}

        # Calculate pattern deviation
        # Score based on how unusual the recent transaction time is
        recent_hour = hours[-1]
        recent_weekday = weekdays[-1] if weekdays else 0

        hour_counts = defaultdict(int)
        weekday_counts = defaultdict(int)

        for h, w in zip(hours[:-1], weekdays[:-1]) if len(hours) > 1 else []:
            hour_counts[h] += 1
            weekday_counts[w] += 1

        # Pattern score: higher for unusual timing
        total_historical = len(hours) - 1
        if total_historical > 0:
            recent_hour_freq = hour_counts.get(recent_hour, 0) / total_historical
            recent_weekday_freq = weekday_counts.get(recent_weekday, 0) / total_historical

            # Unusual timing gets higher score
            pattern_score = 1.0 - (recent_hour_freq + recent_weekday_freq) / 2
        else:
            pattern_score = 0.0

        return {'time_pattern_score': pattern_score}

    def _calculate_behavioral_features(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate merchant and payment method diversity features."""
        merchants = [e.get('merchant', '') for e in events if e.get('merchant')]
        payment_methods = [e.get('payment_method', '') for e in events if e.get('payment_method')]

        # Merchant diversity (unique merchants / total transactions)
        unique_merchants = len(set(merchants)) if merchants else 0
        total_transactions = len(events)
        merchant_diversity = unique_merchants / total_transactions if total_transactions > 0 else 0

        # Payment method consistency
        if payment_methods:
            method_counts = defaultdict(int)
            for method in payment_methods:
                method_counts[method] += 1
            primary_method_count = max(method_counts.values())
            payment_consistency = primary_method_count / len(payment_methods)
        else:
            payment_consistency = 1.0

        return {
            'merchant_diversity': merchant_diversity,
            'payment_method_consistency': payment_consistency
        }
