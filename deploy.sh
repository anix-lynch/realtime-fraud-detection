#!/bin/bash
# Distro Dojo - Unified Deployment Script
# Follows: unified deployment + unified asset paths

set -e

echo "🛡️ Distro Dojo - Unified Deployment"
echo "===================================="

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

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker environment verified"

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
    "docker-compose.yml"
    "docker/Dockerfile"
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

# Build and deploy unified services
echo "🏗️ Building unified deployment..."
docker-compose -f docker-compose.yml up --build -d

# Wait for unified services
echo "⏳ Waiting for unified services..."
sleep 15

# Health checks for unified deployment
echo "🔍 Running unified health checks..."

# API Health Check
if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ API service healthy"
else
    echo "❌ API service failed health check"
    exit 1
fi

# UI Health Check
if curl -f -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ UI service available"
else
    echo "❌ UI service failed health check"
fi

echo ""
echo "🎉 DISTRO DOJO DEPLOYMENT COMPLETE!"
echo "==================================="
echo "📊 API Endpoint: http://localhost:8001"
echo "🎨 Web UI: http://localhost:8501"
echo "📋 API Docs: http://localhost:8001/docs"
echo "📱 Streamlit Cloud: https://share.streamlit.io/anix-lynch/realtime-fraud-detection/main/streamlit_app.py"
echo ""
echo "Distro Dojo Commands:"
echo "  docker-compose logs -f          # View unified logs"
echo "  docker-compose down             # Stop unified deployment"
echo "  docker-compose restart          # Restart unified services"
echo "To restart: docker-compose restart"
