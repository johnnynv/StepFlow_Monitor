# 🐳 ContainerFlow Visualizer

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/your-repo/containerflow-visualizer)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-brightgreen.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://docker.com)

## Professional Container Execution Workflow Visualization

A lightweight, real-time visualization tool for monitoring container execution workflows with GitHub Actions-style interface.

[🇺🇸 English](docs/README_EN.md) | [🇨🇳 中文](docs/README_CN.md)

## ✨ Key Features

- **🚀 Zero Configuration**: Single command deployment
- **📱 Real-time Visualization**: GitHub Actions-style step monitoring  
- **🔄 Live WebSocket Streaming**: Real-time log updates
- **🎨 Modern Responsive UI**: Works on desktop and mobile
- **🐳 Docker Native**: Perfect Docker workflow integration
- **📊 Progress Tracking**: Real-time execution monitoring
- **🏗️ Modular Architecture**: Separated concerns for maintainability

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Python Script │ ◄──────────────► │   Web Interface │
│ (Step Control)   │                 │ (Visualization) │
└─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐    HTTP Service ┌─────────────────┐
│  Docker Container│ ◄──────────────► │   Browser       │
│ (Computing Tasks)│                 │ (User Interface)│
└─────────────────┘                 └─────────────────┘
```

## 🚀 Quick Start

### Method 1: Direct Python Execution

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the visualizer
python container_flow_visualizer.py

# 3. Open browser
# Visit: http://localhost:8080/visualizer.html
```

### Method 2: Docker Deployment

```bash
# 1. Generate Docker configuration
python deployment/docker_integration.py

# 2. Start services
chmod +x deploy_containerflow.sh
./deploy_containerflow.sh

# 3. Access interface
# Auto-opens: http://localhost:8080/visualizer.html
```

### Method 3: Integration Example

```bash
# Run a comprehensive workflow example
python examples/workflow_integration_example.py

# Or run basic integration
python examples/basic_integration_example.py
```

## 📋 Integration Guide

### Step 1: Add Visualization Code

```python
from core import create_visualizer, add_workflow_step, start_visualization_service
import threading

# Initialize visualizer
viz = create_visualizer(http_port=8080, websocket_port=8765)

# Define steps
add_workflow_step("Environment Setup", "Configure Python and scientific computing environment")
add_workflow_step("Data Download", "Download required datasets")
add_workflow_step("Jupyter Execution", "Run data analysis notebook")
add_workflow_step("Test Execution", "Run pytest and generate reports")
add_workflow_step("Report Generation", "Generate final report files")
```

### Step 2: Add Status Updates to Existing Functions

```python
def your_existing_function():
    # Start step
    start_workflow_step(0)  # Step index
    log_step_message(0, "Starting environment setup...")
    
    try:
        # Your existing code
        setup_environment()
        
        # Add progress logs
        log_step_message(0, "Installing scientific packages...")
        install_packages()
        
        log_step_message(0, "Configuring Jupyter environment...")
        setup_jupyter()
        
        # Complete step
        complete_workflow_step(0, "completed")
        log_step_message(0, "✅ Environment setup completed!", "success")
        
    except Exception as e:
        complete_workflow_step(0, "failed")
        log_step_message(0, f"❌ Setup failed: {str(e)}", "error")
```

### Step 3: Start Visualization Service

```python
# Run workflow in background thread
workflow_thread = threading.Thread(target=your_workflow, daemon=True)
workflow_thread.start()

# Start visualizer (main thread)
start_visualization_service()
```

## 🖥️ Interface Features

### 📊 Real-time Monitoring Panel
- **Progress Bar**: Shows overall execution progress
- **Statistics**: Current step, total steps, completed, execution time
- **Step Status**: Detailed status and duration for each step

### 📜 Real-time Logs
- **Color Coding**: info(blue), success(green), warning(yellow), error(red)
- **Timestamps**: Precise timestamp for each log entry
- **Auto-scroll**: New logs automatically scroll to bottom
- **Search Filter**: (future feature)

### 🔄 Status Indicators
- **⏳ Pending**: Waiting for execution
- **🔄 Running**: Currently executing (with animation)
- **✅ Completed**: Successfully finished
- **❌ Failed**: Execution failed

## 📁 Project Structure

