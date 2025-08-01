#!/usr/bin/env python3
"""
ContainerFlow Visualizer Integration Example
How to integrate visualization into your existing workflow scripts

This example demonstrates how to add real-time visualization to 
an existing scientific computing or container workflow.
"""

import sys
import os
import time
import threading
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    create_visualizer,
    add_workflow_step,
    start_workflow_step,
    complete_workflow_step,
    log_step_message,
    start_visualization_service
)


class ScientificWorkflowVisualizer:
    """Example of integrating visualization into a scientific workflow"""
    
    def __init__(self):
        self.results_directory = "workflow_results"
        self.ensure_results_directory()
        
    def ensure_results_directory(self):
        """Create results directory if it doesn't exist"""
        os.makedirs(self.results_directory, exist_ok=True)
    
    def step_1_environment_setup(self):
        """Step 1: Environment configuration with visualization"""
        step_index = 0
        start_workflow_step(step_index)
        log_step_message(step_index, "🐍 Starting environment configuration...")
        
        try:
            # Check Python version
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            log_step_message(step_index, f"Python version: {result.stdout.strip()}")
            
            # Simulate package installation checks
            required_packages = ["numpy", "pandas", "matplotlib", "jupyter", "pytest"]
            for package in required_packages:
                try:
                    __import__(package)
                    log_step_message(step_index, f"✓ {package} is available")
                except ImportError:
                    log_step_message(step_index, f"⚠️ {package} not found", "warning")
                time.sleep(0.3)
            
            # Create subdirectories
            subdirs = ["datasets", "notebooks", "tests", "reports"]
            for subdir in subdirs:
                dir_path = os.path.join(self.results_directory, subdir)
                os.makedirs(dir_path, exist_ok=True)
                log_step_message(step_index, f"📁 Created directory: {subdir}")
                time.sleep(0.2)
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, "✅ Environment setup completed!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Environment setup failed: {str(e)}", "error")
            return False
    
    def step_2_data_acquisition(self):
        """Step 2: Data download and preparation"""
        step_index = 1
        start_workflow_step(step_index)
        log_step_message(step_index, "📥 Starting data acquisition...")
        
        try:
            # Simulate downloading datasets
            datasets = [
                {"name": "training_data.csv", "size": "2.3MB", "source": "external_api"},
                {"name": "test_data.csv", "size": "0.8MB", "source": "external_api"},
                {"name": "metadata.json", "size": "15KB", "source": "config_server"}
            ]
            
            for dataset in datasets:
                log_step_message(step_index, f"📦 Downloading {dataset['name']} ({dataset['size']})...")
                
                # Simulate download progress
                for progress in [25, 50, 75, 100]:
                    time.sleep(0.4)
                    log_step_message(step_index, f"   Download progress: {progress}%")
                
                # Create mock file
                file_path = os.path.join(self.results_directory, "datasets", dataset['name'])
                with open(file_path, 'w') as f:
                    f.write(f"# Mock dataset: {dataset['name']}\n")
                    f.write(f"# Source: {dataset['source']}\n")
                    f.write(f"# Size: {dataset['size']}\n")
                
                log_step_message(step_index, f"✓ {dataset['name']} acquired successfully")
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, f"✅ Successfully acquired {len(datasets)} datasets!", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Data acquisition failed: {str(e)}", "error")
            return False
    
    def step_3_analysis_execution(self):
        """Step 3: Run analysis notebooks"""
        step_index = 2
        start_workflow_step(step_index)
        log_step_message(step_index, "📓 Starting analysis execution...")
        
        try:
            # Simulate notebook creation and execution
            notebook_steps = [
                "Initializing analysis environment...",
                "Loading and validating datasets...",
                "Performing exploratory data analysis...",
                "Running statistical computations...",
                "Generating visualization plots...",
                "Saving analysis results..."
            ]
            
            for i, step_desc in enumerate(notebook_steps):
                log_step_message(step_index, f"🔄 {step_desc}")
                time.sleep(1.2)
                progress = ((i + 1) / len(notebook_steps)) * 100
                log_step_message(step_index, f"   Analysis progress: {progress:.0f}%")
            
            # Create mock output
            output_file = os.path.join(self.results_directory, "reports", "analysis_results.html")
            with open(output_file, 'w') as f:
                f.write(f"""
                <html>
                    <head><title>Analysis Results</title></head>
                    <body>
                        <h1>Scientific Analysis Results</h1>
                        <p>Analysis completed at: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
                        <p>Status: ✅ Successful</p>
                    </body>
                </html>
                """)
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, "✅ Analysis execution completed!", "success")
            log_step_message(step_index, f"📄 Results saved to: {output_file}", "info")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Analysis execution failed: {str(e)}", "error")
            return False
    
    def step_4_quality_assurance(self):
        """Step 4: Run tests and quality checks"""
        step_index = 3
        start_workflow_step(step_index)
        log_step_message(step_index, "🧪 Starting quality assurance...")
        
        try:
            # Simulate test execution
            test_suites = [
                "test_data_validation.py",
                "test_analysis_functions.py", 
                "test_output_format.py",
                "test_performance_benchmarks.py"
            ]
            
            passed_tests = 0
            
            for test_suite in test_suites:
                log_step_message(step_index, f"🔍 Running {test_suite}...")
                time.sleep(1.5)
                
                # Simulate test results (95% pass rate)
                import random
                if random.random() > 0.05:
                    log_step_message(step_index, f"✓ {test_suite} PASSED")
                    passed_tests += 1
                else:
                    log_step_message(step_index, f"✗ {test_suite} FAILED", "warning")
            
            # Generate test report
            coverage_percentage = random.uniform(88, 96)
            log_step_message(step_index, f"📊 Generating quality report...")
            log_step_message(step_index, f"   Tests passed: {passed_tests}/{len(test_suites)}")
            log_step_message(step_index, f"   Code coverage: {coverage_percentage:.1f}%")
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, f"✅ Quality assurance completed! Pass rate: {passed_tests/len(test_suites)*100:.0f}%", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Quality assurance failed: {str(e)}", "error")
            return False
    
    def step_5_final_reporting(self):
        """Step 5: Generate comprehensive reports"""
        step_index = 4
        start_workflow_step(step_index)
        log_step_message(step_index, "📋 Starting final report generation...")
        
        try:
            # Collect all artifacts
            log_step_message(step_index, "📁 Collecting workflow artifacts...")
            time.sleep(1)
            
            # Generate final report
            log_step_message(step_index, "📝 Generating comprehensive report...")
            final_report_path = os.path.join(self.results_directory, "final_workflow_report.html")
            
            with open(final_report_path, 'w') as f:
                f.write(f"""
                <html>
                <head><title>Workflow Execution Report</title></head>
                <body style="font-family: Arial, sans-serif; margin: 40px;">
                    <h1>🔬 Scientific Workflow Execution Report</h1>
                    <h2>📊 Execution Summary</h2>
                    <ul>
                        <li>✅ Environment Setup: Completed</li>
                        <li>✅ Data Acquisition: Completed</li>
                        <li>✅ Analysis Execution: Completed</li>
                        <li>✅ Quality Assurance: Completed</li>
                        <li>✅ Final Reporting: Completed</li>
                    </ul>
                    <h2>⏰ Execution Details</h2>
                    <p>Report generated: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
                    <p>Status: 🎉 All steps completed successfully!</p>
                </body>
                </html>
                """)
            
            log_step_message(step_index, f"📄 Final report generated: {final_report_path}")
            time.sleep(1)
            
            complete_workflow_step(step_index, "completed")
            log_step_message(step_index, "🎉 Workflow completed successfully! All reports generated.", "success")
            return True
            
        except Exception as e:
            complete_workflow_step(step_index, "failed")
            log_step_message(step_index, f"❌ Final reporting failed: {str(e)}", "error")
            return False
    
    def execute_complete_workflow(self):
        """Execute the complete workflow with error handling"""
        workflow_steps = [
            self.step_1_environment_setup,
            self.step_2_data_acquisition,
            self.step_3_analysis_execution,
            self.step_4_quality_assurance,
            self.step_5_final_reporting
        ]
        
        log_step_message(0, "🚀 Starting complete scientific workflow...", "info")
        
        for step_func in workflow_steps:
            if not step_func():
                log_step_message(0, "⚠️ Workflow stopped due to step failure", "warning")
                return False
            time.sleep(0.5)  # Brief pause between steps
        
        log_step_message(4, "🎊 Complete workflow execution finished!", "success")
        return True


