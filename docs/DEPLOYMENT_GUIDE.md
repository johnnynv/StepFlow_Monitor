# 📦 ContainerFlow Visualizer Deployment Guide

## Comprehensive Deployment and Production Setup

This guide covers various deployment scenarios from development to enterprise production environments.

## 🚀 Deployment Options

### 1. Development Environment

**Quick Local Setup**
```bash
# Clone or download the project
git clone https://github.com/your-repo/containerflow-visualizer.git
cd containerflow-visualizer

# Install dependencies
pip install -r requirements.txt

# Run directly
python container_flow_visualizer.py
```

**Access**: http://localhost:8080/visualizer.html

### 2. Docker Single Container

**Build and Run**
```bash
# Build the image
docker build -t containerflow-viz:latest .

# Run container
docker run -d \
  --name containerflow-visualizer \
  -p 8080:8080 \
  -p 8765:8765 \
  -v $(pwd)/workflow_results:/app/workflow_results \
  containerflow-viz:latest

# Check logs
docker logs -f containerflow-visualizer
```

### 3. Docker Compose (Recommended)

**Generate deployment files**
```bash
python deployment/docker_integration.py
```

**Start services**
```bash
# Make script executable
chmod +x deploy_containerflow.sh

# Deploy
./deploy_containerflow.sh
```

**Manual Docker Compose**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Production Kubernetes Deployment

**Create Kubernetes manifests**

`deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: containerflow-visualizer
  labels:
    app: containerflow-visualizer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: containerflow-visualizer
  template:
    metadata:
      labels:
        app: containerflow-visualizer
    spec:
      containers:
      - name: containerflow-visualizer
        image: containerflow-viz:latest
        ports:
        - containerPort: 8080
        - containerPort: 8765
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: workflow-results
          mountPath: /app/workflow_results
      volumes:
      - name: workflow-results
        persistentVolumeClaim:
          claimName: workflow-results-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: containerflow-service
spec:
  selector:
    app: containerflow-visualizer
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  - name: websocket
    port: 8765
    targetPort: 8765
  type: LoadBalancer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: workflow-results-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

**Deploy to Kubernetes**
```bash
kubectl apply -f deployment.yaml

# Check status
kubectl get pods,services

# Access logs
kubectl logs -f deployment/containerflow-visualizer
```

## 🔧 Environment Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CONTAINERFLOW_HTTP_PORT` | 8080 | HTTP server port |
| `CONTAINERFLOW_WS_PORT` | 8765 | WebSocket server port |
| `CONTAINERFLOW_WEB_DIR` | web_interface | Web interface directory |
| `CONTAINERFLOW_LOG_LEVEL` | INFO | Logging level |
| `PYTHONUNBUFFERED` | 1 | Python output buffering |

### Configuration File

Create `config.json`:
```json
{
  "server": {
    "http_port": 8080,
    "websocket_port": 8765,
    "host": "0.0.0.0"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  },
  "workflow": {
    "max_log_entries": 1000,
    "auto_cleanup": true,
    "results_directory": "workflow_results"
  }
}
```

## 🌐 Reverse Proxy Setup

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Apache Configuration

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    
    ProxyPreserveHost On
    ProxyRequests Off
    
    ProxyPass /ws ws://localhost:8765/
    ProxyPassReverse /ws ws://localhost:8765/
    
    ProxyPass / http://localhost:8080/
    ProxyPassReverse / http://localhost:8080/
</VirtualHost>
```

## 🔒 Security Considerations

### SSL/TLS Setup

**Generate SSL certificates**
```bash
# Using Let's Encrypt
certbot --nginx -d your-domain.com

# Or self-signed for development
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

**Nginx SSL Configuration**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Rest of configuration...
}
```

### Firewall Configuration

```bash
# Ubuntu/Debian
sudo ufw allow 8080/tcp
sudo ufw allow 8765/tcp
sudo ufw allow 443/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8765/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

## 📊 Monitoring and Logging

### Health Check Endpoint

Add to your application:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

### Log Aggregation

**Docker Compose with logging**
```yaml
version: '3.8'
services:
  containerflow-visualizer:
    # ... other configuration
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Centralized logging with ELK Stack**
```yaml
version: '3.8'
services:
  containerflow-visualizer:
    # ... other configuration
    depends_on:
      - elasticsearch
    logging:
      driver: "gelf"
      options:
        gelf-address: "udp://localhost:12201"
        
  elasticsearch:
    image: elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
      
  logstash:
    image: logstash:7.14.0
    # ... logstash configuration
    
  kibana:
    image: kibana:7.14.0
    ports:
      - "5601:5601"
```

## 🔄 Backup and Recovery

### Data Backup Strategy

**Automated backup script**
```bash
#!/bin/bash
# backup_containerflow.sh

BACKUP_DIR="/backup/containerflow"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup workflow results
tar -czf $BACKUP_DIR/workflow_results_$DATE.tar.gz workflow_results/

# Backup configuration
cp config.json $BACKUP_DIR/config_$DATE.json

# Backup database (if using one)
# docker exec containerflow-db mysqldump -u root -p database > $BACKUP_DIR/db_$DATE.sql

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.json" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Schedule with cron**
```bash
# Add to crontab
0 2 * * * /path/to/backup_containerflow.sh
```

## 🎯 Performance Optimization

### Resource Limits

**Docker Compose limits**
```yaml
version: '3.8'
services:
  containerflow-visualizer:
    image: containerflow-viz:latest
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Scaling Configuration

**Horizontal scaling with load balancer**
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - containerflow-viz-1
      - containerflow-viz-2
      
  containerflow-viz-1:
    image: containerflow-viz:latest
    environment:
      - INSTANCE_ID=1
      
  containerflow-viz-2:
    image: containerflow-viz:latest
    environment:
      - INSTANCE_ID=2
```

## 🚨 Troubleshooting

### Common Issues and Solutions

**1. Port Already in Use**
```bash
# Find process using port
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>

# Or change port in configuration
```

**2. WebSocket Connection Issues**
```bash
# Check WebSocket connectivity
wscat -c ws://localhost:8765

# Test with curl
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" http://localhost:8765
```

**3. Container Health Issues**
```bash
# Check container status
docker ps
docker logs containerflow-visualizer

# Enter container for debugging
docker exec -it containerflow-visualizer /bin/bash
```

**4. Performance Issues**
```bash
# Monitor resource usage
docker stats containerflow-visualizer

# Check system resources
htop
iostat -x 1
```

## 📋 Deployment Checklist

- [ ] Environment variables configured
- [ ] Ports are available and firewall configured
- [ ] SSL certificates installed (production)
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] Health checks enabled
- [ ] Log aggregation setup
- [ ] Resource limits configured
- [ ] Security measures in place
- [ ] Documentation updated

## 🆘 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Test connectivity: `curl http://localhost:8080/health`
4. Review resource usage: `docker stats`
5. Submit issue with logs and configuration details

---

**For additional deployment scenarios or enterprise support, please contact the development team.**