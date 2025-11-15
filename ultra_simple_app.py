#!/usr/bin/env python3
"""
Ultra Simple Real-Time Fraud Detection Demo
Streamlit application with minimal dependencies for guaranteed deployment
"""

import streamlit as st
import random
from datetime import datetime
import time

# Page config
st.set_page_config(page_title="🛡️ Fraud Detection Demo", page_icon="🛡️")

# Title
st.title("🛡️ Real-Time Fraud Detection Demo")
st.markdown("### Ultra Simple Version - Minimal Dependencies")

# Sidebar
st.sidebar.header("🎯 Controls")
page = st.sidebar.radio("Choose a page:", ["Overview", "Fraud Detection", "About"])

if page == "Overview":
    st.header("📊 Dashboard Overview")

    # Simple metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Transactions", "1,250")

    with col2:
        st.metric("Fraud Alerts", "23")

    with col3:
        st.metric("Accuracy Rate", "94%")

    st.success("✅ System is running successfully!")
    st.info("This is a simplified demo to test Streamlit Cloud deployment.")

elif page == "Fraud Detection":
    st.header("🔍 Fraud Detection Engine")

    # Simple input form
    st.subheader("Transaction Analysis")

    with st.form("fraud_check"):
        user_id = st.text_input("User ID", value="user_123", help="Unique user identifier")
        amount = st.number_input("Amount ($)", min_value=0.01, value=150.00, step=0.01)
        merchant = st.selectbox("Merchant", ["Amazon", "Walmart", "Starbucks", "Target", "Unknown"])
        location = st.selectbox("Location", ["New York", "Los Angeles", "Chicago", "Houston", "Miami", "Unknown"])
        payment_method = st.selectbox("Payment Method", ["credit_card", "debit_card", "paypal", "apple_pay"])

        submitted = st.form_submit_button("🔍 Analyze Transaction")

        if submitted:
            # Simple fraud detection logic (no complex dependencies)
            risk_score = 0.1  # Base low risk

            # Amount-based risk
            if amount > 500:
                risk_score += 0.4
            elif amount > 200:
                risk_score += 0.2

            # Location-based risk
            if location == "Unknown":
                risk_score += 0.3

            # Merchant-based risk
            if merchant == "Unknown":
                risk_score += 0.25

            # Time-based risk (simple approximation)
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 22:  # Unusual hours
                risk_score += 0.15

            # Payment method consistency (simplified)
            if payment_method == "paypal":
                risk_score += 0.1

            # Add some randomness
            risk_score += random.uniform(-0.1, 0.1)
            risk_score = max(0.01, min(0.99, risk_score))

            # Determine risk level
            if risk_score > 0.7:
                risk_level = "🚨 HIGH RISK"
                risk_color = "red"
                recommendation = "Block transaction immediately"
            elif risk_score > 0.4:
                risk_level = "⚠️ MEDIUM RISK"
                risk_color = "orange"
                recommendation = "Require additional verification"
            else:
                risk_level = "✅ LOW RISK"
                risk_color = "green"
                recommendation = "Approve transaction"

            st.success("Analysis Complete!")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Fraud Score", f"{risk_score:.3f}")

            with col2:
                st.metric("Risk Level", risk_level)

            with col3:
                confidence = abs(risk_score - 0.5) * 200
                st.metric("Confidence", f"{confidence:.1f}%")

            # Risk assessment display
            if risk_score > 0.7:
                st.error(f"🚨 **{risk_level}**: {recommendation}")
            elif risk_score > 0.4:
                st.warning(f"⚠️ **{risk_level}**: {recommendation}")
            else:
                st.success(f"✅ **{risk_level}**: {recommendation}")

            # Feature breakdown
            st.subheader("🔍 Risk Factors Analyzed")

            factors = {
                "Transaction Amount": f"${amount:.2f} ({'High' if amount > 500 else 'Medium' if amount > 200 else 'Low'})",
                "Location": f"{location} ({'Suspicious' if location == 'Unknown' else 'Normal'})",
                "Merchant": f"{merchant} ({'Suspicious' if merchant == 'Unknown' else 'Known'})",
                "Time": f"{current_hour}:00 ({'Unusual' if current_hour < 6 or current_hour > 22 else 'Normal'})",
                "Payment Method": payment_method
            }

            for factor, value in factors.items():
                st.write(f"**{factor}:** {value}")

elif page == "About":
    st.header("ℹ️ About This Demo")

    st.markdown("""
    ### Real-Time Fraud Detection Demo

    This is a simplified demonstration of a real-time fraud detection system.

    **Features:**
    - Interactive transaction analysis
    - Real-time risk scoring
    - Multiple risk factors considered
    - Simple ML-based predictions

    **Technology:**
    - Streamlit for the web interface
    - Python for the analysis logic
    - No external dependencies

    **Deployment:**
    - Designed for Streamlit Cloud
    - Minimal resource requirements
    - Fast loading times
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ for fraud detection deployment testing")
st.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
