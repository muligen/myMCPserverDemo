# MCP Server Demo - 心跳服务器

这是一个基于TCP Socket的心跳服务器项目，用于接收和处理客户端的心跳信息。

## 项目结构

```
mcp-server-demo/
├── src/
│   ├── server/
│   │   ├── __init__.py
│   │   ├── heartbeat_server.py  # TCP心跳服务器
│   │   └── http_server.py       # HTTP API服务器
│   └── utils/
│       └── __init__.py
├── config/
│   └── server_config.py         # 服务器配置
├── logs/                        # 日志文件目录
├── main.py                      # 原MCP服务器代码
├── run_server.py               # 心跳服务器启动脚本
├── run_http_server.py          # HTTP服务器启动脚本
├── run_all_servers.py          # 同时启动两个服务器
├── requirements.txt            # Python依赖
├── pyproject.toml             # 项目配置
└── README.md                  # 项目说明
```

## 功能特性

### 心跳服务器（TCP）
- 支持多客户端并发连接
- 实时接收和处理心跳消息
- 客户端状态管理和监控
- 详细的日志记录
- 可配置的服务器参数
- 线程安全的客户端管理
- 支持 `Ctrl+C` 优雅停止
- 标准化的心跳消息格式

### HTTP API服务器
- RESTful API接口
- 支持自定义路由
- JSON格式的请求响应
- 内置健康检查接口
- 详细的请求日志
- 调试模式支持
- **任务队列管理功能**
- **用户输入监听**
- **命令分配和响应机制**

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务器

#### 方式一：分别启动
```bash
# 启动心跳服务器（TCP）
python run_server.py

# 启动HTTP服务器
python run_http_server.py
```

#### 方式二：同时启动两个服务器
```bash
# 使用默认配置启动
python run_all_servers.py

# 自定义配置启动
python run_all_servers.py --http-port 8080 --heartbeat-port 9999
```

#### 方式三：自定义参数启动
```bash
# 心跳服务器
python run_server.py --host 0.0.0.0 --port 8888

# HTTP服务器
python run_http_server.py --host 0.0.0.0 --port 5000 --debug
```

### 3. 测试连接

#### 测试心跳服务器（TCP）
```bash
telnet localhost 8888
# 连接后发送：{"code": 200, "data": "heartbeat", "message": "客户端心跳"}
```

#### 测试HTTP API服务器
```bash
# 启动HTTP服务器（启用用户输入）
python run_http_server.py

# 启动HTTP服务器（禁用用户输入）
python run_http_server.py --no-input

# 测试根路径
curl http://localhost:5000/

# 测试worker2/command接口（获取任务）
curl http://localhost:5000/worker2/command

# 测试worker2/command接口（提交任务结果）
curl "http://localhost:5000/worker2/command?task_id=1&command_result=success"

# 测试健康检查
curl http://localhost:5000/health

# 查看任务状态
curl http://localhost:5000/tasks

# 添加任务到队列
curl -X POST http://localhost:5000/tasks/add \
  -H "Content-Type: application/json" \
  -d '{"command": "start_process"}'
```

## HTTP API接口

### GET /worker2/command
处理worker2命令请求

#### 获取任务
**请求格式：**
```bash
curl "http://localhost:5000/worker2/command"
```

**响应格式（有任务时）：**
```json
{
  "code": 0,
  "data": {
    "buildin": true,
    "command": "init",
    "task_id": 1
  }
}
```

**响应格式（无任务时）：**
```json
{
  "code": 0,
  "data": {
    "buildin": false,
    "command": "",
    "task_id": null
  }
}
```

#### 提交任务结果
**请求参数：**
- `task_id`: 任务ID
- `command_result`: 命令执行结果

**请求格式：**
```bash
curl "http://localhost:5000/worker2/command?task_id=1&command_result=success"
```

**响应格式：**
```json
{
  "code": 0,
  "data": {
    "buildin": true,
    "command": "init",
    "message": "任务 1 完成"
  }
}
```

#### 内置命令说明
当命令为以下之一时，`buildin` 设置为 `true`：
- `init`
- `cleanup`
- `status`

### GET /health
健康检查接口

**响应格式：**
```json
{
  "code": 200,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "server": "HTTPServer"
  }
}
```

### GET /tasks
查看任务队列状态

**响应格式：**
```json
{
  "code": 200,
  "data": {
    "queue_size": 2,
    "pending_tasks": 1,
    "pending_task_details": {
      "1": {
        "command": "init",
        "buildin": true,
        "assigned_time": "2024-01-01T12:00:00.000Z"
      }
    }
  }
}
```

### POST /tasks/add
添加任务到队列

**请求格式：**
```bash
curl -X POST http://localhost:5000/tasks/add \
  -H "Content-Type: application/json" \
  -d '{"command": "start_process"}'
```

**请求体：**
```json
{
  "command": "start_process"
}
```

