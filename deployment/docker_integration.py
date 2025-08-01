#!/usr/bin/env python3
"""
ContainerFlow Visualizer - Docker Integration and Deployment Tools
Deployment utilities for Docker containerization and orchestration

This module provides tools to generate Docker configurations, 
compose files, and deployment scripts for containerized workflows.
"""

import subprocess
import os
import sys
import time
import json
from pathlib import Path


def generate_dockerfile():
    """Generate a Dockerfile for containerized execution"""
    dockerfile_content = """
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python scientific computing packages
RUN pip install --no-cache-dir \\
    numpy \\
    pandas \\
    matplotlib \\
    seaborn \\
    jupyter \\
    pytest \\
    pytest-cov \\
    pytest-html \\
    websockets

# Create application directory
WORKDIR /app

# Copy application files
COPY . .

# Expose required ports
EXPOSE 8080 8765

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the containerflow visualizer
CMD ["python", "container_flow_visualizer.py"]
"""
    
    dockerfile_path = Path("Dockerfile")
    dockerfile_path.write_text(dockerfile_content)
    print("📄 Dockerfile created successfully")
    return dockerfile_path


def generate_docker_compose():
    """Generate docker-compose.yml for service orchestration"""
    compose_content = """
version: '3.8'

services:
  containerflow-visualizer:
    build: .
    container_name: containerflow-visualizer
    ports:
      - "8080:8080"    # HTTP server for web interface
      - "8765:8765"    # WebSocket server for real-time updates
    volumes:
      - ./workflow_results:/app/workflow_results  # Mount results directory
      - ./logs:/app/logs                          # Mount logs directory
    environment:
      - PYTHONUNBUFFERED=1
      - CONTAINERFLOW_HTTP_PORT=8080
      - CONTAINERFLOW_WS_PORT=8765
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/visualizer.html"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - containerflow-network

networks:
  containerflow-network:
    driver: bridge

volumes:
  workflow_results:
    driver: local
  logs:
    driver: local
"""
    
    compose_path = Path("docker-compose.yml")
    compose_path.write_text(compose_content)
    print("📄 docker-compose.yml created successfully")
    return compose_path


def generate_deployment_script():
    """Generate a deployment script for easy startup"""
    script_content = """#!/bin/bash

# ContainerFlow Visualizer Deployment Script
# Professional container execution workflow visualization

set -e

echo "🐳 ContainerFlow Visualizer Deployment"
echo "======================================"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p workflow_results logs

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check docker-compose installation
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and docker-compose are available"

# Build Docker image
echo "🔧 Building ContainerFlow Visualizer image..."
docker-compose build

# Start services
echo "🚀 Starting ContainerFlow Visualizer services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
if curl -s http://localhost:8080/visualizer.html > /dev/null; then
    echo "🟢 ContainerFlow Visualizer is running successfully!"
    echo ""
    echo "📱 Access the web interface:"
    echo "   http://localhost:8080/visualizer.html"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:     docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart:       docker-compose restart"
    echo ""
    
    # Attempt to open browser (optional)
    if command -v xdg-open &> /dev/null; then
        echo "🌐 Opening browser..."
        xdg-open http://localhost:8080/visualizer.html
    elif command -v open &> /dev/null; then
        echo "🌐 Opening browser..."
        open http://localhost:8080/visualizer.html
    fi
    
else
    echo "⚠️ Service may still be starting. Please wait a moment and check:"
    echo "   http://localhost:8080/visualizer.html"
fi

echo ""
echo "🎉 ContainerFlow Visualizer deployment completed!"
"""
    
    script_path = Path("deploy_containerflow.sh")
    script_path.write_text(script_content)
    script_path.chmod(0o755)  # Make executable
    print("📄 deploy_containerflow.sh created successfully")
    return script_path


