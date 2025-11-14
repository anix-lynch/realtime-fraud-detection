#!/usr/bin/env python3
"""
Real-Time Fraud Detection UI
Streamlit application for demonstrating fraud detection capabilities
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone
import json
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.streaming_features import RealTimeFeatureEngine

# Page configuration
st.set_page_config(
    page_title="🛡️ Real-Time Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'engine' not in st.session_state:
    st.session_state.engine = RealTimeFeatureEngine()

if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .score-high {
        color: #dc3545;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .score-low {
        color: #28a745;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🛡️ Real-Time Fraud Detection System</h1>', unsafe_allow_html=True)
    st.markdown("**Live demonstration of real-time feature engineering for fraud detection**")

    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")

        st.subheader("Transaction Input")
        with st.form("transaction_form"):
            user_id = st.text_input("User ID", value="demo_user", help="Unique user identifier")
            amount = st.number_input("Amount ($)", min_value=0.01, value=100.00, step=0.01)
            merchant = st.selectbox("Merchant", ["Amazon", "Walmart", "Starbucks", "Target", "Best Buy", "Apple", "Unknown"])
            location = st.selectbox("Location", ["New York", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle", "Unknown"])
            payment_method = st.selectbox("Payment Method", ["credit_card", "debit_card", "paypal", "apple_pay"])

            submitted = st.form_submit_button("🚀 Process Transaction")

            if submitted:
                process_transaction(user_id, amount, merchant, location, payment_method)

        st.divider()

        st.subheader("Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 Load Sample Data"):
                load_sample_data()
        with col2:
            if st.button("🗑️ Clear History"):
                clear_history()

        st.divider()

        st.subheader("System Status")
        stats = st.session_state.engine.state_store.get_stats()
        st.metric("Active Users", stats['total_users'])
        st.metric("Total Events", stats['total_events'])

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Recent Transactions")

        if st.session_state.transactions:
            df = pd.DataFrame(st.session_state.transactions[-10:])  # Show last 10

            # Format the dataframe for display
            display_df = df.copy()
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%H:%M:%S')
            display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")
            display_df = display_df[['timestamp', 'user_id', 'amount', 'merchant', 'location', 'fraud_score']]

            # Color code fraud scores
            def color_score(val):
                if val > 0.7:
                    return 'background-color: #ffebee'
                elif val > 0.4:
                    return 'background-color: #fff3e0'
                else:
                    return 'background-color: #e8f5e8'

            styled_df = display_df.style.apply(
                lambda x: [color_score(x['fraud_score']) if col == 'fraud_score' else '' for col in x.index],
                axis=1
            )

            st.dataframe(styled_df, use_container_width=True)

            # Fraud score distribution chart
            st.subheader("📈 Fraud Score Distribution")
            fig = px.histogram(
                df, x='fraud_score', nbins=20,
                title="Distribution of Fraud Scores",
                labels={'fraud_score': 'Fraud Score', 'count': 'Frequency'},
                color_discrete_sequence=['#1f77b4']
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No transactions processed yet. Use the sidebar to add transactions or load sample data.")

    with col2:
        st.subheader("🎯 Latest Features")

        if st.session_state.transactions:
            latest_transaction = st.session_state.transactions[-1]
            user_id = latest_transaction['user_id']
            features = st.session_state.engine.get_features(user_id)

            # Fraud score display
            score = latest_transaction['fraud_score']
            if score > 0.7:
                score_class = "score-high"
                risk_level = "🚨 HIGH RISK"
            elif score > 0.4:
                score_class = "score-medium"
                risk_level = "⚠️ MEDIUM RISK"
            else:
                score_class = "score-low"
                risk_level = "✅ LOW RISK"

            st.markdown(f'<div class="{score_class}">Fraud Score: {score:.3f}</div>', unsafe_allow_html=True)
            st.markdown(f"**Risk Level:** {risk_level}")

            st.divider()

            # Feature breakdown
            st.markdown("**Real-Time Features:**")

            feature_info = {
                "Transaction Velocity (1h)": f"{features.get('transaction_velocity_1h', 0):.1f} transactions",
                "Amount Z-Score": f"{features.get('amount_zscore', 0):.3f}",
                "Location Anomaly": "Yes" if features.get('location_anomaly', 0) > 0 else "No",
                "Time Pattern Score": f"{features.get('time_pattern_score', 0):.3f}",
                "Merchant Diversity": f"{features.get('merchant_diversity', 0):.3f}",
                "Payment Consistency": f"{features.get('payment_method_consistency', 0):.3f}"
            }

            for feature_name, value in feature_info.items():
                st.markdown(f"""
                <div class="feature-card">
                    <strong>{feature_name}:</strong> {value}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Process a transaction to see feature analysis")

    # Footer
    st.divider()
    st.markdown("""
    **System Features:**
    - Real-time feature engineering for fraud detection
    - Memory-safe state management with automatic cleanup
    - 8+ engineered features including velocity, anomaly detection, and behavioral patterns
    - Production-ready scoring algorithm
    """)