def main():
    """Main function to demonstrate workflow integration"""
    print("🚀 Starting Enhanced Scientific Workflow Visualizer")
    print("=" * 55)
    
    # Initialize the visualizer
    workflow_viz = create_visualizer(
        http_port=8080, 
        websocket_port=8765,
        web_interface_dir="../web_interface"
    )
    
    # Define the workflow steps
    workflow_steps = [
        ("Environment Configuration", "Configure Python and scientific computing environment"),
        ("Data Acquisition", "Download and prepare required datasets"),
        ("Analysis Execution", "Run data analysis and machine learning notebooks"),
        ("Quality Assurance", "Execute tests and generate coverage reports"),
        ("Final Reporting", "Generate comprehensive workflow reports")
    ]
    
    # Add steps to visualizer
    for step_name, step_description in workflow_steps:
        add_workflow_step(step_name, step_description)
    
    print("📋 Workflow steps configured:")
    for i, (name, desc) in enumerate(workflow_steps):
        print(f"   {i+1}. {name}")
    
    print(f"\n🌐 Monitor at: http://localhost:8080/visualizer.html")
    print("👀 Real-time progress tracking and detailed logging")
    print("⏳ Workflow will start in 3 seconds...\n")
    
    # Create workflow instance
    workflow = ScientificWorkflowVisualizer()
    
    # Execute workflow in background thread
    def delayed_workflow_execution():
        time.sleep(3)  # Allow user to open browser
        workflow.execute_complete_workflow()
    
    workflow_thread = threading.Thread(target=delayed_workflow_execution, daemon=True)
    workflow_thread.start()
    
    # Start the visualization service
    start_visualization_service()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Workflow visualization stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)