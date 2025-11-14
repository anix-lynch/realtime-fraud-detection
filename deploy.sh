#!/bin/bash
# Unified deployment script for Real-Time Fraud Detection
# Follows Distro Dojo: unified deployment + unified asset paths

set -e

echo "🛡️ Starting Unified Deployment - Real-Time Fraud Detection"
echo "========================================================="

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker environment verified"

# Create necessary directories
echo "📁 Setting up unified asset paths..."
mkdir -p logs
mkdir -p data
mkdir -p models

# Build and start services
echo "🏗️ Building and deploying services..."
docker-compose -f docker-compose.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check API health
echo "🔍 Checking API health..."
if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ API service is healthy"
else
    echo "❌ API service health check failed"
    exit 1
fi

# Check UI availability
echo "🔍 Checking UI availability..."
if curl -f -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ UI service is available"
else
    echo "❌ UI service check failed"
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo "📊 API Endpoint: http://localhost:8001"
echo "🎨 Web UI: http://localhost:8501"
echo "📋 API Docs: http://localhost:8001/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "To restart: docker-compose restart"
