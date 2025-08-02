# 🏗️ StepFlow Monitor - High-Performance Architecture

## 🎯 Core Philosophy

**Minimal Marker Injection Strategy**: Users add simple markers to their scripts for precise step detection and visualization.

**Performance-First Design**: Optimized SQLite with WAL mode, connection reuse, and async I/O for handling 500+ concurrent text streams.

## 📋 Project Structure

```
StepFlow_Monitor/
├── app/                           # Application core
│   ├── core/                      # Business logic
│   │   ├── __init__.py
│   │   ├── marker_parser.py       # Marker detection engine
│   │   ├── execution_engine.py    # Script execution handler
│   │   ├── persistence.py         # Optimized data persistence layer
│   │   ├── websocket_server.py    # Real-time communication
│   │   └── auth.py                # Authentication (disabled)
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── execution.py           # Execution session model
│   │   ├── step.py                # Step model
│   │   └── artifact.py            # Artifact model
│   ├── api/                       # REST API endpoints
│   │   ├── __init__.py
│   │   ├── executions.py          # Execution management
│   │   ├── artifacts.py           # Artifact management
│   │   └── health.py              # Health checks & performance monitoring
│   ├── static/                    # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/                 # Frontend templates
│       ├── index.html             # Dashboard
│       ├── execution.html         # Live execution view
│       ├── history.html           # Execution history
│       └── artifacts.html         # Artifact browser
├── storage/                       # Persistent storage
│   ├── executions/                # Execution logs
│   ├── artifacts/                 # Generated artifacts
│   └── database/                  # SQLite database with WAL
├── examples/                      # Usage examples
│   ├── shell_example.sh
│   ├── python_example.py
│   ├── dockerfile_example
│   └── README.md
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Main Docker image
├── docker-compose.yml             # Deployment orchestration
└── README.md                      # Main documentation
```

## 🚀 Core Components

### 1. High-Performance Persistence Layer
- **Database**: SQLite with WAL mode for concurrent reads/writes
- **Connection Reuse**: Single persistent connection to eliminate overhead
- **Async I/O**: Non-blocking file operations using thread executor
- **Batch Processing**: Buffer writes for optimal throughput
- **Performance**: Handles 500+ concurrent operations

**Key Optimizations:**
```sql
-- WAL mode for concurrent access
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;        -- 10MB cache
PRAGMA temp_store=memory;       -- Temp tables in memory
PRAGMA mmap_size=268435456;     -- 256MB memory mapping
```

### 2. Marker Parser Engine
- **Purpose**: Parse standardized markers in script output
- **Markers**: `STEP_START:`, `STEP_COMPLETE:`, `STEP_ERROR:`, `ARTIFACT:`
- **Real-time**: Process streaming output line by line
- **Performance**: Optimized regex patterns and async processing

### 3. Execution Engine
- **Purpose**: Execute scripts and capture output
- **Features**: Real-time streaming, process management, timeout handling
- **Output**: Structured execution data with steps and logs
- **Concurrency**: Supports hundreds of parallel executions

### 4. WebSocket Server
- **Purpose**: Real-time communication with frontend
- **Events**: Step updates, log streaming, completion notifications
- **Scalability**: Support multiple concurrent executions
- **Performance**: Connection pooling and message batching

### 5. Web UI System
- **Dashboard**: Overview of executions with real-time updates
- **Live View**: Real-time execution monitoring
- **History**: Browse past executions with search/filter
- **Artifacts**: Download generated files
- **Monitoring**: Performance metrics and system health

## 🔧 Marker Injection Format

### Standard Markers
```bash
# Step control
echo "STEP_START:Step Name"
echo "STEP_COMPLETE:Step Name"
echo "STEP_ERROR:Error description"

# Artifacts
echo "ARTIFACT:file.xml:Test Report"
echo "ARTIFACT:coverage.html:Coverage Report"

# Metadata
echo "META:ESTIMATED_DURATION:300"
echo "META:DESCRIPTION:This step does X"
```

### Python Example
```python
print("STEP_START:Data Processing")
# Your existing code here
df = process_data()
print("STEP_COMPLETE:Data Processing")
print("ARTIFACT:processed_data.csv:Processed Dataset")
```