def process_transaction(user_id, amount, merchant, location, payment_method):
    """Process a new transaction and update the system state."""
    # Create transaction event
    event = {
        'user_id': user_id,
        'transaction_id': f'txn_{int(time.time() * 1000)}',
        'amount': float(amount),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'merchant': merchant,
        'location': location,
        'payment_method': payment_method
    }

    # Process through engine
    success = st.session_state.engine.process_event(event)

    if success:
        # Get updated features and calculate score
        features = st.session_state.engine.get_features(user_id)

        # Calculate fraud score using same logic as API
        score = (
            features.get('transaction_velocity_1h', 0) * 0.2 +
            features.get('amount_zscore', 0) * 0.25 +
            features.get('location_anomaly', 0) * 0.3 +
            features.get('time_pattern_score', 0) * 0.15 +
            -features.get('merchant_diversity', 0) * 0.05 +
            -features.get('payment_method_consistency', 0) * 0.05
        )

        # Apply sigmoid transformation
        import math
        score = 1 / (1 + math.exp(-score))

        # Store transaction with score
        transaction_record = event.copy()
        transaction_record['fraud_score'] = score
        st.session_state.transactions.append(transaction_record)

        st.success(f"✅ Transaction processed! Fraud Score: {score:.3f}")
    else:
        st.error("❌ Failed to process transaction")

def load_sample_data():
    """Load sample transaction data for demonstration."""
    sample_events = [
        {'user_id': 'user_001', 'amount': 50.0, 'merchant': 'Starbucks', 'location': 'New York', 'payment_method': 'credit_card'},
        {'user_id': 'user_001', 'amount': 25.0, 'merchant': 'Starbucks', 'location': 'New York', 'payment_method': 'credit_card'},
        {'user_id': 'user_001', 'amount': 100.0, 'merchant': 'Amazon', 'location': 'New York', 'payment_method': 'credit_card'},
        {'user_id': 'user_001', 'amount': 500.0, 'merchant': 'Unknown', 'location': 'Los Angeles', 'payment_method': 'credit_card'},  # Suspicious
        {'user_id': 'user_002', 'amount': 75.0, 'merchant': 'Target', 'location': 'Chicago', 'payment_method': 'debit_card'},
        {'user_id': 'user_002', 'amount': 200.0, 'merchant': 'Best Buy', 'location': 'Chicago', 'payment_method': 'debit_card'},
        {'user_id': 'user_002', 'amount': 1500.0, 'merchant': 'Unknown', 'location': 'Miami', 'payment_method': 'paypal'},  # Very suspicious
    ]

    for event_data in sample_events:
        process_transaction(**event_data)
        time.sleep(0.1)  # Small delay for realistic timestamps

    st.success("🎯 Sample data loaded! Check the results.")

def clear_history():
    """Clear all transaction history and reset the engine."""
    st.session_state.transactions = []
    st.session_state.engine = RealTimeFeatureEngine()
    st.success("🗑️ History cleared!")

if __name__ == "__main__":
    main()
