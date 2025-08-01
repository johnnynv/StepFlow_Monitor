#!/usr/bin/env python3
"""
ContainerFlow Visualizer - Basic Integration Example
How to integrate visualization features into your existing scripts

This example shows the simplest way to add real-time visualization
to an existing workflow or container execution process.
"""

import subprocess
import time
import os
import sys
from core import init_visualizer, add_step, start_step, complete_step, log_message, start_visualizer
import threading

def your_existing_workflow():
    """Your existing workflow with integrated visualization features"""
    
    # 1. Environment setup for Python and scientific computing
    step_id = 0
    start_step(step_id)
    log_message(step_id, "Starting Python environment setup...")
    
    try:
        # Simulate environment configuration
        log_message(step_id, "Installing scientific computing packages...")
        time.sleep(2)
        log_message(step_id, "Configuring Jupyter environment...")
        time.sleep(1)
        log_message(step_id, "Validating environment configuration...")
        time.sleep(1)
        
        complete_step(step_id, "completed")
        log_message(step_id, "✅ Python environment setup completed!", "success")
    except Exception as e:
        complete_step(step_id, "failed")
        log_message(step_id, f"❌ Environment setup failed: {str(e)}", "error")
        return
    
    # 2. Dataset download
    step_id = 1
    start_step(step_id)
    log_message(step_id, "Starting dataset download...")
    
    try:
        # Simulate dataset download
        datasets = ["dataset1.csv", "dataset2.json", "images.zip"]
        for i, dataset in enumerate(datasets):
            log_message(step_id, f"Downloading {dataset}... ({i+1}/{len(datasets)})")
            time.sleep(1)
        
        complete_step(step_id, "completed")
        log_message(step_id, f"✅ Successfully downloaded {len(datasets)} datasets!", "success")
    except Exception as e:
        complete_step(step_id, "failed")
        log_message(step_id, f"❌ Dataset download failed: {str(e)}", "error")
        return
    
    # 3. Run Jupyter notebook
    step_id = 2
    start_step(step_id)
    log_message(step_id, "Starting Jupyter Notebook execution...")
    
    try:
        # Simulate notebook execution
        log_message(step_id, "Initializing data analysis...")
        time.sleep(2)
        log_message(step_id, "Executing data preprocessing...")
        time.sleep(3)
        log_message(step_id, "Running machine learning models...")
        time.sleep(4)
        log_message(step_id, "Generating visualization plots...")
        time.sleep(2)
        log_message(step_id, "Saving analysis results...")
        time.sleep(1)
        
        complete_step(step_id, "completed")
        log_message(step_id, "✅ Jupyter Notebook execution completed!", "success")
    except Exception as e:
        complete_step(step_id, "failed")
        log_message(step_id, f"❌ Notebook execution failed: {str(e)}", "error")
        return
    
    # 4. Run pytest
    step_id = 3
    start_step(step_id)
    log_message(step_id, "Starting test execution...")
    
    try:
        # Simulate pytest execution
        tests = ["test_data_validation.py", "test_model_accuracy.py", "test_output_format.py"]
        for i, test in enumerate(tests):
            log_message(step_id, f"Running test: {test}")
            time.sleep(1.5)
            log_message(step_id, f"✓ {test} passed")
        
        log_message(step_id, "Generating coverage report...")
        time.sleep(1)
        log_message(step_id, "Generating HTML test report...")
        time.sleep(1)
        
        complete_step(step_id, "completed")
        log_message(step_id, f"✅ All tests passed! Coverage: 94%", "success")
    except Exception as e:
        complete_step(step_id, "failed")
        log_message(step_id, f"❌ Test execution failed: {str(e)}", "error")
        return
    
    # 5. Generate results and reports
    step_id = 4
    start_step(step_id)
    log_message(step_id, "Starting final report generation...")
    
    try:
        # Simulate report generation
        log_message(step_id, "Collecting execution results...")
        time.sleep(1)
        log_message(step_id, "Generating HTML report...")
        time.sleep(2)
        log_message(step_id, "Generating PDF report...")
        time.sleep(2)
        log_message(step_id, "Packaging result files...")
        time.sleep(1)
        
        # Simulate docker cp operation
        log_message(step_id, "Copying report files to host...")
        time.sleep(1)
        
        complete_step(step_id, "completed")
        log_message(step_id, "🎉 Workflow completed! All reports generated", "success")
        
        # Show final results
        log_message(step_id, "📊 Generated files:", "info")
        files = ["analysis_report.html", "test_coverage.html", "model_results.pdf", "artifacts.zip"]
        for f in files:
            log_message(step_id, f"  📄 {f}", "info")
            
    except Exception as e:
        complete_step(step_id, "failed")
        log_message(step_id, f"❌ Report generation failed: {str(e)}", "error")

def main():
    """Main function"""
    print("🚀 Starting ContainerFlow Visualizer Basic Example")
    
    # Initialize visualizer
    viz = init_visualizer(port=8080, websocket_port=8765)
    
    # Define workflow steps
    add_step("Environment Setup", "Configure Python and scientific computing environment")
    add_step("Dataset Download", "Download required datasets")
    add_step("Jupyter Execution", "Run data analysis notebook")
    add_step("Test Execution", "Run pytest and generate coverage reports")
    add_step("Report Generation", "Generate final reports and result files")
    
    print("📋 Workflow steps defined")
    print("🌐 Open browser at: http://localhost:8080/visualizer.html")
    print("👀 Monitor real-time execution progress and logs")
    
    # Execute workflow in background thread
    workflow_thread = threading.Thread(target=your_existing_workflow, daemon=True)
    
    # Delayed start to let user open browser
    def delayed_start():
        print("⏳ Workflow will start in 5 seconds...")
        time.sleep(5)
        workflow_thread.start()
    
    delay_thread = threading.Thread(target=delayed_start, daemon=True)
    delay_thread.start()
    
    # Start visualization service
    start_visualizer()

if __name__ == "__main__":
    main()