# MCP工具使用说明

本文档说明了如何通过MCP工具控制心跳服务器和HTTP服务器。

## 服务器自动启动

当启动main.py时，以下服务器会自动启动：
- **心跳服务器**: localhost:8888 - 接收客户端心跳
- **HTTP服务器**: localhost:5000 - 提供API接口

## 可用工具

### 1. get_agent_status
从心跳服务器获取所有agent的状态信息，包括系统信息（如果可用）。

**返回：**
```json
{
  "agents": {
    "127.0.0.1:12345": {
      "id": "127.0.0.1:12345",
      "address": "127.0.0.1:12345",
      "last_heartbeat": "2025-12-19T10:30:00",
      "status": "active",
      "system_info": {
        "machine_name": "STFKQMTJXAWDCPI",
        "os_version": "Windows",
        "cpu_usage": 6.71,
        "memory": {
          "total": 65433,
          "used": 27503,
          "usage_percent": 42.04
        },
        "disk": {
          "total": 400,
          "used": 273,
          "usage_percent": 68.25
        },
        "network": {
          "upload": 0.0,
          "download": 0.0
        }
      }
    }
  },
  "servers": {
    "heartbeat_server": {
      "running": true,
      "host": "localhost",
      "port": 8888,
      "connected_clients": 1
    },
    "http_server": {
      "running": true,
      "host": "localhost",
      "port": 5000,
      "queue_size": 3,
      "pending_tasks": 1
    }
  }
}
```

**系统信息字段说明：**
- `machine_name`: 机器名
- `os_version`: 操作系统版本
- `cpu_usage`: CPU使用率（百分比）
- `memory`: 内存信息（MB）
- `disk`: 磁盘信息（GB）
- `network`: 网络上传/下载速度

### 2. agent_execute_command
向HTTP服务器的任务队列添加命令。

**参数：**
- `command` (必需): 要执行的命令

**返回：**
```json
{
  "status": "success",
  "message": "Command 'init' added to queue",
  "queue_size": 4
}
```

### 3. add_task_to_queue
向HTTP服务器的任务队列添加任务（与agent_execute_command功能相同）。

**参数：**
- `command` (必需): 要添加的任务命令

**返回：**
```json
{
  "status": "success",
  "message": "Task 'cleanup' added to queue",
  "queue_size": 5
}
```

### 4. get_task_status
获取HTTP服务器的任务状态。

**返回：**
```json
{
  "status": "success",
  "data": {
    "queue_size": 2,
    "pending_tasks": 1,
    "pending_task_details": {
      "1": {
        "command": "init",
        "buildin": true,
        "assigned_time": "2025-12-19T10:35:00"
      }
    }
  }
}
```

### 5. stop_servers
停止所有正在运行的服务器。

**返回：**
```json
{
  "status": "success",
  "message": "Heartbeat server stopped; HTTP server stopped"
}
```

### 3. get_agent_status
获取所有服务器和客户端的状态信息。

**返回：**
```json
{
  "servers": {
    "heartbeat_server": {
      "running": true,
      "host": "localhost",
      "port": 8888,
      "clients": 2
    },
    "http_server": {
      "running": true,
      "host": "localhost",
      "port": 5000,
      "queue_size": 3,
      "pending_tasks": 1
    }
  },
  "clients": {
    "client1": {
      "address": "127.0.0.1:12345",
      "last_heartbeat": "2025-12-19T10:30:00",
      "status": "active"
    }
  }
}
```

### 4. agent_execute_command
向HTTP服务器的任务队列添加命令。

**参数：**
- `command` (必需): 要执行的命令

**返回：**
```json
{
  "status": "success",
  "message": "Command 'init' added to queue",
  "queue_size": 4
}
```

### 5. add_task_to_queue
向HTTP服务器的任务队列添加任务（与agent_execute_command功能相同）。

**参数：**
- `command` (必需): 要添加的任务命令

**返回：**
```json
{
  "status": "success",
  "message": "Task 'cleanup' added to queue",
  "queue_size": 5
}
```

### 6. get_task_status
获取HTTP服务器的任务状态。

**返回：**
```json
{
  "status": "success",
  "data": {
    "queue_size": 2,
    "pending_tasks": 1,
    "pending_task_details": {
      "1": {
        "command": "init",
        "buildin": true,
        "assigned_time": "2025-12-19T10:35:00"
      }
    }
  }
}
```

## HTTP服务器API端点

当HTTP服务器运行时，可以通过以下端点进行交互：

- `GET /health` - 健康检查
- `GET /tasks` - 查看任务状态
- `POST /tasks/add` - 添加任务到队列（需要JSON体：`{"command": "your_command"}`）
- `GET /worker2/command` - Worker2获取命令接口
- `GET /` - 服务器信息

## 心跳服务器

心跳服务器监听指定端口（默认8888），接收客户端的心跳消息。

### 支持的消息格式

心跳服务器支持以下格式的消息：

1. **系统信息消息**（JSON格式）：
   ```json
   {
     "code": 0,
     "data": "{\"cpu_usage\": 6.71, \"disk_total\": 400, \"disk_used\": 273, \"machine_name\": \"STFKQMTJXAWDCPI\", \"memory_total\": 65433, \"memory_used\": 27503, \"network_download\": 0.0, \"network_upload\": 0.0, \"os_version\": \"Windows\", \"type\": \"system_info\"}"
   }
   ```

2. **普通心跳消息**（可以是JSON或空对象）：
   ```json
   {
     "code": 0,
     "data": "{}"  // 空的JSON对象
   }
   ```
   或
   ```json
   {
     "code": 0,
     "data": "heartbeat"  // 普通字符串
   }
   ```

3. **空数据消息**：
   ```json
   {
     "code": 0,
     "data": ""  // 或data字段为null
   }
   ```

## 使用流程

1. **服务器已自动启动**（main.py启动时）

2. **检查状态：**
   ```
   调用 get_agent_status()
   ```

3. **添加任务：**
   ```
   调用 agent_execute_command("init")
   或
   调用 add_task_to_queue("cleanup")
   ```

4. **查看任务状态：**
   ```
   调用 get_task_status()
   ```

5. **停止服务器：**
   ```
   调用 stop_servers()
   ```

## 内置命令

以下命令会被标记为内置命令（buildin=true）：
- `init`
- `cleanup`
- `status`

## 注意事项

1. 服务器在独立线程中运行，不会阻塞MCP服务器
2. 所有日志都保存在 `logs/` 目录下
3. HTTP服务器默认不显示Flask/Werkzeug的访问日志
4. 任务队列采用FIFO（先进先出）模式