# StepFlow Monitor - Container Quick Start

🚀 **One-Click Container Deployment**

## Quick Deploy

```bash
# One command to rule them all
./deploy.sh
```

That's it! The system will:
- ✅ Auto-detect Podman or Docker
- ✅ Build the container image
- ✅ Generate 300+ test executions
- ✅ Start the web interface on http://localhost:8080

## Commands

```bash
./deploy.sh         # Deploy (default)
./deploy.sh status  # Check status
./deploy.sh logs    # View logs
./deploy.sh stop    # Stop service
./deploy.sh clean   # Complete cleanup
```

## What You Get

- 📊 **Web Dashboard**: http://localhost:8080
- 📋 **Execution History**: http://localhost:8080/history
- 🔍 **API Health**: http://localhost:8080/api/health
- 💾 **Persistent Data**: Automatic volume management
- 🧪 **Test Data**: 300+ sample executions pre-loaded

## Requirements

- Podman or Docker installed
- Ports 8080 and 8765 available

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed documentation.

---

**Happy monitoring!** 🎉