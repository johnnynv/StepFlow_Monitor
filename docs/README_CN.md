# 🐳 ContainerFlow 可视化器

## 专业的容器执行步骤可视化解决方案

**轻量级、实时的容器执行工作流监控可视化工具**

### ✨ 核心特性

- **🚀 零配置**：单命令部署
- **📱 实时可视化**：类似GitHub Actions的步骤展示
- **🔄 实时日志**：WebSocket驱动的实时日志流
- **🎨 响应式界面**：现代化Web界面，支持移动设备
- **🐳 Docker友好**：完美集成Docker工作流
- **📊 进度跟踪**：实时显示执行进度和状态

## 🏗️ 架构设计

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Python脚本    │ ◄──────────────► │   Web界面       │
│ (步骤控制)       │                 │ (实时可视化)     │
└─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐    HTTP服务     ┌─────────────────┐
│  Docker容器     │ ◄──────────────► │   浏览器        │
│ (科学计算任务)   │                 │ (用户界面)       │
└─────────────────┘                 └─────────────────┘
```

## 🚀 快速开始

### 方式1：直接Python运行

```bash
# 1. 安装依赖
pip install websockets

# 2. 运行可视化器
python container_flow_visualizer.py

# 3. 打开浏览器
# 访问: http://localhost:8080/visualizer.html
```

### 方式2：Docker部署

```bash
# 1. 生成Docker配置
python deployment/docker_integration.py

# 2. 启动服务
chmod +x deploy_containerflow.sh
./deploy_containerflow.sh

# 3. 访问界面
# 自动打开: http://localhost:8080/visualizer.html
```

## 📋 集成指南

### 步骤1：添加可视化代码

```python
from core import create_visualizer, add_workflow_step, start_visualization_service
import threading

# 初始化可视化器
viz = create_visualizer(http_port=8080, websocket_port=8765)

# 定义步骤
add_workflow_step("环境配置", "配置Python和科学计算环境")
add_workflow_step("数据下载", "下载所需的数据集")
add_workflow_step("Jupyter执行", "运行数据分析notebook")
add_workflow_step("测试执行", "运行pytest并生成报告")
add_workflow_step("报告生成", "生成最终报告文件")
```

### 步骤2：在现有函数中添加状态更新

```python
def your_existing_function():
    # 开始步骤
    start_workflow_step(0)  # 步骤索引
    log_step_message(0, "开始环境配置...")
    
    try:
        # 你的现有代码
        setup_environment()
        
        # 添加进度日志
        log_step_message(0, "安装科学计算包...")
        install_packages()
        
        log_step_message(0, "配置Jupyter环境...")
        setup_jupyter()
        
        # 完成步骤
        complete_workflow_step(0, "completed")
        log_step_message(0, "✅ 环境配置完成!", "success")
        
    except Exception as e:
        complete_workflow_step(0, "failed")
        log_step_message(0, f"❌ 配置失败: {str(e)}", "error")
```

### 步骤3：启动可视化服务

```python
# 在后台线程运行工作流
workflow_thread = threading.Thread(target=your_workflow, daemon=True)
workflow_thread.start()

