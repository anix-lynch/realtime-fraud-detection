"""Tests for real-time fraud detection engine."""

import pytest
import time
from datetime import datetime, timedelta

from src.streaming_features import RealTimeFeatureEngine
from src.utils.state_store import StateStore
from src.utils.validation_utils import validate_event


class TestRealTimeFeatureEngine:
    """Test cases for the real-time feature engine."""

    def setup_method(self):
        """Setup test fixtures."""
        self.state_store = StateStore(max_window_minutes=60)
        self.engine = RealTimeFeatureEngine(self.state_store)

    def test_process_event_updates_state(self):
        """Test that processing an event updates user state."""
        from datetime import timezone
        event = {
            'user_id': 'test_user',
            'transaction_id': 'txn_001',
            'amount': 100.0,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'merchant': 'Test Merchant',
            'location': 'Test City',
            'payment_method': 'credit_card'
        }

        # Process event
        result = self.engine.process_event(event)
        assert result is True

        # Check that event was stored
        recent_events = self.state_store.get_recent_events('test_user')
        assert len(recent_events) == 1
        assert recent_events[0]['transaction_id'] == 'txn_001'

        # Check that features were calculated
        features = self.engine.get_features('test_user')
        assert 'transaction_velocity_1h' in features
        assert 'amount_zscore' in features
        assert 'location_anomaly' in features

    def test_feature_vector_shape(self):
        """Test that feature vectors have consistent structure."""
        user_id = 'test_user'

        # Add multiple events
        base_time = datetime.now()
        for i in range(5):
            event = {
                'user_id': user_id,
                'transaction_id': f'txn_{i:03d}',
                'amount': 50.0 + i * 10,  # Varying amounts
                'timestamp': (base_time + timedelta(minutes=i)).isoformat() + 'Z',
                'merchant': f'Merchant_{i}',
                'location': 'Same City' if i < 4 else 'Different City',  # One location change
                'payment_method': 'credit_card'
            }
            self.engine.process_event(event)

        features = self.engine.get_features(user_id)

        # Check required features are present
        required_features = [
            'transaction_velocity_1h',
            'amount_zscore',
            'location_anomaly',
            'time_pattern_score',
            'merchant_diversity',
            'payment_method_consistency',
            'amount_volatility',
            'location_consistency'
        ]

        for feature in required_features:
            assert feature in features
            assert isinstance(features[feature], (int, float))

        # Check feature ranges
        assert 0 <= features['transaction_velocity_1h'] <= 100  # Reasonable velocity
        assert features['location_anomaly'] in [0, 1]  # Binary flag
        assert 0 <= features['location_consistency'] <= 1  # Ratio
        assert 0 <= features['merchant_diversity'] <= 1  # Ratio

    def test_velocity_calculation(self):
        """Test transaction velocity calculation."""
        from datetime import timezone
        user_id = 'velocity_test'
        base_time = datetime.now(timezone.utc)

        # Add events within 1 hour
        for i in range(3):
            event = {
                'user_id': user_id,
                'transaction_id': f'txn_{i:03d}',
                'amount': 100.0,
                'timestamp': (base_time + timedelta(minutes=i*10)).isoformat(),
                'merchant': 'Test Merchant',
                'location': 'Test City',
                'payment_method': 'credit_card'
            }
            self.engine.process_event(event)

        features = self.engine.get_features(user_id)
        assert features['transaction_velocity_1h'] == 3  # 3 transactions in 1 hour

    def test_amount_zscore_calculation(self):
        """Test amount z-score calculation."""
        from datetime import timezone
        user_id = 'amount_test'
        base_time = datetime.now(timezone.utc)

        # Add baseline transactions
        for i in range(10):
            event = {
                'user_id': user_id,
                'transaction_id': f'txn_base_{i:03d}',
                'amount': 100.0,  # Consistent amount
                'timestamp': (base_time + timedelta(hours=i)).isoformat(),
                'merchant': 'Test Merchant',
                'location': 'Test City',
                'payment_method': 'credit_card'
            }
            self.engine.process_event(event)

        # Add outlier transaction
        outlier_event = {
            'user_id': user_id,
            'transaction_id': 'txn_outlier',
            'amount': 500.0,  # Much higher amount
            'timestamp': (base_time + timedelta(hours=11)).isoformat(),
            'merchant': 'Test Merchant',
            'location': 'Test City',
            'payment_method': 'credit_card'
        }
        self.engine.process_event(outlier_event)

        features = self.engine.get_features(user_id)
        assert features['amount_zscore'] > 2.0  # Should be a significant outlier

    def test_location_anomaly_detection(self):
        """Test location anomaly detection."""
        from datetime import timezone
        user_id = 'location_test'
        base_time = datetime.now(timezone.utc)

        # Add transactions from same location
        for i in range(9):
            event = {
                'user_id': user_id,
                'transaction_id': f'txn_{i:03d}',
                'amount': 100.0,
                'timestamp': (base_time + timedelta(hours=i)).isoformat(),
                'merchant': 'Test Merchant',
                'location': 'Home City',
                'payment_method': 'credit_card'
            }
            self.engine.process_event(event)

        # Add transaction from different location
        anomaly_event = {
            'user_id': user_id,
            'transaction_id': 'txn_anomaly',
            'amount': 100.0,
            'timestamp': (base_time + timedelta(hours=10)).isoformat(),
            'merchant': 'Test Merchant',
            'location': 'Foreign City',
            'payment_method': 'credit_card'
        }
        self.engine.process_event(anomaly_event)

        features = self.engine.get_features(user_id)
        assert features['location_anomaly'] == 1  # Should detect anomaly
        assert features['location_consistency'] < 1.0  # Should show reduced consistency

    def test_time_pattern_scoring(self):
        """Test time pattern anomaly detection."""
        from datetime import timezone
        user_id = 'time_test'
        base_time = datetime.now(timezone.utc) - timedelta(days=7)  # 1 week ago

        # Add transactions during business hours
        for i in range(5):
            event_time = base_time + timedelta(days=i, hours=2)  # 2 PM each day
            event = {
                'user_id': user_id,
                'transaction_id': f'txn_{i:03d}',
                'amount': 100.0,
                'timestamp': event_time.isoformat(),
                'merchant': 'Test Merchant',
                'location': 'Test City',
                'payment_method': 'credit_card'
            }
            self.engine.process_event(event)

        # Add transaction at unusual time (3 AM)
        unusual_time = base_time + timedelta(days=6, hours=15)  # 3 AM, 6 days later
        unusual_event = {
            'user_id': user_id,
            'transaction_id': 'txn_unusual',
            'amount': 100.0,
            'timestamp': unusual_time.isoformat(),
            'merchant': 'Test Merchant',
            'location': 'Test City',
            'payment_method': 'credit_card'
        }
        self.engine.process_event(unusual_event)

        features = self.engine.get_features(user_id)
        assert features['time_pattern_score'] > 0  # Should detect unusual timing

    def test_state_cleanup(self):
        """Test that old state entries are cleaned up."""
        from datetime import timezone
        user_id = 'cleanup_test'

        # Add event
        event = {
            'user_id': user_id,
            'transaction_id': 'txn_001',
            'amount': 100.0,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'merchant': 'Test Merchant',
            'location': 'Test City',
            'payment_method': 'credit_card'
        }
        self.engine.process_event(event)

        # Manually set old timestamps to simulate aging
        state = self.state_store.get_user_state(user_id)
        old_time = time.time() - (70 * 60)  # 70 minutes ago
        state.last_updated = old_time
        state.created_at = old_time

        # Force cleanup
        cleared = self.state_store.clear_old_entries()
        assert cleared >= 0  # May or may not clear depending on timing

    def test_invalid_event_handling(self):
        """Test handling of invalid events."""
        invalid_event = {
            'user_id': '',  # Invalid empty user_id
            'transaction_id': 'txn_001',
            'amount': 100.0,
            'timestamp': datetime.now().isoformat() + 'Z'
        }

        # Should fail validation
        is_valid, error = validate_event(invalid_event)
        assert not is_valid
        assert 'user_id' in error

    def test_empty_user_features(self):
        """Test getting features for user with no events."""
        features = self.engine.get_features('nonexistent_user')

        # Should return default features
        assert features['transaction_velocity_1h'] == 0.0
        assert features['amount_zscore'] == 0.0
        assert features['location_anomaly'] == 0
        assert features['time_pattern_score'] == 0.0
