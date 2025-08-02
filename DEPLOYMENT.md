# StepFlow Monitor - Container Deployment Guide

🚀 **One-Click Deployment with Podman/Docker Compose**

## 📋 Prerequisites

Choose one of the following container runtimes:

### Option 1: Podman (Recommended)
```bash
# Install Podman and Podman Compose
# On macOS
brew install podman podman-compose

# On Ubuntu/Debian
sudo apt update
sudo apt install podman podman-compose

# On CentOS/RHEL/Fedora
sudo dnf install podman podman-compose
```

### Option 2: Docker
```bash
# Install Docker and Docker Compose
# On macOS
brew install --cask docker

# On Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# On CentOS/RHEL/Fedora
sudo dnf install docker docker-compose
```

## 🚀 Quick Start

### Method 1: One-Click Script (Recommended)

```bash
# Deploy StepFlow Monitor with test data
./deploy.sh

# Other useful commands
./deploy.sh status    # Check service status
./deploy.sh logs      # View real-time logs
./deploy.sh restart   # Restart service
./deploy.sh stop      # Stop service
./deploy.sh clean     # Complete cleanup
```

### Method 2: Manual Podman Compose

```bash
# Build and start
podman-compose up --build -d

# Or with newer podman versions
podman compose up --build -d

# Check status
podman-compose ps

# View logs
podman-compose logs -f stepflow-monitor

# Stop
podman-compose down
```

### Method 3: Manual Docker Compose

```bash
# Build and start
docker-compose up --build -d

# Or with newer docker versions  
docker compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f stepflow-monitor

# Stop
docker-compose down
```

## 📊 Service Access

After deployment, the following services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8080 | Main monitoring interface |
| **History** | http://localhost:8080/history | Execution history browser |
| **API Health** | http://localhost:8080/api/health | Health check endpoint |
| **API Docs** | http://localhost:8080/api | REST API endpoints |

## 🔧 Configuration

### Environment Variables

You can customize the deployment by modifying `docker-compose.yml`:

```yaml
environment:
  - STEPFLOW_ENV=production          # Environment mode
  - STEPFLOW_HOST=0.0.0.0           # Bind host
  - STEPFLOW_PORT=8080              # HTTP port
  - STEPFLOW_WS_PORT=8765           # WebSocket port
  - STEPFLOW_LOG_LEVEL=INFO         # Log level
```

### Port Configuration

To change ports, update the `ports` section in `docker-compose.yml`:

```yaml
ports:
  - "9090:8080"    # Change web port to 9090
  - "9091:8765"    # Change WebSocket port to 9091
```

### Data Persistence

Data is automatically persisted using Docker volumes:
- `stepflow-data`: Contains SQLite database and file artifacts
- `stepflow-logs`: Contains application logs

## 📁 File Structure

```
StepFlow_Monitor/
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Service orchestration
├── deploy.sh                  # One-click deployment script
├── requirements.txt           # Python dependencies
├── .dockerignore              # Build optimization
├── app/                       # Application code
├── generate_complete_test_data.py  # Test data generator
└── storage/                   # Runtime data (created automatically)
    ├── database/              # SQLite database
    ├── executions/            # Step logs
    └── artifacts/             # File artifacts
```

## 🧪 Test Data

The container automatically generates **300+ test executions** on first startup, including:

- ✅ **Diverse execution types**: Data pipelines, ML training, web scraping, etc.
- ✅ **Varied step counts**: 3-15 steps per execution
- ✅ **Mixed outcomes**: Success, failure, and error scenarios
- ✅ **Multiple artifacts**: 1-3 artifacts per execution
- ✅ **Realistic durations**: From seconds to hours

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
./deploy.sh logs

# Or manually
podman-compose logs stepflow-monitor
```

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8080

# Kill the process or change port in docker-compose.yml
```

### Permission Issues (Podman)

```bash
# Enable user namespaces
echo 'user.max_user_namespaces=28633' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Or run with sudo
sudo podman-compose up --build -d
```

### Database Issues

```bash
# Reset data volume
./deploy.sh clean
./deploy.sh deploy
```

## 🔧 Development Mode

For development with live code reloading:

```bash
# Mount source code as volume
podman run -it --rm \
  -p 8080:8080 -p 8765:8765 \
  -v $(pwd):/app \
  -v stepflow-data:/app/storage \
  stepflow-monitor:latest
```

## 📈 Performance Monitoring

### Resource Usage

```bash
# Monitor container resources
podman stats stepflow-monitor

# Or with Docker
docker stats stepflow-monitor
```

### Application Metrics

```bash
# Health check
curl http://localhost:8080/api/health

# Performance metrics
curl http://localhost:8080/api/health/metrics

# System overview
curl http://localhost:8080/api/executions/statistics
```

## 🔄 Updates

```bash
# Pull latest changes and rebuild
git pull
./deploy.sh clean
./deploy.sh deploy
```

## 🗑️ Cleanup

```bash
# Stop and remove everything
./deploy.sh clean

# Or manually
podman-compose down -v --rmi all
```

## 📞 Support

If you encounter issues:

1. Check the [troubleshooting section](#🔍-troubleshooting)
2. View container logs: `./deploy.sh logs`
3. Verify service health: `./deploy.sh status`
4. Reset environment: `./deploy.sh clean && ./deploy.sh deploy`

---

🎉 **Enjoy monitoring your executions with StepFlow Monitor!**