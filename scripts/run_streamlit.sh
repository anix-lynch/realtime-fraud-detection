#!/bin/bash

# Run Streamlit UI for fraud detection
cd "$(dirname "$0")/.."

echo "Starting Streamlit UI for Real-Time Fraud Detection..."
echo "Open your browser to: http://localhost:8501"

# Set Python path
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Run Streamlit
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
