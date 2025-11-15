#!/bin/bash
# Distro Dojo - Local Unified Deployment (No Docker)
# For environments without Docker daemon

set -e

echo "🛡️ Distro Dojo - Local Unified Deployment"
echo "=========================================="

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Load unified configuration
CONFIG_FILE="deploy/config.toml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Unified config not found: $CONFIG_FILE"
    exit 1
fi

echo "✅ Loaded unified deployment config"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

# Setup unified asset paths
echo "📁 Setting up unified asset paths..."
mkdir -p logs
mkdir -p data
mkdir -p models

# Verify all required files exist (unified asset check)
REQUIRED_FILES=(
    "src/streaming_features.py"
    "src/api.py"
    "streamlit_app.py"
    "requirements.txt"
    "deploy/config.toml"
)

echo "🔍 Verifying unified asset paths..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing unified asset: $file"
        exit 1
    fi
done
echo "✅ All unified assets present"

# Install dependencies if needed
echo "📦 Installing unified dependencies..."
pip install -r requirements.txt --quiet || echo "⚠️  Some dependencies may need manual installation"

echo ""
echo "🎉 DISTRO DOJO LOCAL DEPLOYMENT READY!"
echo "======================================="
echo "Run these commands in separate terminals:"
echo ""
echo "API Server:"
echo "  export PYTHONPATH=\"\$PWD/src:\$PYTHONPATH\" && uvicorn src.api:app --host 0.0.0.0 --port 8001 --reload"
echo ""
echo "Streamlit UI:"
echo "  export PYTHONPATH=\"\$PWD/src:\$PYTHONPATH\" && streamlit run streamlit_app.py --server.port 8501"
echo ""
echo "Demo:"
echo "  python demo.py"
echo ""
echo "Test:"
echo "  export PYTHONPATH=\"\$PWD/src:\$PYTHONPATH\" && python -m pytest tests/ -v"
echo ""
echo "📊 API Endpoint: http://localhost:8001"
echo "🎨 Web UI: http://localhost:8501"
echo "📋 API Docs: http://localhost:8001/docs"
echo "📱 Streamlit Cloud: https://share.streamlit.io/anix-lynch/realtime-fraud-detection/main/streamlit_app.py"
