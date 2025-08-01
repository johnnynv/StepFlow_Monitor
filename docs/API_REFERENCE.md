# 📚 ContainerFlow Visualizer API Reference

## Core API Functions

### Visualizer Initialization

#### `create_visualizer(http_port=8080, websocket_port=8765, web_interface_dir="web_interface")`

Initialize a new ContainerFlow visualizer instance.

**Parameters:**
- `http_port` (int): Port for HTTP server (default: 8080)
- `websocket_port` (int): Port for WebSocket server (default: 8765)  
- `web_interface_dir` (str): Directory containing web interface files

**Returns:**
- `ContainerFlowVisualizer`: Visualizer instance

**Example:**
```python
from core import create_visualizer

viz = create_visualizer(http_port=8080, websocket_port=8765)
```

### Workflow Management

#### `add_workflow_step(step_name, description="")`

Add a new step to the workflow.

**Parameters:**
- `step_name` (str): Name of the execution step
- `description` (str): Optional detailed description

**Example:**
```python
add_workflow_step("Environment Setup", "Configure Python and dependencies")
add_workflow_step("Data Processing", "Clean and transform datasets")
```

#### `start_workflow_step(step_index)`

Start executing a specific workflow step.

**Parameters:**
- `step_index` (int): Zero-based index of the step to start

**Example:**
```python
start_workflow_step(0)  # Start first step
```

#### `complete_workflow_step(step_index, status="completed")`

Mark a workflow step as completed.

**Parameters:**
- `step_index` (int): Zero-based index of the step
- `status` (str): Status to set ("completed", "failed", "cancelled")

**Example:**
```python
complete_workflow_step(0, "completed")
complete_workflow_step(1, "failed")
```

### Logging

#### `log_step_message(step_index, message, log_level="info")`

Add a log message for a specific step.

**Parameters:**
- `step_index` (int): Zero-based index of the step
- `message` (str): Log message content  
- `log_level` (str): Log level ("info", "success", "warning", "error")

**Example:**
```python
log_step_message(0, "Starting environment configuration...")
log_step_message(0, "Configuration completed!", "success")
log_step_message(1, "Warning: deprecated package detected", "warning")
log_step_message(2, "Critical error occurred", "error")
```

### Service Control

#### `start_visualization_service()`

Start the complete visualization service (HTTP + WebSocket servers).

**Example:**
```python
# This will block the main thread
start_visualization_service()
```

## ContainerFlowVisualizer Class

### Constructor

```python
ContainerFlowVisualizer(http_port=8080, websocket_port=8765, web_interface_dir="web_interface")
```

### Methods

#### `add_execution_step(step_name, description="")`

Add an execution step to the workflow.

#### `start_execution_step(step_index)`

Start executing a specific step.

#### `complete_execution_step(step_index, status="completed")`

Complete a specific step with given status.

#### `add_step_log(step_index, message, log_level="info")`

Add a log entry for a specific step.

#### `start_visualization_service()`

Start the complete visualization service.

### Properties

- `execution_steps` (list): List of workflow steps
- `execution_logs` (list): List of log entries
- `current_step_index` (int): Index of currently executing step
- `total_step_count` (int): Total number of steps
- `workflow_start_time` (str): ISO timestamp of workflow start

## Legacy API (Backward Compatibility)

For backward compatibility, the following legacy functions are available:

```python
# Legacy function -> New function
init_visualizer()        -> create_visualizer()
add_step()              -> add_workflow_step()
start_step()            -> start_workflow_step()
complete_step()         -> complete_workflow_step()
log_message()           -> log_step_message()
start_visualizer()      -> start_visualization_service()
```

## WebSocket Protocol

### Message Types

#### Client → Server
Currently, no client-to-server messages are implemented.

#### Server → Client

**Initial State Message**
```json
{
  "type": "initial_state",
  "data": {
    "current_step_index": 0,
    "total_step_count": 5,
    "execution_steps": [...],
    "recent_logs": [...],
    "workflow_start_time": "2023-12-01T10:00:00"
  }
}
```