# 启动可视化器（主线程）
start_visualization_service()
```

## 🖥️ 界面功能

### 📊 实时监控面板
- **进度条**：显示整体执行进度
- **统计信息**：当前步骤、总步骤、已完成、执行时间
- **步骤状态**：每个步骤的详细状态和耗时

### 📜 实时日志
- **颜色分类**：信息(蓝)、成功(绿)、警告(黄)、错误(红)
- **时间戳**：每条日志都有精确的时间戳
- **自动滚动**：新日志自动滚动到底部

### 🔄 状态指示
- **⏳ 等待中**：等待执行
- **🔄 运行中**：正在执行（带动画效果）
- **✅ 已完成**：执行成功
- **❌ 已失败**：执行失败

## 📁 项目结构

```
ContainerFlow_Visualizer/
├── core/                           # 核心可视化模块
│   ├── __init__.py                # 包初始化
│   ├── visualizer.py              # 主可视化类
│   └── api.py                     # 便捷API函数
├── web_interface/                  # Web界面资源
│   ├── visualizer.html            # 主HTML界面
│   ├── styles.css                 # CSS样式
│   └── visualizer.js              # 客户端JavaScript
├── examples/                       # 使用示例
│   ├── basic_integration_example.py
│   └── workflow_integration_example.py
├── deployment/                     # 部署工具
│   ├── docker_integration.py      # Docker部署工具
│   └── production_workflow_example.py
├── docs/                          # 文档
│   ├── README_EN.md               # 英文文档
│   └── README_CN.md               # 中文文档
├── container_flow_visualizer.py   # 主入口点
└── requirements.txt               # Python依赖
```

## 🔧 配置选项

### 端口配置
```python
# 自定义端口
viz = create_visualizer(
    http_port=8080,          # HTTP服务器端口
    websocket_port=8765      # WebSocket端口
)
```

### 日志级别
```python
# 不同级别的日志
log_step_message(step_index, "普通信息", "info")      # 蓝色
log_step_message(step_index, "成功信息", "success")   # 绿色  
log_step_message(step_index, "警告信息", "warning")   # 黄色
log_step_message(step_index, "错误信息", "error")     # 红色
```

## 🛠️ 高级用法

### 自定义步骤描述
```python
add_workflow_step("数据预处理", "清洗和转换原始数据集，处理缺失值")
add_workflow_step("特征工程", "提取和选择最重要的特征变量")
add_workflow_step("模型训练", "训练机器学习模型并调优参数")
```

### 错误处理
```python
try:
    risky_operation()
    complete_workflow_step(step_index, "completed")
except SpecificError as e:
    log_step_message(step_index, f"特定错误: {e}", "warning")
    complete_workflow_step(step_index, "completed")  # 继续执行
except Exception as e:
    log_step_message(step_index, f"严重错误: {e}", "error") 
    complete_workflow_step(step_index, "failed")     # 停止执行
    return False
```

### 进度细分
```python
def complex_step():
    start_workflow_step(2)
    
    subtasks = ["子任务1", "子任务2", "子任务3"]
    for i, task in enumerate(subtasks):
        log_step_message(2, f"执行 {task}...")
        execute_subtask(task)
        
        progress = ((i + 1) / len(subtasks)) * 100
        log_step_message(2, f"进度: {progress:.0f}%")
    
    complete_workflow_step(2, "completed")
```

## 🚀 部署建议

### 开发环境
```bash
# 直接运行，快速迭代
python container_flow_visualizer.py
```

### 测试环境  
```bash
# Docker单容器
docker build -t containerflow-viz .
docker run -p 8080:8080 -p 8765:8765 containerflow-viz
```

### 生产环境
```bash
# Docker Compose，带持久化
docker-compose up -d
```

## 🔍 故障排除

### 常见问题

**1. WebSocket连接失败**
```bash
# 检查端口是否被占用
netstat -an | grep 8765

# 防火墙设置
sudo ufw allow 8765
```

**2. 浏览器无法访问**
```bash
# 检查HTTP服务器
curl http://localhost:8080/visualizer.html

# 检查Docker端口映射
docker ps | grep 8080
```

**3. 界面不更新**
- 刷新浏览器页面
- 检查WebSocket连接状态
- 查看浏览器开发者工具的控制台错误

## 🎨 界面自定义

### 修改样式
编辑 `web_interface/styles.css`：

```css
/* 自定义颜色主题 */
.step.running { 
    border-left-color: #your-color; 
    background: #your-bg-color;
}
```

### 添加新功能
扩展 `core/visualizer.py`：

```python
# 自定义消息处理
def handle_custom_message(self, message):
    if message.type == 'custom':
        # 处理自定义消息
        pass
```

## 📊 与其他方案对比

| 特性 | ContainerFlow | GitHub Actions | Jenkins | Tekton |
|------|---------------|----------------|---------|--------|
| 部署复杂度 | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 学习成本 | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 实时可视化 | ✅ | ✅ | ✅ | ✅ |
| 自定义程度 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Docker集成 | ✅ | ✅ | ✅ | ✅ |
| 零配置 | ✅ | ❌ | ❌ | ❌ |

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个方案！

## 📄 许可证

MIT License - 可自由使用和修改。

---

**🎉 现在你可以像GitHub Actions一样监控你的容器执行过程了！**