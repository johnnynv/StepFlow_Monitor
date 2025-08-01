#!/usr/bin/env python3
"""
ContainerFlow Visualizer API - Convenience Functions
Simple API for integrating workflow visualization into existing scripts
"""

from .visualizer import ContainerFlowVisualizer

# Global visualizer instance for convenience API
_global_visualizer = None


def create_visualizer(http_port=8080, websocket_port=8765, web_interface_dir="../web_interface"):
    """Initialize the global ContainerFlow visualizer instance"""
    global _global_visualizer
    _global_visualizer = ContainerFlowVisualizer(http_port, websocket_port, web_interface_dir)
    return _global_visualizer


def add_workflow_step(step_name, description=""):
    """Add an execution step to the workflow"""
    global _global_visualizer
    if _global_visualizer:
        _global_visualizer.add_execution_step(step_name, description)


def start_workflow_step(step_index):
    """Start executing a workflow step"""
    global _global_visualizer
    if _global_visualizer:
        _global_visualizer.start_execution_step(step_index)


def complete_workflow_step(step_index, status="completed"):
    """Complete a workflow step with given status"""
    global _global_visualizer
    if _global_visualizer:
        _global_visualizer.complete_execution_step(step_index, status)


def log_step_message(step_index, message, log_level="info"):
    """Add a log message for a specific step"""
    global _global_visualizer
    if _global_visualizer:
        _global_visualizer.add_step_log(step_index, message, log_level)


def start_visualization_service():
    """Start the visualization service (WebSocket + HTTP servers)"""
    global _global_visualizer
    if _global_visualizer:
        _global_visualizer.start_visualization_service()


# Legacy API for backward compatibility
init_visualizer = create_visualizer
add_step = add_workflow_step
start_step = start_workflow_step
complete_step = complete_workflow_step
log_message = log_step_message
start_visualizer = start_visualization_service