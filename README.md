# MCP Server Demo - 心跳服务器

这是一个基于TCP Socket的心跳服务器项目，用于接收和处理客户端的心跳信息。

## 项目结构

```
mcp-server-demo/
├── src/
│   ├── server/
│   │   ├── __init__.py
│   │   └── heartbeat_server.py  # TCP心跳服务器
│   └── utils/
│       └── __init__.py
├── config/
│   └── server_config.py         # 服务器配置
├── logs/                        # 日志文件目录
├── main.py                      # 原MCP服务器代码
├── run_server.py               # 服务器启动脚本
├── requirements.txt            # Python依赖
├── pyproject.toml             # 项目配置
└── README.md                  # 项目说明
```

## 功能特性

### 服务器端
- 支持多客户端并发连接
- 实时接收和处理心跳消息
- 客户端状态管理和监控
- 详细的日志记录
- 可配置的服务器参数
- 线程安全的客户端管理
- 支持 `Ctrl+C` 优雅停止
- 标准化的心跳消息格式

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
# 使用默认配置启动
python run_server.py

# 自定义地址和端口
python run_server.py --host 0.0.0.0 --port 9999
```

### 3. 测试连接
可以使用任何TCP客户端工具连接服务器，发送心跳消息：

**使用telnet测试：**
```bash
telnet localhost 8888
# 连接后发送：{"code": 200, "data": "heartbeat", "message": "客户端心跳"}
```

**使用curl测试：**
```bash
# 需要使用支持TCP的客户端或编写简单脚本
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

服务器日志会同时输出到控制台和文件 `logs/heartbeat_server.log`：

```
2024-01-01 12:00:00 - HeartbeatServer - INFO - 心跳服务器启动在 localhost:8888
2024-01-01 12:00:01 - HeartbeatServer - INFO - 新客户端连接: ('127.0.0.1', 54321)
2024-01-01 12:00:01 - HeartbeatServer - INFO - 收到心跳 - 客户端: 127.0.0.1:54321, 代码: 200, 数据: server_heartbeat, 消息: Web服务器正常, 地址: ('127.0.0.1', 54321)
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
5. 日志文件会自动记录在 `logs/heartbeat_server.log`