def generate_advanced_workflow_example():
    """Generate an advanced Docker workflow integration example"""
    workflow_content = """#!/usr/bin/env python3
'''
Advanced ContainerFlow Integration Example
Production-ready workflow with Docker integration and monitoring

This example demonstrates enterprise-level integration patterns
for containerized scientific computing workflows.
'''

import subprocess
import time
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Import ContainerFlow components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import (
    create_visualizer,
    add_workflow_step,
    start_workflow_step, 
    complete_workflow_step,
    log_step_message,
    start_visualization_service
)


class ProductionWorkflowOrchestrator:
    '''Enterprise-grade workflow orchestrator with comprehensive monitoring'''
    
    def __init__(self, workspace_dir="production_workspace"):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(exist_ok=True)
        self.setup_logging()
        
    def setup_logging(self):
        '''Configure structured logging for production environments'''
        log_dir = self.workspace / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "workflow.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ProductionWorkflow")
        
    def step_1_infrastructure_validation(self):
        '''Validate infrastructure and dependencies'''
        step_index = 0
        start_workflow_step(step_index)
        log_step_message(step_index, "🔧 Starting infrastructure validation...")
        
        try:
            # Check Docker daemon
            result = subprocess.run(["docker", "info"], capture_output=True)
            if result.returncode == 0:
                log_step_message(step_index, "✓ Docker daemon is running")
            else:
                log_step_message(step_index, "❌ Docker daemon not accessible", "error")
                return False
                
            # Validate resource availability
            import psutil
            cpu_count = psutil.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
            disk_gb = psutil.disk_usage('/').free / (1024**3)
            
            log_step_message(step_index, f"💻 System resources:")
            log_step_message(step_index, f"   CPU cores: {cpu_count}")
            log_step_message(step_index, f"   Available RAM: {memory_gb:.1f} GB")
            log_step_message(step_index, f"   Free disk space: {disk_gb:.1f} GB")
            
            # Validate network connectivity
            log_step_message(step_index, "🌐 Testing network connectivity...")
            test_urls = ["https://pypi.org", "https://hub.docker.com"]
            for url in test_urls:
                try:
                    import urllib.request
                    urllib.request.urlopen(url, timeout=5)
                    log_step_message(step_index, f"✓ Connection to {url} successful")
                except:
                    log_step_message(step_index, f"⚠️ Connection to {url} failed", "warning")
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, "✅ Infrastructure validation completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Infrastructure validation failed: {str(e)}", "error")
            return False
    
    def step_2_container_orchestration(self):
        '''Orchestrate container deployment and scaling'''
        step_index = 1
        start_workflow_step(step_index)
        log_step_message(step_index, "🐳 Starting container orchestration...")
        
        try:
            # Build application containers
            services = ["data-processor", "ml-trainer", "report-generator"]
            
            for service in services:
                log_step_message(step_index, f"🔨 Building {service} container...")
                # Simulate container build
                for progress in [20, 40, 60, 80, 100]:
                    time.sleep(0.3)
                    log_step_message(step_index, f"   {service} build progress: {progress}%")
                log_step_message(step_index, f"✓ {service} container ready")
            
            # Deploy containers with health checks
            log_step_message(step_index, "🚀 Deploying container stack...")
            time.sleep(2)
            
            # Simulate health checks
            for service in services:
                log_step_message(step_index, f"🔍 Health check: {service}")
                time.sleep(0.5)
                log_step_message(step_index, f"✓ {service} is healthy")
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, "✅ Container orchestration completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Container orchestration failed: {str(e)}", "error")
            return False
    
    def step_3_distributed_processing(self):
        '''Execute distributed data processing'''
        step_index = 2
        start_workflow_step(step_index)
        log_step_message(step_index, "⚡ Starting distributed processing...")
        
        try:
            # Simulate multi-node processing
            processing_nodes = ["node-1", "node-2", "node-3", "node-4"]
            
            for i, node in enumerate(processing_nodes):
                log_step_message(step_index, f"🖥️ Initializing {node}...")
                time.sleep(0.8)
                
                # Simulate workload distribution
                tasks = ["data-validation", "feature-extraction", "model-training", "result-aggregation"]
                for task in tasks:
                    log_step_message(step_index, f"   {node}: executing {task}")
                    time.sleep(0.6)
                
                log_step_message(step_index, f"✓ {node} processing completed")
            
            # Aggregate results
            log_step_message(step_index, "🔄 Aggregating distributed results...")
            time.sleep(2)
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, "✅ Distributed processing completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Distributed processing failed: {str(e)}", "error")
            return False
    
    def step_4_quality_assurance_pipeline(self):
        '''Comprehensive quality assurance and testing'''
        step_index = 3
        start_workflow_step(step_index)
        log_step_message(step_index, "🛡️ Starting quality assurance pipeline...")
        
        try:
            # Security scanning
            log_step_message(step_index, "🔒 Running security scans...")
            security_checks = ["dependency-scan", "vulnerability-assessment", "compliance-check"]
            for check in security_checks:
                log_step_message(step_index, f"   Executing {check}...")
                time.sleep(1)
                log_step_message(step_index, f"✓ {check} passed")
            
            # Performance benchmarking
            log_step_message(step_index, "⚡ Performance benchmarking...")
            benchmarks = ["throughput-test", "latency-test", "resource-usage-test"]
            for benchmark in benchmarks:
                log_step_message(step_index, f"   Running {benchmark}...")
                time.sleep(1.2)
                # Simulate benchmark results
                import random
                result = random.uniform(85, 98)
                log_step_message(step_index, f"✓ {benchmark}: {result:.1f}% optimal")
            
            # Integration testing
            log_step_message(step_index, "🔗 Integration testing...")
            time.sleep(1.5)
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, "✅ Quality assurance pipeline completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Quality assurance failed: {str(e)}", "error")
            return False
    
    def step_5_deployment_and_monitoring(self):
        '''Production deployment with monitoring setup'''
        step_index = 4
        start_workflow_step(step_index)
        log_step_message(step_index, "🎯 Starting production deployment...")
        
        try:
            # Deploy to production environment
            log_step_message(step_index, "🚀 Deploying to production...")
            time.sleep(2)
            
            # Setup monitoring and alerting
            monitoring_components = [
                "metrics-collector", "log-aggregator", 
                "alert-manager", "dashboard-service"
            ]
            
            for component in monitoring_components:
                log_step_message(step_index, f"📊 Setting up {component}...")
                time.sleep(0.8)
                log_step_message(step_index, f"✓ {component} configured")
            
            # Generate comprehensive deployment report
            report_path = self.workspace / "production_deployment_report.json"
            deployment_report = {
                "deployment_id": f"deploy-{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "components": monitoring_components,
                "metrics": {
                    "deployment_duration": "4.2 minutes",
                    "services_deployed": 7,
                    "health_score": "98.5%"
                }
            }
            
            with open(report_path, 'w') as f:
                json.dump(deployment_report, f, indent=2)
            
            log_step_message(step_index, f"📄 Deployment report: {report_path}")
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, "🎉 Production deployment completed successfully!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Production deployment failed: {str(e)}", "error")
            return False
    
    def execute_production_workflow(self):
        '''Execute the complete production workflow'''
        workflow_steps = [
            self.step_1_infrastructure_validation,
            self.step_2_container_orchestration,
            self.step_3_distributed_processing,
            self.step_4_quality_assurance_pipeline,
            self.step_5_deployment_and_monitoring
        ]
        
        self.logger.info("Starting production workflow execution")
        log_step_message(0, "🚀 Initiating production workflow...", "info")
        
        start_time = time.time()
        
        for step_func in workflow_steps:
            if not step_func():
                self.logger.error("Workflow failed at step")
                log_step_message(0, "⚠️ Production workflow halted due to step failure", "error")
                return False
            time.sleep(0.5)
        
        execution_time = time.time() - start_time
        self.logger.info(f"Production workflow completed in {execution_time:.1f} seconds")
        log_step_message(4, f"🎊 Production workflow completed in {execution_time:.1f}s!", "success")
        return True


def main():
    '''Main function for production workflow demonstration'''
    print("🏭 ContainerFlow Production Workflow Orchestrator")
    print("=" * 60)
    
    # Initialize visualizer
    visualizer = create_visualizer(
        http_port=8080,
        websocket_port=8765,
        web_interface_dir="../web_interface"
    )
    
    # Define production workflow steps
    production_steps = [
        ("Infrastructure Validation", "Validate system resources and dependencies"),
        ("Container Orchestration", "Deploy and scale containerized services"),
        ("Distributed Processing", "Execute distributed data processing tasks"),
        ("Quality Assurance", "Run comprehensive testing and security scans"),
        ("Production Deployment", "Deploy to production with monitoring")
    ]
    
    # Configure workflow steps
    for step_name, step_description in production_steps:
        add_workflow_step(step_name, step_description)
    
    print("📋 Production workflow configured:")
    for i, (name, desc) in enumerate(production_steps):
        print(f"   {i+1}. {name}")
    
    print(f"\\n🌐 Monitor at: http://localhost:8080/visualizer.html")
    print("📊 Enterprise-grade monitoring and logging enabled")
    print("⏳ Production workflow will start in 3 seconds...\\n")
    
    # Create orchestrator
    orchestrator = ProductionWorkflowOrchestrator()
    
    # Execute in background thread
    def delayed_execution():
        time.sleep(3)
        orchestrator.execute_production_workflow()
    
    import threading
    workflow_thread = threading.Thread(target=delayed_execution, daemon=True)
    workflow_thread.start()
    
    # Start visualization service
    start_visualization_service()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n🛑 Production workflow orchestrator stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\\n❌ Critical error: {e}")
        sys.exit(1)
"""
    
    workflow_path = Path("deployment/production_workflow_example.py")
    workflow_path.parent.mkdir(exist_ok=True)
    workflow_path.write_text(workflow_content)
    print("📄 production_workflow_example.py created successfully")
    return workflow_path


def create_complete_deployment_package():
    """Create a complete deployment package with all necessary files"""
    print("📦 Creating complete ContainerFlow deployment package...")
    
    # Create deployment directory structure
    deployment_dir = Path("deployment")
    deployment_dir.mkdir(exist_ok=True)
    
    # Generate all deployment files
    generated_files = []
    
    try:
        generated_files.append(generate_dockerfile())
        generated_files.append(generate_docker_compose())
        generated_files.append(generate_deployment_script())
        generated_files.append(generate_advanced_workflow_example())
        
        print("\\n✅ Complete deployment package created successfully!")
        print("\\n📋 Generated files:")
        for file_path in generated_files:
            print(f"  ✓ {file_path}")
        
        print("\\n🚀 Quick start:")
        print("1. Run: chmod +x deploy_containerflow.sh")
        print("2. Execute: ./deploy_containerflow.sh")
        print("3. Access: http://localhost:8080/visualizer.html")
        print("4. Stop: docker-compose down")
        
        return generated_files
        
    except Exception as e:
        print(f"❌ Error creating deployment package: {e}")
        return []


if __name__ == "__main__":
    create_complete_deployment_package()