# 🎯 ContainerFlow Visualizer Examples Guide

## Complete Examples and Use Cases

This guide provides comprehensive examples for different use cases and integration scenarios.

## 📋 Table of Contents

1. [Basic Integration](#basic-integration)
2. [Scientific Workflow](#scientific-workflow)
3. [CI/CD Pipeline](#cicd-pipeline)
4. [Docker Multi-Stage Build](#docker-multi-stage-build)
5. [Data Processing Pipeline](#data-processing-pipeline)
6. [ML Training Workflow](#ml-training-workflow)
7. [Kubernetes Job Monitoring](#kubernetes-job-monitoring)
8. [Custom Integration Patterns](#custom-integration-patterns)

## 🚀 Basic Integration

### Simple Script Monitoring

```python
#!/usr/bin/env python3
"""Simple script with visualization"""

import time
import sys
import os

# Add core to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import *

def basic_workflow():
    """Basic workflow example"""
    
    # Initialize visualizer
    create_visualizer(http_port=8080, websocket_port=8765)
    
    # Define steps
    add_workflow_step("Initialize", "Setting up environment")
    add_workflow_step("Process", "Main processing task")
    add_workflow_step("Finalize", "Cleanup and results")
    
    print("🌐 Monitor at: http://localhost:8080/visualizer.html")
    
    # Execute workflow
    def execute():
        time.sleep(2)  # Allow browser opening
        
        # Step 1: Initialize
        start_workflow_step(0)
        log_step_message(0, "Initializing system...")
        time.sleep(2)
        log_step_message(0, "System ready!", "success")
        complete_workflow_step(0)
        
        # Step 2: Process
        start_workflow_step(1)
        log_step_message(1, "Starting main processing...")
        for i in range(5):
            time.sleep(1)
            log_step_message(1, f"Processing item {i+1}/5...")
        log_step_message(1, "Processing completed!", "success")
        complete_workflow_step(1)
        
        # Step 3: Finalize
        start_workflow_step(2)
        log_step_message(2, "Cleaning up...")
        time.sleep(1)
        log_step_message(2, "Generating reports...")
        time.sleep(1)
        log_step_message(2, "Workflow completed!", "success")
        complete_workflow_step(2)
    
    import threading
    threading.Thread(target=execute, daemon=True).start()
    start_visualization_service()

if __name__ == "__main__":
    basic_workflow()
```

## 🔬 Scientific Workflow

### Research Data Pipeline

```python
#!/usr/bin/env python3
"""Scientific research data processing pipeline"""

import time
import random
import json
import os
from datetime import datetime
from pathlib import Path

from core import *

class ResearchPipeline:
    """Scientific research data processing pipeline"""
    
    def __init__(self, project_name="research_project"):
        self.project_name = project_name
        self.workspace = Path(f"workspace_{project_name}")
        self.workspace.mkdir(exist_ok=True)
        
        # Initialize visualizer
        create_visualizer()
        
        # Define research workflow steps
        self.define_workflow_steps()
    
    def define_workflow_steps(self):
        """Define the research workflow steps"""
        steps = [
            ("Data Collection", "Gather research data from multiple sources"),
            ("Data Validation", "Validate data quality and completeness"),
            ("Preprocessing", "Clean and transform raw data"),
            ("Analysis", "Perform statistical and computational analysis"),
            ("Visualization", "Generate plots and visualizations"),
            ("Model Training", "Train machine learning models"),
            ("Evaluation", "Evaluate model performance"),
            ("Report Generation", "Generate research report and findings")
        ]
        
        for step_name, description in steps:
            add_workflow_step(step_name, description)
    
    def step_1_data_collection(self):
        """Step 1: Collect research data"""
        step_idx = 0
        start_workflow_step(step_idx)
        log_step_message(step_idx, "🔍 Starting data collection...")
        
        try:
            # Simulate data collection from multiple sources
            data_sources = [
                {"name": "Public Dataset A", "records": 10000, "format": "CSV"},
                {"name": "Sensor Data B", "records": 50000, "format": "JSON"},
                {"name": "Survey Data C", "records": 2500, "format": "Excel"},
                {"name": "External API D", "records": 15000, "format": "JSON"}
            ]
            
            collected_data = []
            
            for source in data_sources:
                log_step_message(step_idx, f"📥 Collecting from {source['name']}...")
                
                # Simulate collection time based on data size
                collection_time = source['records'] / 10000
                time.sleep(collection_time)
                
                # Simulate success rate
                if random.random() > 0.1:  # 90% success rate
                    collected_data.append(source)
                    log_step_message(step_idx, f"✓ Collected {source['records']} records from {source['name']}")
                else:
                    log_step_message(step_idx, f"⚠️ Failed to collect from {source['name']}", "warning")
            
            # Save collection metadata
            metadata = {
                "collection_timestamp": datetime.now().isoformat(),
                "sources": collected_data,
                "total_records": sum(s['records'] for s in collected_data)
            }
            
            with open(self.workspace / "collection_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            log_step_message(step_idx, f"📊 Total records collected: {metadata['total_records']}")
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Data collection completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Data collection failed: {str(e)}", "error")
            return False
    
    def step_2_data_validation(self):
        """Step 2: Validate collected data"""
        step_idx = 1
        start_workflow_step(step_idx)
        log_step_message(step_idx, "🔍 Starting data validation...")
        
        try:
            validation_checks = [
                "Schema validation",
                "Data type consistency",
                "Missing value analysis",
                "Outlier detection",
                "Duplicate record check",
                "Referential integrity"
            ]
            
            validation_results = {}
            
            for check in validation_checks:
                log_step_message(step_idx, f"🔍 Running {check}...")
                time.sleep(0.8)
                
                # Simulate validation results
                success_rate = random.uniform(0.85, 0.98)
                validation_results[check] = {
                    "status": "passed" if success_rate > 0.9 else "warning",
                    "score": success_rate,
                    "details": f"{success_rate*100:.1f}% of records passed"
                }
                
                if success_rate > 0.9:
                    log_step_message(step_idx, f"✓ {check}: {success_rate*100:.1f}% passed")
                else:
                    log_step_message(step_idx, f"⚠️ {check}: {success_rate*100:.1f}% passed", "warning")
            
            # Generate validation report
            avg_score = sum(r['score'] for r in validation_results.values()) / len(validation_results)
            log_step_message(step_idx, f"📊 Overall validation score: {avg_score*100:.1f}%")
            
            # Save validation results
            with open(self.workspace / "validation_results.json", 'w') as f:
                json.dump(validation_results, f, indent=2)
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Data validation completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Data validation failed: {str(e)}", "error")
            return False
    
    def step_3_preprocessing(self):
        """Step 3: Preprocess and clean data"""
        step_idx = 2
        start_workflow_step(step_idx)
        log_step_message(step_idx, "🛠️ Starting data preprocessing...")
        
        try:
            preprocessing_tasks = [
                ("Data cleaning", "Remove invalid and duplicate records"),
                ("Normalization", "Normalize numerical features"),
                ("Feature engineering", "Create derived features"),
                ("Data transformation", "Apply necessary transformations"),
                ("Feature selection", "Select relevant features"),
                ("Data splitting", "Split into train/test sets")
            ]
            
            for i, (task, description) in enumerate(preprocessing_tasks):
                log_step_message(step_idx, f"⚙️ {task}: {description}")
                
                # Simulate processing time
                time.sleep(random.uniform(0.8, 1.5))
                
                # Simulate progress
                progress = ((i + 1) / len(preprocessing_tasks)) * 100
                log_step_message(step_idx, f"   Progress: {progress:.0f}%")
                
                log_step_message(step_idx, f"✓ {task} completed")
            
            # Generate preprocessing summary
            preprocessing_summary = {
                "timestamp": datetime.now().isoformat(),
                "tasks_completed": len(preprocessing_tasks),
                "output_datasets": {
                    "training_set": {"records": 45000, "features": 25},
                    "test_set": {"records": 15000, "features": 25},
                    "validation_set": {"records": 10000, "features": 25}
                }
            }
            
            with open(self.workspace / "preprocessing_summary.json", 'w') as f:
                json.dump(preprocessing_summary, f, indent=2)
            
            log_step_message(step_idx, "📊 Preprocessing summary:")
            for dataset, info in preprocessing_summary["output_datasets"].items():
                log_step_message(step_idx, f"   {dataset}: {info['records']} records, {info['features']} features")
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Data preprocessing completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Data preprocessing failed: {str(e)}", "error")
            return False
    
    def execute_research_workflow(self):
        """Execute the complete research workflow"""
        log_step_message(0, f"🚀 Starting research project: {self.project_name}", "info")
        
        workflow_steps = [
            self.step_1_data_collection,
            self.step_2_data_validation,
            self.step_3_preprocessing,
            # Add more steps as needed
        ]
        
        for step_func in workflow_steps:
            if not step_func():
                log_step_message(0, "⚠️ Research workflow stopped due to step failure", "warning")
                return False
            time.sleep(0.5)
        
        log_step_message(len(workflow_steps)-1, "🎉 Research workflow completed successfully!", "success")
        return True

def main():
    """Main function for research pipeline"""
    print("🔬 Scientific Research Pipeline Visualizer")
    print("=" * 50)
    
    # Create pipeline
    pipeline = ResearchPipeline("genomics_analysis")
    
    print("📋 Research workflow configured")
    print("🌐 Monitor at: http://localhost:8080/visualizer.html")
    print("⏳ Research workflow will start in 3 seconds...")
    
    # Execute in background
    def delayed_execution():
        time.sleep(3)
        pipeline.execute_research_workflow()
    
    import threading
    threading.Thread(target=delayed_execution, daemon=True).start()
    
    # Start visualization
    start_visualization_service()

if __name__ == "__main__":
    main()
```

## 🏗️ CI/CD Pipeline

### Continuous Integration Workflow

```python
#!/usr/bin/env python3
"""CI/CD Pipeline with ContainerFlow Visualization"""

import subprocess
import time
import os
import json
from pathlib import Path

from core import *

class CIPipeline:
    """Continuous Integration Pipeline"""
    
    def __init__(self, repo_name="my-project"):
        self.repo_name = repo_name
        self.build_dir = Path("build")
        self.build_dir.mkdir(exist_ok=True)
        
        create_visualizer()
        self.setup_pipeline_steps()
    
    def setup_pipeline_steps(self):
        """Setup CI/CD pipeline steps"""
        steps = [
            ("Source Checkout", "Clone repository and checkout branch"),
            ("Dependency Installation", "Install project dependencies"),
            ("Code Quality", "Run linting and code quality checks"),
            ("Unit Tests", "Execute unit test suite"),
            ("Integration Tests", "Run integration tests"),
            ("Build Artifacts", "Build and package application"),
            ("Security Scan", "Run security vulnerability scan"),
            ("Deployment", "Deploy to staging environment")
        ]
        
        for step_name, description in steps:
            add_workflow_step(step_name, description)
    
    def step_1_source_checkout(self):
        """Step 1: Source code checkout"""
        step_idx = 0
        start_workflow_step(step_idx)
        log_step_message(step_idx, "📥 Starting source checkout...")
        
        try:
            # Simulate git operations
            log_step_message(step_idx, "🔍 Fetching latest changes...")
            time.sleep(1)
            
            log_step_message(step_idx, "📋 Checking out branch: main")
            time.sleep(0.5)
            
            log_step_message(step_idx, "🏷️ Commit: abc123def (feat: add new feature)")
            log_step_message(step_idx, "👤 Author: developer@company.com")
            
            # Simulate submodule updates
            log_step_message(step_idx, "📦 Updating submodules...")
            time.sleep(0.8)
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Source checkout completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Source checkout failed: {str(e)}", "error")
            return False
    
    def step_2_dependency_installation(self):
        """Step 2: Install dependencies"""
        step_idx = 1
        start_workflow_step(step_idx)
        log_step_message(step_idx, "📦 Installing dependencies...")
        
        try:
            # Simulate different package managers
            package_managers = [
                ("npm", "package.json", "Installing Node.js dependencies"),
                ("pip", "requirements.txt", "Installing Python dependencies"),
                ("maven", "pom.xml", "Installing Java dependencies")
            ]
            
            for pm, config_file, description in package_managers:
                if Path(config_file).exists() or True:  # Simulate file existence
                    log_step_message(step_idx, f"📋 {description}...")
                    log_step_message(step_idx, f"   Using {pm} with {config_file}")
                    
                    # Simulate installation time
                    time.sleep(random.uniform(1, 2))
                    
                    # Simulate package installation logs
                    packages = ["package-a", "package-b", "package-c"]
                    for pkg in packages:
                        log_step_message(step_idx, f"   Installing {pkg}...")
                        time.sleep(0.3)
                    
                    log_step_message(step_idx, f"✓ {pm} dependencies installed")
            
            # Cache information
            log_step_message(step_idx, "💾 Updating dependency cache...")
            time.sleep(0.5)
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Dependencies installed successfully!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Dependency installation failed: {str(e)}", "error")
            return False
    
    def step_3_code_quality(self):
        """Step 3: Code quality checks"""
        step_idx = 2
        start_workflow_step(step_idx)
        log_step_message(step_idx, "🔍 Running code quality checks...")
        
        try:
            quality_tools = [
                ("ESLint", "JavaScript/TypeScript linting"),
                ("Pylint", "Python code analysis"),
                ("SonarQube", "Code quality and security analysis"),
                ("Prettier", "Code formatting check")
            ]
            
            quality_results = {}
            
            for tool, description in quality_tools:
                log_step_message(step_idx, f"🔍 Running {tool}: {description}")
                time.sleep(random.uniform(0.8, 1.5))
                
                # Simulate quality scores
                score = random.uniform(7.5, 9.8)
                issues = random.randint(0, 15)
                
                quality_results[tool] = {"score": score, "issues": issues}
                
                if score >= 8.0 and issues <= 5:
                    log_step_message(step_idx, f"✓ {tool}: Score {score:.1f}/10, {issues} issues")
                elif score >= 7.0:
                    log_step_message(step_idx, f"⚠️ {tool}: Score {score:.1f}/10, {issues} issues", "warning")
                else:
                    log_step_message(step_idx, f"❌ {tool}: Score {score:.1f}/10, {issues} issues", "error")
                    return False
            
            # Overall quality summary
            avg_score = sum(r['score'] for r in quality_results.values()) / len(quality_results)
            total_issues = sum(r['issues'] for r in quality_results.values())
            
            log_step_message(step_idx, f"📊 Overall quality score: {avg_score:.1f}/10")
            log_step_message(step_idx, f"📋 Total issues found: {total_issues}")
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Code quality checks passed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Code quality checks failed: {str(e)}", "error")
            return False
    
    def execute_ci_pipeline(self):
        """Execute the complete CI pipeline"""
        log_step_message(0, f"🚀 Starting CI pipeline for {self.repo_name}", "info")
        
        pipeline_steps = [
            self.step_1_source_checkout,
            self.step_2_dependency_installation,
            self.step_3_code_quality,
            # Add more steps as needed
        ]
        
        start_time = time.time()
        
        for step_func in pipeline_steps:
            if not step_func():
                log_step_message(0, "⚠️ CI pipeline failed", "error")
                return False
            time.sleep(0.3)
        
        execution_time = time.time() - start_time
        log_step_message(len(pipeline_steps)-1, f"🎉 CI pipeline completed in {execution_time:.1f}s!", "success")
        return True

def main():
    """Main function for CI pipeline"""
    print("🏗️ CI/CD Pipeline Visualizer")
    print("=" * 40)
    
    pipeline = CIPipeline("awesome-project")
    
    print("🌐 Monitor at: http://localhost:8080/visualizer.html")
    print("⏳ CI pipeline will start in 3 seconds...")
    
    def delayed_execution():
        time.sleep(3)
        pipeline.execute_ci_pipeline()
    
    import threading
    threading.Thread(target=delayed_execution, daemon=True).start()
    
    start_visualization_service()

if __name__ == "__main__":
    main()
```

## 🐳 Docker Multi-Stage Build

### Container Build Pipeline

```python
#!/usr/bin/env python3
"""Docker Multi-Stage Build Visualization"""

import time
import random
import json
from pathlib import Path

from core import *

class DockerBuildPipeline:
    """Docker multi-stage build with visualization"""
    
    def __init__(self, image_name="my-app"):
        self.image_name = image_name
        self.build_context = Path("docker_build")
        self.build_context.mkdir(exist_ok=True)
        
        create_visualizer()
        self.setup_build_steps()
    
    def setup_build_steps(self):
        """Setup Docker build pipeline steps"""
        steps = [
            ("Build Context", "Prepare Docker build context"),
            ("Base Image", "Pull and prepare base image"),
            ("Dependencies", "Install system and app dependencies"),
            ("Application", "Copy and build application code"),
            ("Testing", "Run tests in container environment"),
            ("Optimization", "Optimize image size and layers"),
            ("Security Scan", "Scan for vulnerabilities"),
            ("Registry Push", "Push image to container registry")
        ]
        
        for step_name, description in steps:
            add_workflow_step(step_name, description)
    
    def step_1_build_context(self):
        """Step 1: Prepare build context"""
        step_idx = 0
        start_workflow_step(step_idx)
        log_step_message(step_idx, "📁 Preparing Docker build context...")
        
        try:
            # Simulate file operations
            files_to_copy = [
                "Dockerfile",
                "requirements.txt", 
                "package.json",
                "src/",
                "config/",
                ".dockerignore"
            ]
            
            context_size = 0
            for file_path in files_to_copy:
                log_step_message(step_idx, f"📄 Adding {file_path} to build context")
                time.sleep(0.2)
                
                # Simulate file sizes
                file_size = random.randint(1, 1000)
                context_size += file_size
            
            log_step_message(step_idx, f"📊 Build context size: {context_size} KB")
            
            # Create .dockerignore simulation
            log_step_message(step_idx, "🚫 Applying .dockerignore filters...")
            excluded_files = ["node_modules/", "*.log", ".git/", "__pycache__/"]
            for excluded in excluded_files:
                log_step_message(step_idx, f"   Excluding {excluded}")
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Build context prepared!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Build context preparation failed: {str(e)}", "error")
            return False
    
    def step_2_base_image(self):
        """Step 2: Base image preparation"""
        step_idx = 1
        start_workflow_step(step_idx)
        log_step_message(step_idx, "🐳 Preparing base image...")
        
        try:
            # Simulate base image operations
            base_images = [
                ("python:3.9-slim", "120MB"),
                ("node:16-alpine", "85MB"),
                ("nginx:alpine", "23MB")
            ]
            
            for image, size in base_images:
                log_step_message(step_idx, f"📥 Pulling {image}...")
                
                # Simulate pull progress
                for progress in [25, 50, 75, 100]:
                    time.sleep(0.3)
                    log_step_message(step_idx, f"   Download progress: {progress}%")
                
                log_step_message(step_idx, f"✓ {image} pulled ({size})")
            
            # Simulate layer caching
            log_step_message(step_idx, "💾 Checking layer cache...")
            cached_layers = random.randint(2, 5)
            log_step_message(step_idx, f"✓ Found {cached_layers} cached layers")
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Base image ready!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Base image preparation failed: {str(e)}", "error")
            return False
    
    def step_3_dependencies(self):
        """Step 3: Install dependencies"""
        step_idx = 2
        start_workflow_step(step_idx)
        log_step_message(step_idx, "📦 Installing dependencies...")
        
        try:
            # System dependencies
            log_step_message(step_idx, "🔧 Installing system dependencies...")
            system_packages = ["curl", "git", "build-essential", "libssl-dev"]
            
            for package in system_packages:
                log_step_message(step_idx, f"   Installing {package}...")
                time.sleep(0.4)
            log_step_message(step_idx, "✓ System dependencies installed")
            
            # Application dependencies
            log_step_message(step_idx, "🐍 Installing application dependencies...")
            
            # Simulate pip install
            log_step_message(step_idx, "   Running: pip install -r requirements.txt")
            pip_packages = ["flask", "requests", "pandas", "numpy", "gunicorn"]
            
            for i, package in enumerate(pip_packages):
                time.sleep(0.6)
                progress = ((i + 1) / len(pip_packages)) * 100
                log_step_message(step_idx, f"   Installing {package}... ({progress:.0f}%)")
            
            log_step_message(step_idx, "✓ Application dependencies installed")
            
            # Clean up package cache
            log_step_message(step_idx, "🧹 Cleaning package cache...")
            time.sleep(0.5)
            saved_space = random.randint(50, 200)
            log_step_message(step_idx, f"✓ Freed {saved_space}MB of cache")
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Dependencies installed successfully!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Dependency installation failed: {str(e)}", "error")
            return False
    
    def execute_docker_build(self):
        """Execute the complete Docker build pipeline"""
        log_step_message(0, f"🐳 Starting Docker build for {self.image_name}", "info")
        
        build_steps = [
            self.step_1_build_context,
            self.step_2_base_image,
            self.step_3_dependencies,
            # Add more steps as needed
        ]
        
        start_time = time.time()
        
        for step_func in build_steps:
            if not step_func():
                log_step_message(0, "⚠️ Docker build failed", "error")
                return False
            time.sleep(0.3)
        
        build_time = time.time() - start_time
        final_size = random.randint(200, 800)
        
        log_step_message(len(build_steps)-1, f"🎉 Docker build completed!", "success")
        log_step_message(len(build_steps)-1, f"📊 Build time: {build_time:.1f}s", "info")
        log_step_message(len(build_steps)-1, f"📦 Final image size: {final_size}MB", "info")
        log_step_message(len(build_steps)-1, f"🏷️ Image tag: {self.image_name}:latest", "info")
        
        return True

def main():
    """Main function for Docker build pipeline"""
    print("🐳 Docker Build Pipeline Visualizer")
    print("=" * 45)
    
    pipeline = DockerBuildPipeline("awesome-web-app")
    
    print("🌐 Monitor at: http://localhost:8080/visualizer.html")
    print("⏳ Docker build will start in 3 seconds...")
    
    def delayed_execution():
        time.sleep(3)
        pipeline.execute_docker_build()
    
    import threading
    threading.Thread(target=delayed_execution, daemon=True).start()
    
    start_visualization_service()

if __name__ == "__main__":
    main()
```

## 📊 Data Processing Pipeline

### ETL Workflow

```python
#!/usr/bin/env python3
"""ETL Data Processing Pipeline with Visualization"""

import time
import random
import json
from datetime import datetime, timedelta
from pathlib import Path

from core import *

class ETLPipeline:
    """Extract, Transform, Load pipeline with visualization"""
    
    def __init__(self, pipeline_name="daily_etl"):
        self.pipeline_name = pipeline_name
        self.data_dir = Path("etl_data")
        self.data_dir.mkdir(exist_ok=True)
        
        create_visualizer()
        self.setup_etl_steps()
    
    def setup_etl_steps(self):
        """Setup ETL pipeline steps"""
        steps = [
            ("Data Extraction", "Extract data from multiple sources"),
            ("Data Validation", "Validate extracted data quality"),
            ("Data Transformation", "Transform and clean data"),
            ("Business Rules", "Apply business logic and rules"),
            ("Data Enrichment", "Enrich with reference data"),
            ("Quality Checks", "Final quality assurance"),
            ("Data Loading", "Load data into target systems"),
            ("Indexing", "Create indexes and optimize")
        ]
        
        for step_name, description in steps:
            add_workflow_step(step_name, description)
    
    def step_1_data_extraction(self):
        """Step 1: Extract data from sources"""
        step_idx = 0
        start_workflow_step(step_idx)
        log_step_message(step_idx, "📥 Starting data extraction...")
        
        try:
            # Define data sources
            data_sources = [
                {
                    "name": "PostgreSQL Database",
                    "type": "database",
                    "tables": ["users", "orders", "products"],
                    "records": 150000
                },
                {
                    "name": "REST API",
                    "type": "api",
                    "endpoints": ["/customer-data", "/transaction-data"],
                    "records": 75000
                },
                {
                    "name": "CSV Files",
                    "type": "file",
                    "files": ["sales_data.csv", "inventory.csv"],
                    "records": 50000
                },
                {
                    "name": "External Service",
                    "type": "service",
                    "services": ["payment-service", "notification-service"],
                    "records": 25000
                }
            ]
            
            total_extracted = 0
            
            for source in data_sources:
                log_step_message(step_idx, f"🔌 Connecting to {source['name']}...")
                time.sleep(0.5)
                
                if source['type'] == 'database':
                    for table in source['tables']:
                        log_step_message(step_idx, f"   Extracting from table: {table}")
                        time.sleep(0.8)
                        
                        # Simulate extraction progress
                        for progress in [30, 60, 90, 100]:
                            time.sleep(0.2)
                            log_step_message(step_idx, f"     Progress: {progress}%")
                        
                        records = random.randint(10000, 60000)
                        total_extracted += records
                        log_step_message(step_idx, f"   ✓ Extracted {records} records from {table}")
                
                elif source['type'] == 'api':
                    for endpoint in source['endpoints']:
                        log_step_message(step_idx, f"   Calling API endpoint: {endpoint}")
                        time.sleep(1.0)
                        
                        records = random.randint(20000, 40000)
                        total_extracted += records
                        log_step_message(step_idx, f"   ✓ Retrieved {records} records from {endpoint}")
                
                elif source['type'] == 'file':
                    for file_name in source['files']:
                        log_step_message(step_idx, f"   Reading file: {file_name}")
                        time.sleep(0.6)
                        
                        records = random.randint(15000, 35000)
                        total_extracted += records
                        log_step_message(step_idx, f"   ✓ Processed {records} records from {file_name}")
                
                log_step_message(step_idx, f"✓ {source['name']} extraction completed")
            
            # Save extraction metadata
            extraction_metadata = {
                "timestamp": datetime.now().isoformat(),
                "total_records": total_extracted,
                "sources": len(data_sources),
                "extraction_time": "3.2 minutes"
            }
            
            with open(self.data_dir / "extraction_metadata.json", 'w') as f:
                json.dump(extraction_metadata, f, indent=2)
            
            log_step_message(step_idx, f"📊 Total records extracted: {total_extracted:,}")
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Data extraction completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Data extraction failed: {str(e)}", "error")
            return False
    
    def step_2_data_validation(self):
        """Step 2: Validate extracted data"""
        step_idx = 1
        start_workflow_step(step_idx)
        log_step_message(step_idx, "🔍 Starting data validation...")
        
        try:
            validation_rules = [
                ("Null Value Check", "Check for unexpected null values"),
                ("Data Type Validation", "Validate column data types"),
                ("Range Validation", "Check value ranges and constraints"),
                ("Referential Integrity", "Validate foreign key relationships"),
                ("Business Rules", "Apply business-specific validation"),
                ("Duplicate Detection", "Identify duplicate records")
            ]
            
            validation_results = {}
            
            for rule_name, description in validation_rules:
                log_step_message(step_idx, f"🔍 {rule_name}: {description}")
                time.sleep(random.uniform(0.8, 1.5))
                
                # Simulate validation results
                passed_records = random.randint(290000, 299000)
                total_records = 300000
                pass_rate = (passed_records / total_records) * 100
                
                validation_results[rule_name] = {
                    "passed": passed_records,
                    "total": total_records,
                    "pass_rate": pass_rate,
                    "status": "passed" if pass_rate >= 95 else "warning" if pass_rate >= 90 else "failed"
                }
                
                if pass_rate >= 95:
                    log_step_message(step_idx, f"   ✓ {pass_rate:.1f}% passed ({passed_records:,}/{total_records:,})")
                elif pass_rate >= 90:
                    log_step_message(step_idx, f"   ⚠️ {pass_rate:.1f}% passed ({passed_records:,}/{total_records:,})", "warning")
                else:
                    log_step_message(step_idx, f"   ❌ {pass_rate:.1f}% passed ({passed_records:,}/{total_records:,})", "error")
                    return False
            
            # Overall validation summary
            avg_pass_rate = sum(r['pass_rate'] for r in validation_results.values()) / len(validation_results)
            log_step_message(step_idx, f"📊 Overall validation pass rate: {avg_pass_rate:.1f}%")
            
            # Save validation results
            with open(self.data_dir / "validation_results.json", 'w') as f:
                json.dump(validation_results, f, indent=2)
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Data validation completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Data validation failed: {str(e)}", "error")
            return False
    
    def step_3_data_transformation(self):
        """Step 3: Transform and clean data"""
        step_idx = 2
        start_workflow_step(step_idx)
        log_step_message(step_idx, "⚙️ Starting data transformation...")
        
        try:
            transformation_tasks = [
                ("Data Cleaning", "Remove invalid and corrupt records"),
                ("Standardization", "Standardize formats and encodings"),
                ("Normalization", "Normalize data structures"),
                ("Aggregation", "Create summary and aggregate tables"),
                ("Derivation", "Calculate derived fields and metrics"),
                ("Anonymization", "Apply data privacy and anonymization")
            ]
            
            processed_records = 0
            
            for task_name, description in transformation_tasks:
                log_step_message(step_idx, f"⚙️ {task_name}: {description}")
                
                # Simulate processing batches
                batch_size = 50000
                total_batches = 6
                
                for batch in range(1, total_batches + 1):
                    time.sleep(0.5)
                    batch_processed = min(batch_size, 300000 - processed_records)
                    processed_records += batch_processed
                    
                    progress = (processed_records / 300000) * 100
                    log_step_message(step_idx, f"   Batch {batch}/{total_batches}: {batch_processed:,} records ({progress:.1f}%)")
                
                log_step_message(step_idx, f"   ✓ {task_name} completed")
            
            # Transformation statistics
            transformation_stats = {
                "records_processed": processed_records,
                "records_cleaned": random.randint(5000, 15000),
                "records_transformed": processed_records - random.randint(1000, 5000),
                "processing_time": "8.5 minutes"
            }
            
            log_step_message(step_idx, f"📊 Transformation statistics:")
            log_step_message(step_idx, f"   Processed: {transformation_stats['records_processed']:,} records")
            log_step_message(step_idx, f"   Cleaned: {transformation_stats['records_cleaned']:,} records")
            log_step_message(step_idx, f"   Transformed: {transformation_stats['records_transformed']:,} records")
            
            with open(self.data_dir / "transformation_stats.json", 'w') as f:
                json.dump(transformation_stats, f, indent=2)
            
            complete_workflow_step(step_idx)
            log_step_message(step_idx, "✅ Data transformation completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_idx, "failed")
            log_step_message(step_idx, f"❌ Data transformation failed: {str(e)}", "error")
            return False
    
    def execute_etl_pipeline(self):
        """Execute the complete ETL pipeline"""
        log_step_message(0, f"🚀 Starting ETL pipeline: {self.pipeline_name}", "info")
        
        etl_steps = [
            self.step_1_data_extraction,
            self.step_2_data_validation,
            self.step_3_data_transformation,
            # Add more steps as needed
        ]
        
        pipeline_start = time.time()
        
        for step_func in etl_steps:
            if not step_func():
                log_step_message(0, "⚠️ ETL pipeline failed", "error")
                return False
            time.sleep(0.5)
        
        pipeline_duration = time.time() - pipeline_start
        
        log_step_message(len(etl_steps)-1, f"🎉 ETL pipeline completed successfully!", "success")
        log_step_message(len(etl_steps)-1, f"⏱️ Total execution time: {pipeline_duration:.1f}s", "info")
        log_step_message(len(etl_steps)-1, f"📊 Pipeline efficiency: High", "info")
        
        return True

def main():
    """Main function for ETL pipeline"""
    print("📊 ETL Data Processing Pipeline Visualizer")
    print("=" * 50)
    
    pipeline = ETLPipeline("customer_analytics_etl")
    
    print("🌐 Monitor at: http://localhost:8080/visualizer.html")
    print("⏳ ETL pipeline will start in 3 seconds...")
    
    def delayed_execution():
        time.sleep(3)
        pipeline.execute_etl_pipeline()
    
    import threading
    threading.Thread(target=delayed_execution, daemon=True).start()
    
    start_visualization_service()

if __name__ == "__main__":
    main()
```

## 🎯 Usage Tips

### Best Practices

1. **Step Granularity**: Make steps meaningful but not too granular
2. **Error Handling**: Always handle exceptions and set appropriate status
3. **Progress Updates**: Provide regular progress updates within long steps
4. **Log Levels**: Use appropriate log levels (info, success, warning, error)
5. **Resource Cleanup**: Clean up resources in finally blocks

### Performance Considerations

- Limit log frequency for high-throughput operations
- Use batch updates for similar operations
- Consider step duration for user experience
- Monitor WebSocket connection limits

### Integration Patterns

- **Decorator Pattern**: Wrap existing functions with visualization
- **Context Manager**: Use with statements for step management
- **Background Execution**: Always run workflows in background threads
- **Configuration**: Use environment variables for deployment flexibility

---

For more examples and advanced patterns, check the `examples/` directory in the project repository.