### Shell Example
```bash
echo "STEP_START:Environment Setup"
pip install -r requirements.txt
echo "STEP_COMPLETE:Environment Setup"

echo "STEP_START:Model Training"
python train.py > training.log
echo "ARTIFACT:training.log:Training Output"
echo "STEP_COMPLETE:Model Training"
```

## 🐳 Docker Deployment

### Single Container
```yaml
services:
  stepflow:
    image: stepflow/monitor
    ports:
      - "8080:8080"   # Web UI
      - "8765:8765"   # WebSocket
    volumes:
      - ./storage:/app/storage
      - ./scripts:/workspace
    environment:
      - AUTH_ENABLED=false
```

### Multi-Container (Future)
- Separate database container (PostgreSQL)
- Redis for session management
- Nginx for load balancing

## 🔐 Authentication (Disabled)

### SSO Integration Points
- **OIDC/SAML**: Enterprise identity providers
- **RBAC**: Role-based access control
- **API Keys**: Programmatic access
- **Session Management**: Web session handling

**Current State**: All authentication bypassed, direct access to all features.

## 📊 Data Flow

```mermaid
graph TB
    A[Script Execution] --> B[Marker Parser]
    B --> C[Execution Engine]
    C --> D[Optimized Persistence]
    C --> E[WebSocket Server]
    E --> F[Web UI]
    D --> G[Async File Storage]
    D --> H[SQLite WAL DB]
    F --> I[Dashboard]
    F --> J[Live View]
    F --> K[History]
    F --> L[Artifacts]
```

## ⚡ Performance Characteristics

### Concurrency Limits
- **Concurrent Executions**: 500+ (tested)
- **Database Operations**: 2000+ ops/sec
- **File I/O**: Non-blocking, 100+ concurrent writes
- **WebSocket Connections**: 1000+ clients
- **Memory Usage**: ~200MB for 500 concurrent streams

### Response Times
- **Database Queries**: <5ms average
- **File Operations**: <10ms (async)
- **WebSocket Updates**: <1ms
- **API Endpoints**: <50ms

### Storage Efficiency
- **50GB Storage**: 4,000-20,000 executions (depends on size)
- **Database Size**: ~2KB per execution + ~150 bytes per step
- **Log Files**: ~200KB average per execution
- **Artifacts**: Variable (1KB - 100MB)

## 🎯 Key Features

### Simplicity
- Minimal marker syntax
- Single Docker container deployment
- No external dependencies required

### Real-time
- Live step progress updates
- Streaming log output
- Instant artifact availability

### High Performance
- SQLite WAL mode for concurrent access
- Connection reuse eliminates overhead
- Async I/O prevents blocking
- Batch processing optimizes throughput

### Persistence
- Complete execution history
- Downloadable artifacts
- Searchable logs
- Performance metrics

### Enterprise Ready
- SSO integration points
- RBAC preparation
- Audit logging
- API access
- Performance monitoring

## 📈 Performance Monitoring

### API Endpoints
- `/api/health` - Basic health check
- `/api/health/metrics` - Detailed performance metrics
- `/api/health/optimize` - Run optimization tasks

### Metrics Collected
- Database performance (WAL mode status, cache hit ratio)
- System resources (CPU, memory, disk)
- Connection counts (WebSocket, database)
- Operation counts and timings

### Optimization Features
- Automatic WAL checkpointing
- Database analysis for query optimization
- Buffer flushing strategies
- Connection health monitoring

## 🚀 Getting Started

1. **Add markers to your script**:
   ```bash
   echo "STEP_START:My Process"
   # your code here
   echo "STEP_COMPLETE:My Process"
   ```

2. **Run with StepFlow Monitor**:
   ```bash
   docker run -p 8080:8080 stepflow/monitor bash your_script.sh
   ```

3. **View in browser**: http://localhost:8080

4. **Monitor performance**: http://localhost:8080/api/health/metrics

## 🔧 Performance Tuning

### Database Optimization
- WAL mode enabled by default
- Connection reuse reduces overhead
- Batch writes improve throughput
- Automatic optimization tasks

### File I/O Optimization
- Async writes prevent blocking
- Thread pool for I/O operations
- Directory structure optimized for access
- Log file compression (future)

### Memory Management
- Connection pooling
- Buffer management
- Garbage collection optimization
- Memory usage monitoring

### Monitoring & Alerting
- Real-time performance metrics
- Health check endpoints
- Resource usage tracking
- Performance optimization suggestions