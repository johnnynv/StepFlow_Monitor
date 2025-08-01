# ContainerFlow Visualizer Examples

This directory contains example scripts demonstrating the marker injection strategy for step visualization.

## 🎯 Marker Injection Strategy

ContainerFlow uses **minimal markers** that you add to your existing scripts to enable step-by-step visualization. The markers are simple echo/print statements that don't interfere with your script logic.

## 📋 Marker Types

### Step Control Markers
- `STEP_START:Name` - Marks the beginning of a step
- `STEP_COMPLETE:Name` - Marks successful completion
- `STEP_ERROR:Description` - Marks step failure

### Artifact Markers
- `ARTIFACT:file_path:description` - Declares generated files as artifacts

### Metadata Markers
- `META:key:value` - Provides additional step metadata

## 🚀 Running Examples

### Shell Script Example
```bash
# Make executable
chmod +x examples/shell_example.sh

# Run with ContainerFlow
docker run -p 8080:8080 -p 8765:8765 \
  -v $(pwd)/examples:/workspace \
  containerflow/visualizer \
  bash /workspace/shell_example.sh
```

### Python Script Example
```bash
# Run with ContainerFlow
docker run -p 8080:8080 -p 8765:8765 \
  -v $(pwd)/examples:/workspace \
  containerflow/visualizer \
  python /workspace/python_example.py
```

### Docker Example
```bash
# Build with visualization
docker run -p 8080:8080 -p 8765:8765 \
  -v $(pwd)/examples:/workspace \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containerflow/visualizer \
  docker build -t myapp /workspace/dockerfile_example/
```

## 🌐 Viewing Results

1. **Open your browser**: http://localhost:8080
2. **Dashboard**: Overview of all executions
3. **Live View**: Real-time execution monitoring
4. **History**: Browse past executions
5. **Artifacts**: Download generated files

## 📊 What You'll See

- **Real-time step progress** with GitHub Actions-style visualization
- **Live log streaming** for each step
- **Artifact collection** and download links
- **Execution statistics** and history
- **Error handling** and failure detection

## 🔧 Integration Best Practices

### Minimal Impact
```bash
# Before
pip install -r requirements.txt
python train_model.py

# After - just add markers
echo "STEP_START:Environment Setup"
pip install -r requirements.txt
echo "STEP_COMPLETE:Environment Setup"

echo "STEP_START:Model Training" 
python train_model.py
echo "ARTIFACT:model.pkl:Trained Model"
echo "STEP_COMPLETE:Model Training"
```

### Error Handling
```bash
# Detect and report failures
if ! python risky_operation.py; then
    echo "STEP_ERROR:Risky operation failed with exit code $?"
    exit 1
fi
```

### Metadata Enhancement
```bash
echo "STEP_START:Long Running Task"
echo "META:ESTIMATED_DURATION:300"
echo "META:DESCRIPTION:This step processes large datasets"
# Your existing code here
```

## 🐳 Docker Integration

ContainerFlow works seamlessly with Docker workflows:

```bash
# Dockerfile with markers
FROM python:3.9
RUN echo "STEP_START:Base Image Setup"
RUN echo "STEP_COMPLETE:Base Image Setup"

COPY requirements.txt .
RUN echo "STEP_START:Dependencies Installation"
RUN pip install -r requirements.txt
RUN echo "STEP_COMPLETE:Dependencies Installation"

COPY . .
RUN echo "STEP_START:Application Setup"
RUN python setup.py build
RUN echo "ARTIFACT:dist/:Build Artifacts"
RUN echo "STEP_COMPLETE:Application Setup"
```

## 📈 Advanced Features

### Conditional Steps
```bash
if [ "$ENVIRONMENT" == "production" ]; then
    echo "STEP_START:Production Deployment"
    # Production-specific steps
    echo "STEP_COMPLETE:Production Deployment"
else
    echo "STEP_START:Development Setup"
    # Development-specific steps
    echo "STEP_COMPLETE:Development Setup"
fi
```

### Parallel Processing
```bash
echo "STEP_START:Parallel Data Processing"
echo "META:DESCRIPTION:Processing multiple datasets in parallel"

# Start background jobs
python process_dataset_1.py &
python process_dataset_2.py &
python process_dataset_3.py &

# Wait for completion
wait

echo "ARTIFACT:results/:Processing Results"
echo "STEP_COMPLETE:Parallel Data Processing"
```

## 🎯 Zero-Modification Alternative

If you cannot modify your scripts, ContainerFlow also supports **zero-modification** mode with heuristic pattern detection. However, marker injection provides much more accurate step detection and artifact collection.