# 📡 StepFlow Monitor - API Reference

## 🌐 Base URL

```
http://localhost:8080/api
```

## 🔐 Authentication

Currently **disabled** by default. All endpoints are publicly accessible.

## 📋 Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "data": { /* response data */ },
  "error": null,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Error responses:
```json
{
  "success": false,
  "data": null,
  "error": "Error description",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🏃 Executions API

### List Executions
```http
GET /api/executions
```

**Query Parameters:**
- `limit` (int): Number of results (default: 100, max: 1000)
- `offset` (int): Pagination offset (default: 0)
- `status` (string): Filter by status (`pending`, `running`, `completed`, `failed`, `cancelled`)
- `user` (string): Filter by user name

**Response:**
```json
{
  "success": true,
  "data": {
    "executions": [
      {
        "id": "uuid-string",
        "name": "Execution Name",
        "command": "python script.py",
        "working_directory": "/workspace",
        "status": "completed",
        "exit_code": 0,
        "error_message": null,
        "created_at": "2024-01-15T10:00:00Z",
        "started_at": "2024-01-15T10:00:05Z",
        "completed_at": "2024-01-15T10:15:30Z",
        "environment": {},
        "user": "developer",
        "tags": ["ml", "training"],
        "total_steps": 5,
        "completed_steps": 5,
        "current_step_index": 4,
        "duration_seconds": 925,
        "progress_percentage": 100.0,
        "metadata": {}
      }
    ],
    "total_count": 150,
    "has_more": true
  }
}
```

### Get Execution Details
```http
GET /api/executions/{execution_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution": { /* execution object */ },
    "steps": [
      {
        "id": "step-uuid",
        "execution_id": "execution-uuid",
        "name": "Step Name",
        "description": "Step description",
        "index": 0,
        "status": "completed",
        "exit_code": 0,
        "error_message": null,
        "created_at": "2024-01-15T10:00:00Z",
        "started_at": "2024-01-15T10:00:05Z",
        "completed_at": "2024-01-15T10:02:30Z",
        "estimated_duration": 120.0,
        "stop_on_error": false,
        "duration_seconds": 145.0,
        "metadata": {}
      }
    ],
    "artifacts": [
      {
        "id": "artifact-uuid",
        "execution_id": "execution-uuid",
        "step_id": "step-uuid",
        "name": "Output Report",
        "description": "Generated report",
        "file_path": "/storage/artifacts/...",
        "file_name": "report.html",
        "file_size": 2048,
        "mime_type": "text/html",
        "artifact_type": "document",
        "created_at": "2024-01-15T10:02:30Z",
        "tags": ["report"],
        "is_public": true,
        "retention_days": 30,
        "download_url": "/api/artifacts/artifact-uuid/download"
      }
    ]
  }
}
```

### Create Execution
```http
POST /api/executions
```

**Request Body:**
```json
{
  "name": "My Script Execution",
  "command": "python train_model.py",
  "working_directory": "/workspace",
  "environment": {
    "PYTHON_PATH": "/usr/bin/python",
    "MODEL_TYPE": "neural_network"
  },
  "tags": ["ml", "training"],
  "metadata": {
    "project": "image_classification",
    "version": "1.0"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "new-execution-uuid",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Delete Execution
```http
DELETE /api/executions/{execution_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Execution deleted successfully"
  }
}
```

## 📁 Artifacts API

### List Artifacts
```http
GET /api/artifacts
```

**Query Parameters:**
- `execution_id` (string): Filter by execution ID
- `step_id` (string): Filter by step ID
- `artifact_type` (string): Filter by type (`document`, `image`, `data`, `log`, `archive`, `other`)
- `limit` (int): Number of results (default: 100)
- `offset` (int): Pagination offset (default: 0)

### Get Artifact Details
```http
GET /api/artifacts/{artifact_id}
```

### Download Artifact
```http
GET /api/artifacts/{artifact_id}/download
```

**Response:**
- Binary file content
- Appropriate Content-Type header
- Content-Disposition header for filename

### Upload Artifact
```http
POST /api/artifacts
```

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `execution_id` (string): Required
- `step_id` (string): Optional
- `name` (string): Required
- `description` (string): Optional
- `artifact_type` (string): Optional
- `tags` (array): Optional
- `file` (file): Required

### Delete Artifact
```http
DELETE /api/artifacts/{artifact_id}
```

## 🏥 Health & Monitoring API

### Basic Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0",
    "uptime_seconds": 86400,
    "database": "connected",
    "websocket": "running",
    "storage": "accessible"
  }
}
```

### System Status
```http
GET /api/health/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "system": {
      "cpu_percent": 25.3,
      "memory_percent": 45.8,
      "disk_usage_percent": 67.2,
      "load_average": [1.2, 1.5, 1.8]
    },
    "database": {
      "status": "connected",
      "size_mb": 15.6,
      "wal_mode": true,
      "cache_hit_ratio": 0.95
    },
    "websocket": {
      "status": "running",
      "connected_clients": 125,
      "total_messages": 50000
    }
  }
}
```

### Performance Metrics
```http
GET /api/health/metrics
```

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2024-01-15T10:30:00Z",
    "database": {
      "database_size_bytes": 16384000,
      "database_size_mb": 15.6,
      "table_counts": {
        "executions": 1250,
        "steps": 8500,
        "artifacts": 3200
      },
      "wal_mode": "wal",
      "cache_size": 10000,
      "storage_path": "/app/storage"
    },
    "system": {
      "cpu_percent": 25.3,
      "memory_percent": 45.8,
      "disk_usage_percent": 67.2,
      "open_connections": 125
    },
    "uptime_seconds": 86400
  }
}
```

