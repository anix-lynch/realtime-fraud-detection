#!/bin/bash

# Run the test suite
cd "$(dirname "$0")/.."

echo "Running test suite..."

# Set Python path
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Run pytest with verbose output
python -m pytest tests/ -v --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Some tests failed!"
    exit 1
fi
