# ContainerFlow Visualizer Examples

This directory contains example implementations and demo servers for the ContainerFlow Visualizer.

## Files

### Demo Server
- `web_demo_server.py` - Complete WebSocket demo server with real-time workflow visualization
- `start_demo.sh` - Convenient script to start the demo with port cleanup

### File Server  
- `serve_files.py` - Independent file server for accessing generated files after demo ends

### Integration Examples
- `basic_integration_example.py` - Basic integration example
- `workflow_integration_example.py` - Advanced workflow integration

## Quick Start

### 1. Run the Interactive Demo
```bash
./examples/start_demo.sh
```
Then open: http://localhost:9000/visualizer.html

### 2. Access Generated Files (After Demo)
After running the demo, you can access the generated files even after the server stops:

```bash
# Start independent file server
python3 examples/serve_files.py

# Or on a different port
python3 examples/serve_files.py --port 8081
```

Then open: http://localhost:8080

## Generated Files

The demo generates these files during execution:

### Artifact Files (after test step completion)
- `pytest-report.xml` - PyTest execution report
- `test-results.xml` - Test results in XML format  
- `coverage.xml` - Code coverage report

### Complete Log (after all steps completion)
- `execution_output.log` - Complete workflow execution log

## File Access Methods

### Method 1: During Demo
While the demo is running, files are available at:
- http://localhost:9000/downloads/filename.xml

### Method 2: After Demo (Independent Server)
After demo stops, use the independent file server:
```bash
python3 examples/serve_files.py
```
Files available at:
- http://localhost:8080/filename.xml
- http://localhost:8080/ (file browser)

### Method 3: Direct File Access
Files are stored in: `web_interface/downloads/`
```bash
ls -la web_interface/downloads/
```

## Port Information

- **Demo Server**: HTTP: 9000, WebSocket: 8765
- **File Server**: 8080 (configurable)
- **Auto Port Selection**: Both servers will try alternative ports if default is occupied

## Troubleshooting

### Port Already in Use
```bash
# Kill processes on port 9000
lsof -ti:9000 | xargs kill -9

# Or use the cleanup in start_demo.sh
./examples/start_demo.sh
```

### Files Not Found
```bash
# Check if files exist
ls -la web_interface/downloads/

# Regenerate by running demo
./examples/start_demo.sh
```