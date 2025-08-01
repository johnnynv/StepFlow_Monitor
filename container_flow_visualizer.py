#!/usr/bin/env python3
"""
ContainerFlow Visualizer - Main Entry Point
Professional container execution step visualization tool

A lightweight, real-time visualization tool for monitoring container execution workflows.
Modular architecture with separated concerns for better maintainability.

Usage:
    python container_flow_visualizer.py

Or import as a module:
    from core import create_visualizer, add_workflow_step, start_visualization_service
"""

import time
import threading
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import (
    create_visualizer,
    add_workflow_step,
    start_workflow_step,
    complete_workflow_step,
    log_step_message,
    start_visualization_service
)


def demonstrate_workflow():
    """Demonstrate the visualizer with a sample workflow execution"""
    
    # Initialize the ContainerFlow visualizer
    workflow_visualizer = create_visualizer(
        http_port=8080, 
        websocket_port=8765,
        web_interface_dir="web_interface"
    )
    
    # Define workflow steps
    workflow_steps = [
        ("Environment Setup", "Setting up Python and scientific computing environment"),
        ("Dataset Download", "Downloading required datasets and dependencies"),
        ("Jupyter Execution", "Running Jupyter notebook analysis and processing"),
        ("Pytest Execution", "Running tests and generating coverage reports"),
        ("Report Generation", "Generating final reports and artifacts")
    ]
    
    # Add all steps to the visualizer
    for step_name, step_description in workflow_steps:
        add_workflow_step(step_name, step_description)
    
    print("📋 Workflow steps defined:")
    for i, (name, desc) in enumerate(workflow_steps):
        print(f"   {i+1}. {name}: {desc}")
    
    print(f"\n🌐 Web interface: http://localhost:8080/visualizer.html")
    print("👀 Monitor real-time execution progress and detailed logs")
    
    # Simulate workflow execution in background thread
    def simulate_workflow_execution():
        time.sleep(3)  # Allow time for interface to load
        
        for step_index in range(len(workflow_steps)):
            step_name = workflow_steps[step_index][0]
            
            # Start the step
            start_workflow_step(step_index)
            log_step_message(step_index, f"🚀 Starting step {step_index+1}: {step_name}")
            
            # Simulate step execution with progress updates
            progress_updates = [
                ("Initializing...", 1),
                ("Processing data...", 2),
                ("Generating outputs...", 1.5),
                ("Finalizing...", 0.5)
            ]
            
            for progress_msg, delay in progress_updates:
                time.sleep(delay)
                log_step_message(step_index, f"   {progress_msg}")
            
            # Complete the step
            complete_workflow_step(step_index)
            log_step_message(step_index, f"✅ Step {step_index+1} completed successfully!", "success")
            time.sleep(0.5)
        
        log_step_message(len(workflow_steps)-1, "🎉 All workflow steps completed!", "success")
    
    # Start the simulation in background
    simulation_thread = threading.Thread(target=simulate_workflow_execution, daemon=True)
    simulation_thread.start()
    
    # Start the visualization service (this will block)
    start_visualization_service()


if __name__ == "__main__":
    try:
        print("🚀 Starting ContainerFlow Visualizer")
        print("=" * 50)
        demonstrate_workflow()
    except KeyboardInterrupt:
        print("\n🛑 Stopping ContainerFlow Visualizer...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)