**响应格式：**
```json
{
  "code": 200,
  "data": {
    "message": "命令 'start_process' 已添加到队列",
    "queue_size": 3
  }
}
```

### GET /
根路径，显示服务器信息

**响应格式：**
```json
{
  "code": 200,
  "data": {
    "message": "HTTP服务器运行中",
    "version": "1.0.0",
    "features": [
      "任务队列管理",
      "用户输入监听",
      "worker2命令处理"
    ],
    "endpoints": [
      "GET /worker2/command - 获取/处理worker2命令",
      "GET /health - 健康检查",
      "GET /tasks - 查看任务状态",
      "POST /tasks/add - 添加任务到队列"
    ]
  }
}
```

## 心跳消息格式

### 客户端发送的消息
```json
{
  "code": 200,
  "data": "heartbeat_data",
  "message": "客户端心跳信息"
}
```

**字段说明：**
- `code`: 状态码（整数，如 200 表示成功）
- `data`: 数据内容（字符串，可包含心跳数据）
- `message`: 消息描述（字符串，心跳的具体信息）

### 服务器响应消息
```json
{
  "code": 200,
  "data": "success",
  "message": "心跳接收成功"
}
```

**错误响应示例：**
```json
{
  "code": 400,
  "data": "error",
  "message": "消息格式错误"
}
```

## 配置说明

在 `config/server_config.py` 中可以修改以下配置：

- `HOST`: 服务器监听地址
- `PORT`: 服务器监听端口
- `CLIENT_TIMEOUT`: 客户端超时时间
- `MAX_CLIENTS`: 最大客户端连接数
- `EXPECTED_HEARTBEAT_INTERVAL`: 期望的心跳间隔
- `LOG_LEVEL`: 日志级别

## 使用示例

### 任务队列系统使用示例
```bash
# 终端1: 启动HTTP服务器（启用用户输入）
python run_http_server.py

# 服务器启动后，可以直接在终端输入命令：
init
status
cleanup
restart_service
check_logs

# 终端2: 客户端获取任务
curl "http://localhost:5000/worker2/command"
# 响应: {"code": 0, "data": {"buildin": true, "command": "init", "task_id": 1}}

# 终端2: 客户端完成任务并提交结果
curl "http://localhost:5000/worker2/command?task_id=1&command_result=init_success"
# 响应: {"code": 0, "data": {"buildin": true, "command": "init", "message": "任务 1 完成"}}

# 终端2: 获取下一个任务
curl "http://localhost:5000/worker2/command"
# 响应: {"code": 0, "data": {"buildin": true, "command": "status", "task_id": 2}}

# 终端3: 查看任务状态
curl http://localhost:5000/tasks
```

### 测试不同心跳消息
```bash
# 终端1: 启动服务器
python run_server.py

# 终端2: 使用telnet测试
telnet localhost 8888
# 连接后发送：
# {"code": 200, "data": "server_heartbeat", "message": "Web服务器正常"}
# {"code": 201, "data": "database_status", "message": "数据库连接正常"}
# {"code": 500, "data": "error_alert", "message": "CPU使用率过高"}
```

### 环境变量配置
```bash
export HEARTBEAT_HOST=0.0.0.0
export HEARTBEAT_PORT=8888
export LOG_LEVEL=DEBUG
python run_server.py
```

## 日志输出

服务器日志只输出到文件，不在控制台显示：

**心跳服务器日志：** `logs/heartbeat_server.log`
**HTTP服务器日志：** `logs/http_server.log`

日志文件内容示例：
```
2024-01-01 12:00:00 - HeartbeatServer - INFO - 心跳服务器启动在 localhost:8888
2024-01-01 12:00:01 - HeartbeatServer - INFO - 新客户端连接: ('127.0.0.1', 54321)
2024-01-01 12:00:01 - HeartbeatServer - INFO - 收到心跳 - 客户端: 127.0.0.1:54321, 代码: 200, 数据: server_heartbeat, 地址: ('127.0.0.1', 54321)

2024-01-01 12:00:05 - HTTPServer - INFO - 启动HTTP服务器在 localhost:5000
2024-01-01 12:00:06 - HTTPServer - INFO - 收到请求: GET /worker2/command from 127.0.0.1
2024-01-01 12:00:06 - HTTPServer - INFO - 分配任务: {'code': 0, 'data': {'buildin': True, 'command': 'init', 'task_id': 1}}
```

## 扩展功能

项目支持以下扩展：
- 数据库持久化
- 客户端认证
- 心跳数据统计和分析
- Web管理界面
- 集群部署
- 心跳数据可视化

## 注意事项

1. 确保服务器端口没有被占用
2. 客户端通过IP和端口组合作为唯一标识
3. 心跳消息必须包含 `code`、`data`、`message` 三个字段
4. 按 `Ctrl+C` 可以优雅停止服务器
5. 日志文件只输出到文件，不在控制台显示：
   - `logs/heartbeat_server.log` - 心跳服务器日志
   - `logs/http_server.log` - HTTP服务器日志