"""
ContainerFlow Visualizer Core Package
Professional container execution step visualization tool
"""

from .visualizer import ContainerFlowVisualizer
from .api import (
    create_visualizer,
    add_workflow_step,
    start_workflow_step,
    complete_workflow_step,
    log_step_message,
    start_visualization_service,
    # Legacy compatibility
    init_visualizer,
    add_step,
    start_step,
    complete_step,
    log_message,
    start_visualizer
)

__version__ = "2.0.0"
__author__ = "ContainerFlow Team"

__all__ = [
    "ContainerFlowVisualizer",
    "create_visualizer",
    "add_workflow_step",
    "start_workflow_step", 
    "complete_workflow_step",
    "log_step_message",
    "start_visualization_service",
    # Legacy API
    "init_visualizer",
    "add_step",
    "start_step",
    "complete_step",
    "log_message",
    "start_visualizer"
]