**Status Update Message**
```json
{
  "type": "status_update", 
  "data": {
    "current_step_index": 1,
    "total_step_count": 5,
    "execution_steps": [...],
    "recent_logs": [...],
    "workflow_start_time": "2023-12-01T10:00:00",
    "update_timestamp": "2023-12-01T10:05:00"
  }
}
```

### Step Object Structure

```json
{
  "id": 0,
  "name": "Environment Setup",
  "description": "Configure Python and dependencies",
  "status": "completed",
  "start_time": "2023-12-01T10:00:00",
  "end_time": "2023-12-01T10:02:00", 
  "logs": [...],
  "duration_seconds": 120.5
}
```

### Log Entry Structure

```json
{
  "timestamp": "2023-12-01T10:01:00",
  "step_index": 0,
  "level": "info",
  "message": "Installing dependencies..."
}
```

## Error Handling

### Exception Types

The visualizer uses standard Python exceptions:

- `ConnectionError`: WebSocket connection issues
- `ValueError`: Invalid parameter values
- `RuntimeError`: Service startup failures

### Best Practices

```python
try:
    start_workflow_step(0)
    # Your step logic here
    complete_workflow_step(0, "completed")
except Exception as e:
    log_step_message(0, f"Step failed: {str(e)}", "error")
    complete_workflow_step(0, "failed")
```

## Configuration

### Environment Variables

- `CONTAINERFLOW_HTTP_PORT`: Override default HTTP port
- `CONTAINERFLOW_WS_PORT`: Override default WebSocket port
- `CONTAINERFLOW_WEB_DIR`: Override web interface directory
- `CONTAINERFLOW_LOG_LEVEL`: Set logging level

### Custom Configuration

```python
import os
from core import create_visualizer

# Use environment variables
http_port = int(os.getenv('CONTAINERFLOW_HTTP_PORT', 8080))
ws_port = int(os.getenv('CONTAINERFLOW_WS_PORT', 8765))

viz = create_visualizer(http_port=http_port, websocket_port=ws_port)
```

## Examples

### Basic Usage

```python
from core import *
import threading
import time

# Initialize
viz = create_visualizer()

# Define workflow
add_workflow_step("Step 1", "First step")
add_workflow_step("Step 2", "Second step")

# Background execution
def execute_workflow():
    time.sleep(2)  # Wait for interface
    
    for i in range(2):
        start_workflow_step(i)
        log_step_message(i, f"Executing step {i+1}...")
        time.sleep(3)  # Simulate work
        complete_workflow_step(i)
        log_step_message(i, f"Step {i+1} completed!", "success")

# Start background execution
threading.Thread(target=execute_workflow, daemon=True).start()

# Start visualization (blocks)
start_visualization_service()
```

### Error Handling

```python
def robust_step():
    step_index = 0
    start_workflow_step(step_index)
    
    try:
        log_step_message(step_index, "Starting risky operation...")
        
        # Risky operation here
        risky_operation()
        
        complete_workflow_step(step_index, "completed")
        log_step_message(step_index, "Operation successful!", "success")
        
    except SpecificError as e:
        log_step_message(step_index, f"Recoverable error: {e}", "warning")
        # Handle and continue
        complete_workflow_step(step_index, "completed")
        
    except Exception as e:
        log_step_message(step_index, f"Critical error: {e}", "error")
        complete_workflow_step(step_index, "failed")
        raise
```

### Progress Tracking

```python
def step_with_progress():
    step_index = 2
    start_workflow_step(step_index)
    
    tasks = ["Task A", "Task B", "Task C", "Task D"]
    
    for i, task in enumerate(tasks):
        log_step_message(step_index, f"Processing {task}...")
        
        # Simulate task execution
        time.sleep(1)
        
        # Report progress
        progress = ((i + 1) / len(tasks)) * 100
        log_step_message(step_index, f"Progress: {progress:.0f}%")
    
    complete_workflow_step(step_index, "completed")
    log_step_message(step_index, "All tasks completed!", "success")
```

## Performance Considerations

- Log messages are limited to last 50 entries per broadcast
- WebSocket connections are cleaned up automatically
- File serving is handled by Python's built-in HTTP server
- No persistent storage is used by default

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## Limitations

- Single workflow per visualizer instance
- No authentication/authorization built-in
- No persistent workflow history
- WebSocket connections limited by browser/server limits