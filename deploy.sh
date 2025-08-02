#!/bin/bash

# StepFlow Monitor - One-Click Deployment Script
# Compatible with both Docker and Podman

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect container runtime
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    # Try podman compose first, fallback to podman-compose
    if podman compose --help &> /dev/null; then
        COMPOSE_CMD="podman compose"
    fi
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker-compose"
    # Try docker compose first, fallback to docker-compose
    if docker compose --help &> /dev/null; then
        COMPOSE_CMD="docker compose"
    fi
else
    echo -e "${RED}❌ Neither Docker nor Podman found. Please install one of them.${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 StepFlow Monitor - One-Click Deployment${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}📋 Using container runtime: ${CONTAINER_CMD}${NC}"
echo -e "${GREEN}📋 Using compose command: ${COMPOSE_CMD}${NC}"
echo ""

# Function to check if service is running
check_service() {
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}🔍 Waiting for StepFlow Monitor to start...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ StepFlow Monitor is running!${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ Service failed to start within 60 seconds${NC}"
    return 1
}

# Main deployment function
deploy() {
    echo -e "${YELLOW}📦 Building and starting StepFlow Monitor...${NC}"
    
    # Stop any existing containers
    $COMPOSE_CMD down 2>/dev/null || true
    
    # Build and start services
    $COMPOSE_CMD up --build -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Container started successfully${NC}"
        
        # Check if service is ready
        if check_service; then
            echo ""
            echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${BLUE}📊 StepFlow Monitor Dashboard: ${YELLOW}http://localhost:8080/${NC}"
            echo -e "${BLUE}📋 Execution History: ${YELLOW}http://localhost:8080/history${NC}"
            echo -e "${BLUE}🔧 API Health Check: ${YELLOW}http://localhost:8080/api/health${NC}"
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${BLUE}📝 Useful commands:${NC}"
            echo -e "  • View logs: ${YELLOW}$COMPOSE_CMD logs -f${NC}"
            echo -e "  • Stop service: ${YELLOW}$COMPOSE_CMD down${NC}"
            echo -e "  • Restart service: ${YELLOW}$COMPOSE_CMD restart${NC}"
            echo -e "  • View status: ${YELLOW}$COMPOSE_CMD ps${NC}"
            echo ""
        else
            echo -e "${RED}❌ Service health check failed${NC}"
            echo -e "${YELLOW}📋 Checking logs...${NC}"
            $COMPOSE_CMD logs stepflow-monitor
            exit 1
        fi
    else
        echo -e "${RED}❌ Failed to start container${NC}"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy"|"start"|"up")
        deploy
        ;;
    "stop"|"down")
        echo -e "${YELLOW}🛑 Stopping StepFlow Monitor...${NC}"
        $COMPOSE_CMD down
        echo -e "${GREEN}✅ StepFlow Monitor stopped${NC}"
        ;;
    "restart")
        echo -e "${YELLOW}🔄 Restarting StepFlow Monitor...${NC}"
        $COMPOSE_CMD restart
        check_service && echo -e "${GREEN}✅ StepFlow Monitor restarted${NC}"
        ;;
    "logs")
        $COMPOSE_CMD logs -f stepflow-monitor
        ;;
    "status")
        $COMPOSE_CMD ps
        echo ""
        echo -e "${BLUE}🔍 Health Check:${NC}"
        if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Service is healthy${NC}"
        else
            echo -e "${RED}❌ Service is not responding${NC}"
        fi
        ;;
    "clean")
        echo -e "${YELLOW}🧹 Cleaning up StepFlow Monitor...${NC}"
        $COMPOSE_CMD down -v --rmi all
        echo -e "${GREEN}✅ Cleanup completed${NC}"
        ;;
    "help"|"-h"|"--help")
        echo -e "${BLUE}StepFlow Monitor Deployment Script${NC}"
        echo ""
        echo -e "${YELLOW}Usage:${NC}"
        echo -e "  ./deploy.sh [command]"
        echo ""
        echo -e "${YELLOW}Commands:${NC}"
        echo -e "  deploy, start, up    Deploy and start StepFlow Monitor (default)"
        echo -e "  stop, down          Stop StepFlow Monitor"
        echo -e "  restart             Restart StepFlow Monitor"
        echo -e "  logs                View real-time logs"
        echo -e "  status              Check service status"
        echo -e "  clean               Stop and remove all containers, volumes, and images"
        echo -e "  help                Show this help message"
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo -e "${YELLOW}Run './deploy.sh help' for available commands${NC}"
        exit 1
        ;;
esac