### Database Statistics
```http
GET /api/health/database
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_executions": 1250,
    "running_executions": 25,
    "completed_executions": 1100,
    "failed_executions": 125,
    "total_steps": 8500,
    "total_artifacts": 3200,
    "database_size_mb": 15.6,
    "oldest_execution": "2024-01-01T00:00:00Z",
    "newest_execution": "2024-01-15T10:25:00Z"
  }
}
```

### Optimize Performance
```http
POST /api/health/optimize
```

Triggers database optimization tasks and returns updated metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "optimization_completed",
    "timestamp": "2024-01-15T10:30:00Z",
    "operations_performed": [
      "ANALYZE tables",
      "WAL checkpoint",
      "Cache refresh"
    ],
    "metrics": { /* updated performance metrics */ }
  }
}
```

## 🔌 WebSocket API

### Connection
```
ws://localhost:8765
```

### Message Format
All WebSocket messages follow this format:

```json
{
  "type": "message_type",
  "data": { /* message data */ },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Message Types

#### Connection Established
```json
{
  "type": "connection_established",
  "data": {
    "client_id": 12345,
    "server_time": "2024-01-15T10:30:00Z",
    "connected_clients": 125
  }
}
```

#### Execution Started
```json
{
  "type": "execution_started",
  "data": {
    "execution_id": "uuid-string",
    "name": "Execution Name",
    "command": "python script.py",
    "started_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Step Update
```json
{
  "type": "step_update",
  "data": {
    "execution_id": "uuid-string",
    "step": {
      "id": "step-uuid",
      "name": "Step Name",
      "status": "running",
      "index": 2,
      "started_at": "2024-01-15T10:30:05Z"
    }
  }
}
```

#### Log Entry
```json
{
  "type": "log_entry",
  "data": {
    "execution_id": "uuid-string",
    "step_id": "step-uuid",
    "content": "Processing data...",
    "timestamp": "2024-01-15T10:30:06Z",
    "level": "info"
  }
}
```

#### Execution Completed
```json
{
  "type": "execution_completed",
  "data": {
    "execution_id": "uuid-string",
    "status": "completed",
    "exit_code": 0,
    "completed_at": "2024-01-15T10:45:00Z",
    "duration_seconds": 900,
    "total_steps": 5,
    "artifacts_count": 3
  }
}
```

#### Artifact Created
```json
{
  "type": "artifact_created",
  "data": {
    "execution_id": "uuid-string",
    "artifact": {
      "id": "artifact-uuid",
      "name": "Output Report",
      "file_name": "report.html",
      "download_url": "/api/artifacts/artifact-uuid/download"
    }
  }
}
```

#### Error
```json
{
  "type": "error",
  "data": {
    "execution_id": "uuid-string",
    "error_message": "Script execution failed",
    "error_code": "EXECUTION_ERROR",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

### Client Commands

#### Subscribe to Execution
```json
{
  "type": "subscribe",
  "data": {
    "execution_id": "uuid-string"
  }
}
```

#### Unsubscribe from Execution
```json
{
  "type": "unsubscribe",
  "data": {
    "execution_id": "uuid-string"
  }
}
```

#### Request Status
```json
{
  "type": "get_status",
  "data": {
    "execution_id": "uuid-string"
  }
}
```

## 📊 Status Codes

### HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Execution Status Values
- `pending` - Execution queued but not started
- `running` - Currently executing
- `completed` - Finished successfully
- `failed` - Finished with error
- `cancelled` - Manually cancelled

### Step Status Values
- `pending` - Step not started
- `running` - Currently executing
- `completed` - Finished successfully
- `failed` - Finished with error
- `skipped` - Skipped due to condition

### Artifact Types
- `document` - Text documents, reports
- `image` - Images, plots, diagrams
- `data` - Data files, CSV, JSON
- `log` - Log files
- `archive` - ZIP, TAR files
- `other` - Other file types

## 🔧 Configuration

### Environment Variables
- `STEPFLOW_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `STEPFLOW_STORAGE_PATH` - Storage directory path
- `STEPFLOW_WEBSOCKET_HOST` - WebSocket server host
- `STEPFLOW_WEBSOCKET_PORT` - WebSocket server port
- `STEPFLOW_AUTH_ENABLED` - Enable authentication (true/false)

### Rate Limiting
Currently not implemented. All endpoints have unlimited access.

### CORS
Configured to allow all origins in development mode.

## 📝 Examples

### Python Client Example
```python
import requests
import websocket
import json

# Create execution
response = requests.post('http://localhost:8080/api/executions', json={
    "name": "Test Execution",
    "command": "python test.py",
    "tags": ["test"]
})
execution_id = response.json()['data']['execution_id']

# WebSocket connection
def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data['type']}")

ws = websocket.WebSocketApp("ws://localhost:8765",
                           on_message=on_message)
ws.run_forever()
```

### JavaScript Client Example
```javascript
// REST API
const response = await fetch('/api/executions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: 'Test Execution',
        command: 'npm test',
        tags: ['test']
    })
});
const result = await response.json();

// WebSocket
const ws = new WebSocket('ws://localhost:8765');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data.type, data.data);
};
```

### Curl Examples
```bash
# List executions
curl "http://localhost:8080/api/executions?limit=10&status=completed"

# Get execution details
curl "http://localhost:8080/api/executions/uuid-string"

# Create execution
curl -X POST "http://localhost:8080/api/executions" \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","command":"echo hello"}'

# Download artifact
curl "http://localhost:8080/api/artifacts/artifact-uuid/download" \
     --output report.html

# Health check
curl "http://localhost:8080/api/health"

# Performance metrics
curl "http://localhost:8080/api/health/metrics"
```