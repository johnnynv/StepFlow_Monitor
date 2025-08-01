#!/bin/bash
# StepFlow Monitor Quick Start Script

set -e

echo "🔍 StepFlow Monitor - Quick Start"
echo "========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Default configuration
HTTP_PORT=${HTTP_PORT:-8080}
WS_PORT=${WS_PORT:-8765}
STORAGE_DIR=${STORAGE_DIR:-$(pwd)/storage}
SCRIPTS_DIR=${SCRIPTS_DIR:-$(pwd)/examples}

echo "📋 Configuration:"
echo "   HTTP Port: $HTTP_PORT"
echo "   WebSocket Port: $WS_PORT" 
echo "   Storage Directory: $STORAGE_DIR"
echo "   Scripts Directory: $SCRIPTS_DIR"
echo ""

# Create directories if they don't exist
mkdir -p "$STORAGE_DIR"/{executions,artifacts,database}
mkdir -p "$SCRIPTS_DIR"

# Check if container is already running
if docker ps --format "table {{.Names}}" | grep -q "stepflow"; then
    echo "⚠️  StepFlow Monitor is already running."
    echo "   To restart: docker restart stepflow"
    echo "   To stop: docker stop stepflow"
    echo "   To view logs: docker logs -f stepflow"
    echo ""
    echo "🌐 Access at: http://localhost:$HTTP_PORT"
    exit 0
fi

# Build or pull image
if [ "$1" = "--build" ]; then
    echo "🔨 Building StepFlow Monitor image..."
    docker build -t stepflow/monitor .
else
    echo "📥 Pulling StepFlow Monitor image..."
    # docker pull stepflow/monitor
    # For now, build locally since image is not published
    echo "🔨 Building StepFlow Monitor image locally..."
    docker build -t stepflow/monitor .
fi

echo ""
echo "🚀 Starting StepFlow Monitor Visualizer..."

# Run container
docker run -d \
    --name stepflow \
    -p "$HTTP_PORT:8080" \
    -p "$WS_PORT:8765" \
    -v "$STORAGE_DIR:/app/storage" \
    -v "$SCRIPTS_DIR:/workspace" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e PYTHONUNBUFFERED=1 \
    -e STEPFLOW_LOG_LEVEL=INFO \
    -e STEPFLOW_AUTH_ENABLED=false \
    --restart unless-stopped \
    stepflow/monitor

# Wait for container to start
echo "⏳ Waiting for service to start..."
sleep 5

# Health check
if curl -f -s "http://localhost:$HTTP_PORT/api/health" > /dev/null; then
    echo "✅ StepFlow Monitor Visualizer is running!"
    echo ""
    echo "🌐 Dashboard: http://localhost:$HTTP_PORT"
    echo "🔗 WebSocket: ws://localhost:$WS_PORT"
    echo "📁 Storage: $STORAGE_DIR"
    echo "📂 Scripts: $SCRIPTS_DIR"
    echo ""
    echo "📋 Quick Commands:"
    echo "   View logs: docker logs -f stepflow"
    echo "   Stop: docker stop stepflow"
    echo "   Restart: docker restart stepflow"
    echo "   Remove: docker rm -f stepflow"
    echo ""
    echo "📚 Try the examples:"
    echo "   1. Open http://localhost:$HTTP_PORT"
    echo "   2. Click 'New Execution'"
    echo "   3. Run: bash /workspace/shell_example.sh"
    echo "   4. Watch the real-time visualization!"
else
    echo "❌ Failed to start StepFlow Monitor Visualizer"
    echo "📋 Check logs: docker logs stepflow"
    exit 1
fi