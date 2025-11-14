#!/bin/bash

# Run the fraud detection API locally
cd "$(dirname "$0")/.."

echo "Starting Fraud Detection API on http://localhost:8001"
echo "Health check: http://localhost:8001/health"
echo "API docs: http://localhost:8001/docs"

# Set Python path
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Run with uvicorn
uvicorn src.api:app --host 0.0.0.0 --port 8001 --reload
