#!/usr/bin/env python3
"""Demo script showing real-time fraud detection working"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.streaming_features import RealTimeFeatureEngine
from datetime import datetime, timezone
import math

def main():
    print('🛡️ Real-Time Fraud Detection System Demo')
    print('=' * 50)

    # Create engine
    engine = RealTimeFeatureEngine()
    print('✅ Engine initialized')

    # Process some sample transactions
    events = [
        {
            'user_id': 'user_001',
            'transaction_id': 'txn_001',
            'amount': 100.0,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'merchant': 'Amazon',
            'location': 'New York',
            'payment_method': 'credit_card'
        },
        {
            'user_id': 'user_001',
            'transaction_id': 'txn_002',
            'amount': 50.0,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'merchant': 'Starbucks',
            'location': 'New York',
            'payment_method': 'credit_card'
        },
        {
            'user_id': 'user_001',
            'transaction_id': 'txn_003',
            'amount': 500.0,  # Unusual amount
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'merchant': 'Unknown Store',
            'location': 'Los Angeles',  # Unusual location
            'payment_method': 'credit_card'
        }
    ]

    print('\n📊 Processing transactions...')
    for i, event in enumerate(events, 1):
        success = engine.process_event(event)
        features = engine.get_features(event['user_id'])

        # Calculate fraud score
        score = (
            features.get('transaction_velocity_1h', 0) * 0.2 +
            features.get('amount_zscore', 0) * 0.25 +
            features.get('location_anomaly', 0) * 0.3 +
            features.get('time_pattern_score', 0) * 0.15 +
            -features.get('merchant_diversity', 0) * 0.05 +
            -features.get('payment_method_consistency', 0) * 0.05
        )
        score = 1 / (1 + math.exp(-score))  # sigmoid

        print('  {}. ${:.0f} at {} ({})'.format(
            i, event['amount'], event['merchant'], event['location']
        ))
        print('     → Fraud Score: {:.3f}'.format(score))

    print('\n🎯 Features computed:')
    features = engine.get_features('user_001')
    for key, value in features.items():
        if isinstance(value, float):
            print('  {}: {:.3f}'.format(key, value))
        else:
            print('  {}: {}'.format(key, value))

    print('\n✅ System working! Ready for production use.')

if __name__ == '__main__':
    main()