```
ContainerFlow_Visualizer/
├── core/                           # Core visualization modules
│   ├── __init__.py                # Package initialization  
│   ├── visualizer.py              # Main ContainerFlowVisualizer class
│   └── api.py                     # Convenience API functions
├── web_interface/                  # Separated web interface
│   ├── visualizer.html            # Main HTML interface
│   ├── styles.css                 # CSS styling
│   └── visualizer.js              # Client-side JavaScript
├── examples/                       # Usage examples and demos
│   ├── basic_integration_example.py
│   └── workflow_integration_example.py  
├── deployment/                     # Deployment and Docker tools
│   ├── docker_integration.py      # Docker deployment utilities
│   └── production_workflow_example.py
├── docs/                          # Comprehensive documentation
│   ├── README_EN.md               # English documentation
│   ├── README_CN.md               # Chinese documentation  
│   ├── API_REFERENCE.md           # API documentation
│   ├── DEPLOYMENT_GUIDE.md        # Deployment guide
│   └── EXAMPLES_GUIDE.md          # Examples and tutorials
├── container_flow_visualizer.py   # Main entry point
├── requirements.txt               # Python dependencies
└── README.md                      # Project overview
```

## 🔧 Configuration Options

### Port Configuration
```python
# Custom ports
viz = create_visualizer(
    http_port=8080,          # HTTP server port
    websocket_port=8765      # WebSocket port
)
```

### Log Levels
```python
# Different log levels
log_step_message(step_index, "Normal info", "info")      # Blue
log_step_message(step_index, "Success info", "success")  # Green  
log_step_message(step_index, "Warning info", "warning")  # Yellow
log_step_message(step_index, "Error info", "error")      # Red
```

## 🛠️ Advanced Usage

### Custom Step Descriptions
```python
add_workflow_step("Data Preprocessing", "Clean and transform raw datasets, handle missing values")
add_workflow_step("Feature Engineering", "Extract and select the most important feature variables")
add_workflow_step("Model Training", "Train machine learning models and optimize parameters")
```

### Error Handling
```python
try:
    risky_operation()
    complete_workflow_step(step_index, "completed")
except SpecificError as e:
    log_step_message(step_index, f"Specific error: {e}", "warning")
    complete_workflow_step(step_index, "completed")  # Continue execution
except Exception as e:
    log_step_message(step_index, f"Critical error: {e}", "error") 
    complete_workflow_step(step_index, "failed")     # Stop execution
    return False
```

### Progress Breakdown
```python
def complex_step():
    start_workflow_step(2)
    
    subtasks = ["Subtask 1", "Subtask 2", "Subtask 3"]
    for i, task in enumerate(subtasks):
        log_step_message(2, f"Executing {task}...")
        execute_subtask(task)
        
        progress = ((i + 1) / len(subtasks)) * 100
        log_step_message(2, f"Progress: {progress:.0f}%")
    
    complete_workflow_step(2, "completed")
```

## 🚀 Deployment Recommendations

### Development Environment
```bash
# Direct execution for rapid iteration
python container_flow_visualizer.py
```

### Testing Environment  
```bash
# Single Docker container
docker build -t containerflow-viz .
docker run -p 8080:8080 -p 8765:8765 containerflow-viz
```

### Production Environment
```bash
# Docker Compose with persistence
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

**1. WebSocket Connection Failed**
```bash
# Check if port is in use
netstat -an | grep 8765

# Configure firewall
sudo ufw allow 8765
```

**2. Browser Cannot Access**
```bash
# Check HTTP server
curl http://localhost:8080/visualizer.html

# Check Docker port mapping
docker ps | grep 8080
```

**3. Interface Not Updating**
- Refresh browser page
- Check WebSocket connection status
- Review browser developer console for errors

## 🎨 Interface Customization

### Modify Styles
Edit CSS styles in `web_interface/styles.css`:

```css
/* Custom color theme */
.step.running { 
    border-left-color: #your-color; 
    background: #your-bg-color;
}
```

### Add New Features
```python
# Custom message handling
def handle_custom_message(self, message):
    if message.type == 'custom':
        # Handle custom message
        pass
```

## 📊 Comparison with Other Solutions

| Feature | ContainerFlow | GitHub Actions | Jenkins | Tekton |
|---------|---------------|----------------|---------|--------|
| Deployment Complexity | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Learning Curve | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Real-time Visualization | ✅ | ✅ | ✅ | ✅ |
| Customization Level | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Docker Integration | ✅ | ✅ | ✅ | ✅ |
| Zero Configuration | ✅ | ❌ | ❌ | ❌ |
| Modular Architecture | ✅ | ❌ | ⭐⭐ | ⭐⭐⭐ |

## 📚 Documentation

- **[📖 API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[🚀 Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment guide  
- **[💡 Examples Guide](docs/EXAMPLES_GUIDE.md)** - Comprehensive examples
- **[🇺🇸 English Docs](docs/README_EN.md)** - Full English documentation
- **[🇨🇳 中文文档](docs/README_CN.md)** - Complete Chinese documentation

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to improve this solution!

## 📄 License

MIT License - Free to use and modify.

---

**🎉 Now you can monitor your container execution processes just like GitHub Actions!**