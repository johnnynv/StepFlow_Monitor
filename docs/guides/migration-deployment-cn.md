# 🚀 StepFlow Monitor - 迁移和部署指南

## 📋 目录

1. [概述](#概述)
2. [迁移策略](#迁移策略)
3. [迁移前检查清单](#迁移前检查清单)
4. [分步迁移](#分步迁移)
5. [部署选项](#部署选项)
6. [配置管理](#配置管理)
7. [性能调优](#性能调优)
8. [监控设置](#监控设置)
9. [回滚程序](#回滚程序)
10. [故障排除](#故障排除)

## 📊 概述

本指南为现有StepFlow Monitor安装迁移到优化的SQLite WAL实现以及部署新的高性能实例提供全面说明。

### 迁移好处
- **25-33倍性能提升**：并发操作
- **亚5ms数据库响应时间**
- **零停机迁移**：向后兼容
- **生产就绪可靠性**：增强监控

### 支持的迁移路径
- **传统SQLite** → SQLite WAL（推荐）
- **全新安装** → 优化部署
- **开发环境** → 生产部署
- **单实例** → 可扩展架构

## 🎯 迁移策略

### 零停机方法

SQLite WAL优化设计为**零停机迁移**，具有以下关键原则：

1. **向后兼容**：所有现有API保持不变
2. **渐进式转换**：WAL模式激活自动且透明
3. **数据保护**：迁移期间保留所有现有数据
4. **回滚安全**：需要时可恢复到之前状态

### 迁移时间表

```
迁移过程概览:
├── 阶段1: 准备 (10分钟)
├── 阶段2: 代码部署 (5分钟)
├── 阶段3: WAL激活 (2分钟)
├── 阶段4: 验证 (10分钟)
└── 阶段5: 监控 (持续)

总停机时间: 0分钟 (服务保持可用)
```

## ✅ 迁移前检查清单

### 环境要求

#### 系统要求
```bash
# 最小系统规格
操作系统: Linux/macOS/Windows
Python: 3.8+ (推荐3.13+)
内存: 最小512MB (推荐2GB+)
存储: 最小10GB (推荐SSD)
网络: 最小100Mbps

# 检查Python版本
python3 --version  # 应该是3.8+

# 检查可用内存
free -h  # Linux
vm_stat  # macOS

# 检查磁盘空间
df -h
```

#### 依赖验证
```bash
# 验证所需包
pip list | grep -E "(aiosqlite|aiohttp|asyncio)"

# 检查SQLite版本
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
# 应该是3.7.0+以支持WAL
```

### 数据备份策略

#### 1. 数据库备份
```bash
# 创建备份目录
mkdir -p backups/$(date +%Y%m%d_%H%M%S)

# 备份SQLite数据库
cp storage/database/stepflow.db backups/$(date +%Y%m%d_%H%M%S)/

# 验证备份完整性
sqlite3 backups/$(date +%Y%m%d_%H%M%S)/stepflow.db "PRAGMA integrity_check;"
```

#### 2. 文件系统备份
```bash
# 备份执行日志和工件
tar -czf backups/$(date +%Y%m%d_%H%M%S)/storage_backup.tar.gz storage/

# 验证备份大小
ls -lah backups/$(date +%Y%m%d_%H%M%S)/
```

#### 3. 配置备份
```bash
# 备份配置文件
cp -r app/ backups/$(date +%Y%m%d_%H%M%S)/app_backup/
cp requirements.txt backups/$(date +%Y%m%d_%H%M%S)/
cp docker-compose.yml backups/$(date +%Y%m%d_%H%M%S)/
```

### 环境健康检查

#### 数据库连接测试
```bash
# 测试数据库访问
python3 -c "
import sqlite3
conn = sqlite3.connect('storage/database/stepflow.db')
print('数据库可访问:', conn.execute('SELECT 1').fetchone()[0] == 1)
conn.close()
"
```

#### 服务健康检查
```bash
# 检查服务是否运行
curl -f http://localhost:8080/api/health || echo "服务无响应"

# 检查WebSocket连接
curl --include --no-buffer --header "Connection: Upgrade" \
     --header "Upgrade: websocket" --header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
     --header "Sec-WebSocket-Version: 13" \
     http://localhost:8765/
```

## 🔄 分步迁移

### 阶段1：准备

#### 1.1 停止应用程序（可选）
```bash
# 为了最大安全性，停止应用程序
# 注意：这是可选的，因为迁移支持零停机
pkill -f "python.*main.py" || echo "应用程序未运行"

# 或使用Docker
docker-compose down
```

#### 1.2 创建迁移环境
```bash
# 创建虚拟环境
python3 -m venv migration_env
source migration_env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 1.3 验证当前状态
```bash
# 检查当前数据库模式
sqlite3 storage/database/stepflow.db "PRAGMA journal_mode;"
# 应该返回: delete (或 truncate)

# 计算现有记录
sqlite3 storage/database/stepflow.db "
SELECT 
    '执行: ' || COUNT(*) FROM executions 
UNION ALL SELECT 
    '步骤: ' || COUNT(*) FROM steps 
UNION ALL SELECT 
    '工件: ' || COUNT(*) FROM artifacts;
"
```

### 阶段2：代码部署

#### 2.1 更新应用程序代码
```bash
# 拉取最新优化代码
git pull origin main

# 或手动替换文件
# 复制优化的 app/core/persistence.py
# 复制优化的 app/main.py
# 复制优化的 requirements.txt
```

#### 2.2 安装依赖
```bash
# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 验证安装
pip list | grep aiosqlite
```

#### 2.3 验证代码变更
```bash
# 运行语法检查
python3 -m py_compile app/main.py app/core/persistence.py

# 检查导入语句
python3 -c "
from app.core.persistence import PersistenceLayer
print('代码验证成功')
"
```

### 阶段3：WAL激活

#### 3.1 启动优化应用程序
```bash
# 使用详细日志启动
PYTHONPATH=. python3 app/main.py

# 监控WAL激活日志
tail -f logs/stepflow.log | grep -i wal
```

#### 3.2 验证WAL模式激活
```bash
# 检查WAL模式已激活（在另一个终端）
sqlite3 storage/database/stepflow.db "PRAGMA journal_mode;"
# 应该返回: wal

# 验证WAL文件存在
ls -la storage/database/stepflow.db*
# 应该显示: stepflow.db, stepflow.db-wal, stepflow.db-shm
```

#### 3.3 性能验证
```bash
# 快速性能测试
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8080/api/health"

# 预期: 总时间 < 5ms
```

### 阶段4：验证

#### 4.1 数据完整性检查
```bash
# 验证所有数据可访问
python3 -c "
import asyncio
import sys
sys.path.append('.')
from app.core.persistence import PersistenceLayer

async def verify_data():
    persistence = PersistenceLayer()
    await persistence.initialize()
    
    executions = await persistence.get_executions(limit=10)
    print(f'找到 {len(executions)} 个执行')
    
    if executions:
        steps = await persistence.get_steps(executions[0].id)
        print(f'第一个执行找到 {len(steps)} 个步骤')
    
    await persistence.close()
    print('数据完整性检查通过')

asyncio.run(verify_data())
"
```

#### 4.2 功能测试
```bash
# 测试执行创建
curl -X POST http://localhost:8080/api/executions \
     -H "Content-Type: application/json" \
     -d '{"name":"迁移测试","command":"echo hello","tags":["test"]}'

# 测试执行检索
curl http://localhost:8080/api/executions?limit=5
```

#### 4.3 性能基线
```bash
# 运行性能测试套件
python3 scripts/performance_test.py

# 预期结果:
# - API响应时间: < 5ms
# - 并发操作: 20+ 成功
# - 数据库操作: > 500 ops/sec
```

### 阶段5：生产就绪

#### 5.1 配置生产设置
```bash
# 设置生产环境变量
export STEPFLOW_LOG_LEVEL=INFO
export STEPFLOW_STORAGE_PATH=/app/storage
export STEPFLOW_AUTH_ENABLED=false  # 或 true 用于生产

# 更新配置
echo "生产配置已应用"
```

#### 5.2 设置监控
```bash
# 启用性能监控
curl http://localhost:8080/api/health/metrics

# 设置日志监控
tail -f logs/stepflow.log | grep -E "(ERROR|WARNING|performance)"
```

## 🐳 部署选项

### 选项1：Docker部署（推荐）

#### Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  stepflow:
    build: .
    container_name: stepflow-monitor-optimized
    ports:
      - "8080:8080"   # HTTP/Web UI
      - "8765:8765"   # WebSocket
    volumes:
      - ./storage:/app/storage
      - ./scripts:/workspace
    environment:
      - PYTHONUNBUFFERED=1
      - STEPFLOW_LOG_LEVEL=INFO
      - STEPFLOW_STORAGE_PATH=/app/storage
      - STEPFLOW_WEBSOCKET_HOST=0.0.0.0
      - STEPFLOW_WEBSOCKET_PORT=8765
      - STEPFLOW_AUTH_ENABLED=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - stepflow

networks:
  stepflow:
    driver: bridge

volumes:
  storage:
    driver: local
```

#### 部署命令
```bash
# 构建和部署
docker-compose up -d

# 验证部署
docker-compose ps
docker-compose logs stepflow

# 健康检查
curl http://localhost:8080/api/health
```

### 选项2：原生Python部署

#### 系统服务配置
```ini
# /etc/systemd/system/stepflow.service
[Unit]
Description=StepFlow Monitor
After=network.target

[Service]
Type=simple
User=stepflow
Group=stepflow
WorkingDirectory=/opt/stepflow
Environment=PYTHONPATH=/opt/stepflow
Environment=STEPFLOW_LOG_LEVEL=INFO
ExecStart=/opt/stepflow/venv/bin/python app/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 服务管理
```bash
# 安装和启动服务
sudo systemctl daemon-reload
sudo systemctl enable stepflow
sudo systemctl start stepflow

# 监控服务
sudo systemctl status stepflow
sudo journalctl -u stepflow -f
```

### 选项3：Kubernetes部署

#### Kubernetes清单
```yaml
# stepflow-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stepflow-monitor
  labels:
    app: stepflow-monitor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: stepflow-monitor
  template:
    metadata:
      labels:
        app: stepflow-monitor
    spec:
      containers:
      - name: stepflow-monitor
        image: stepflow/monitor:optimized
        ports:
        - containerPort: 8080
        - containerPort: 8765
        env:
        - name: STEPFLOW_LOG_LEVEL
          value: "INFO"
        - name: STEPFLOW_STORAGE_PATH
          value: "/app/storage"
        volumeMounts:
        - name: storage
          mountPath: /app/storage
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: stepflow-storage

---
apiVersion: v1
kind: Service
metadata:
  name: stepflow-monitor-service
spec:
  selector:
    app: stepflow-monitor
  ports:
    - name: http
      protocol: TCP
      port: 8080
      targetPort: 8080
    - name: websocket
      protocol: TCP
      port: 8765
      targetPort: 8765
  type: LoadBalancer
```

## ⚙️ 配置管理

### 环境变量

#### 核心配置
```bash
# 应用程序设置
export STEPFLOW_LOG_LEVEL=INFO
export STEPFLOW_STORAGE_PATH=/app/storage
export STEPFLOW_WEBSOCKET_HOST=0.0.0.0
export STEPFLOW_WEBSOCKET_PORT=8765

# 性能设置
export STEPFLOW_WAL_AUTOCHECKPOINT=1000
export STEPFLOW_CACHE_SIZE=10000
export STEPFLOW_BUFFER_SIZE=50

# 安全设置
export STEPFLOW_AUTH_ENABLED=false
export STEPFLOW_API_KEY=""
```

#### 生产环境文件
```bash
# 为生产创建.env文件
cat > .env << EOF
STEPFLOW_LOG_LEVEL=INFO
STEPFLOW_STORAGE_PATH=/app/storage
STEPFLOW_WEBSOCKET_HOST=0.0.0.0
STEPFLOW_WEBSOCKET_PORT=8765
STEPFLOW_AUTH_ENABLED=true
STEPFLOW_API_KEY=your-secure-api-key
EOF
```

### 数据库调优

#### SQLite配置优化
```python
# app/core/persistence.py - 生产调优
PRODUCTION_SQLITE_CONFIG = {
    "journal_mode": "WAL",
    "synchronous": "NORMAL",
    "cache_size": "20000",  # 生产环境20MB
    "temp_store": "memory",
    "mmap_size": "536870912",  # 大数据集512MB
    "wal_autocheckpoint": "1000",
    "busy_timeout": "30000"  # 30秒
}
```

## 🎛️ 性能调优

### 生产优化

#### 1. 内存配置
```bash
# 系统级调优
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.dirty_ratio=5' >> /etc/sysctl.conf
echo 'vm.dirty_background_ratio=2' >> /etc/sysctl.conf

# 应用更改
sysctl -p
```

#### 2. 文件系统优化
```bash
# 在SSD上的SQLite
mount -o remount,noatime /path/to/storage

# 验证挂载选项
mount | grep storage
```

#### 3. 应用程序调优
```python
# app/core/persistence.py - 生产设置
class PersistenceLayer:
    def __init__(self, storage_path: str = "storage"):
        # 生产优化的缓冲区设置
        self._buffer_size = 100  # 生产增加
        self._flush_interval = 0.5  # 更频繁刷新
        
        # 连接池设置
        self._connection_timeout = 60
        self._busy_timeout = 30000
```

## 📊 监控设置

### 应用程序指标

#### 健康检查端点
```bash
# 基本健康
curl http://localhost:8080/api/health

# 详细指标
curl http://localhost:8080/api/health/metrics

# 数据库性能
curl http://localhost:8080/api/health/database
```

#### 性能监控脚本
```bash
# 创建监控脚本
cat > monitor.sh << 'EOF'
#!/bin/bash

while true; do
    echo "=== $(date) ==="
    
    # API响应时间
    curl -w "API响应: %{time_total}s\n" -o /dev/null -s \
         http://localhost:8080/api/health
    
    # 数据库指标
    curl -s http://localhost:8080/api/health/metrics | \
         python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    db = data.get('database', {})
    print(f\"数据库大小: {db.get('database_size_mb', 'N/A')}MB\")
    print(f\"WAL模式: {db.get('wal_mode', 'N/A')}\")
    print(f\"执行数: {db.get('table_counts', {}).get('executions', 'N/A')}\")
except:
    print('指标不可用')
"
    
    echo "---"
    sleep 30
done
EOF

chmod +x monitor.sh
```

### 日志监控

#### 集中日志
```bash
# 配置rsyslog集中日志
echo '*.* @@log-server:514' >> /etc/rsyslog.conf

# Docker部署
docker-compose logs -f stepflow | grep -E "(ERROR|WARNING|performance)"
```

#### 日志分析
```bash
# 错误跟踪
grep -E "(ERROR|CRITICAL)" logs/stepflow.log | tail -20

# 性能分析
grep "performance" logs/stepflow.log | awk '{print $NF}' | sort -n

# WAL模式验证
grep -i "wal" logs/stepflow.log
```

## 🔄 回滚程序

### 紧急回滚

#### 1. 快速回滚（< 5分钟）
```bash
# 停止当前服务
docker-compose down  # 或 systemctl stop stepflow

# 恢复备份
cp backups/$(ls backups/ | tail -1)/stepflow.db storage/database/

# 使用之前代码启动
git checkout HEAD~1  # 或从备份恢复
docker-compose up -d
```

#### 2. 数据库回滚
```bash
# 如果WAL造成问题，转换回回滚日志
sqlite3 storage/database/stepflow.db "PRAGMA journal_mode=DELETE;"

# 验证回滚
sqlite3 storage/database/stepflow.db "PRAGMA journal_mode;"
# 应该返回: delete
```

#### 3. 完整环境回滚
```bash
# 恢复完整备份
rm -rf storage/
tar -xzf backups/$(ls backups/ | tail -1)/storage_backup.tar.gz

# 恢复应用程序代码
cp -r backups/$(ls backups/ | tail -1)/app_backup/ app/

# 重启服务
docker-compose restart
```

### 回滚后验证
```bash
# 测试基本功能
curl http://localhost:8080/api/health
curl http://localhost:8080/api/executions?limit=5

# 验证数据完整性
python3 -c "
import sqlite3
conn = sqlite3.connect('storage/database/stepflow.db')
print('执行数:', conn.execute('SELECT COUNT(*) FROM executions').fetchone()[0])
conn.close()
"
```

## 🔧 故障排除

### 常见问题和解决方案

#### 问题1：WAL模式未激活
```bash
# 症状: journal_mode返回'delete'而不是'wal'
# 解决方案1: 检查文件权限
ls -la storage/database/
chmod 664 storage/database/stepflow.db

# 解决方案2: 验证SQLite版本
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
# 确保版本 >= 3.7.0

# 解决方案3: 手动WAL激活
sqlite3 storage/database/stepflow.db "PRAGMA journal_mode=WAL;"
```

#### 问题2：高内存使用
```bash
# 症状: 内存使用 > 500MB
# 解决方案1: 减少缓存大小
sqlite3 storage/database/stepflow.db "PRAGMA cache_size=5000;"

# 解决方案2: 检查内存泄漏
ps aux | grep python
pmap $(pgrep python)

# 解决方案3: 重启应用程序
docker-compose restart stepflow
```

#### 问题3：数据库锁定错误
```bash
# 症状: "database is locked"错误
# 解决方案1: 检查忙等待超时
sqlite3 storage/database/stepflow.db "PRAGMA busy_timeout;"

# 解决方案2: 验证WAL检查点
sqlite3 storage/database/stepflow.db "PRAGMA wal_checkpoint(FULL);"

# 解决方案3: 检查文件权限
ls -la storage/database/stepflow.db*
```

#### 问题4：性能下降
```bash
# 症状: 响应时间 > 50ms
# 解决方案1: 运行数据库优化
curl -X POST http://localhost:8080/api/health/optimize

# 解决方案2: 检查WAL文件大小
ls -lah storage/database/stepflow.db-wal
# 如果 > 100MB，需要检查点

# 解决方案3: 分析性能
python3 scripts/performance_test.py
```

### 调试模式激活
```bash
# 启用调试日志
export STEPFLOW_LOG_LEVEL=DEBUG

# 或临时修改应用程序
sed -i 's/logging.INFO/logging.DEBUG/' app/main.py

# 监控调试输出
tail -f logs/stepflow.log | grep DEBUG
```

### 支持信息收集
```bash
# 为支持收集系统信息
cat > debug_info.txt << EOF
=== 系统信息 ===
操作系统: $(uname -a)
Python: $(python3 --version)
存储: $(df -h storage/)

=== 应用程序状态 ===
健康: $(curl -s http://localhost:8080/api/health)
WAL模式: $(sqlite3 storage/database/stepflow.db "PRAGMA journal_mode;")
数据库大小: $(ls -lah storage/database/)

=== 最近日志 ===
$(tail -50 logs/stepflow.log)
EOF

echo "调试信息已收集到 debug_info.txt"
```

## 🎯 结论

这个迁移和部署指南为在StepFlow Monitor中成功实施SQLite WAL优化提供了全面说明。关键要点：

### 迁移成功因素
- **零停机方法**：确保服务连续性
- **全面备份策略**：提供安全网
- **分步验证**：确认迁移成功
- **回滚程序**：需要时快速恢复

### 部署最佳实践
- **Docker部署**：推荐保持一致性
- **环境配置**：对性能至关重要
- **监控设置**：运营可见性必需
- **性能调优**：最大化优化收益

### 预期结果
- **25-33倍性能提升**：并发操作
- **亚5ms响应时间**：数据库操作
- **100%数据完整性**：迁移期间保持
- **生产就绪可靠性**：增强监控

遵循本指南确保平滑过渡到高性能SQLite WAL实现，风险最小，收益最大。

---

**支持**：如需额外协助，请参考性能基准和技术实现文档。