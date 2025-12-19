import atexit
import os
import sys
import threading
import time

from mcp.server.fastmcp import FastMCP

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from server.heartbeat_server import HeartbeatServer
from server.http_server import HTTPServer

# Create an MCP server
mcp = FastMCP("Demo", json_response=True)

# 全局服务器实例
heartbeat_server = HeartbeatServer(host="localhost", port=8888)
http_server = HTTPServer(host="localhost", port=5000)


# Add an addition tool，工具调用
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# 读取文件内容
@mcp.tool()
def read_file(file_path: str) -> str:
    """Read the content of a file"""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# 获取agent状态
@mcp.tool()
def get_agent_status() -> dict:
    """Get all agents status information from heartbeat server"""
    global heartbeat_server, http_server

    # 从心跳服务器获取agent状态
    agents_status = {}
    if heartbeat_server and heartbeat_server.clients:
        for client_id, client_info in heartbeat_server.clients.items():
            # 构建agent状态信息
            agent_data = {
                "id": client_id,
                "address": f"{client_info.get('client_address', ('unknown', 'unknown'))[0]}:{client_info.get('client_address', ('unknown', 'unknown'))[1]}",
                "last_heartbeat": client_info.get("last_heartbeat", "unknown"),
                "status": "active",  # 假设存在于clients中的都是活跃的
            }

            # 如果有系统信息，添加到agent数据中
            if "system_info" in client_info:
                sys_info = client_info["system_info"]
                agent_data["system_info"] = {
                    "machine_name": sys_info.get("machine_name", "unknown"),
                    "os_version": sys_info.get("os_version", "unknown"),
                    "cpu_usage": round(sys_info.get("cpu_usage", 0), 2),
                    "memory": {
                        "total": sys_info.get("memory_total", 0),
                        "used": sys_info.get("memory_used", 0),
                        "usage_percent": round((sys_info.get("memory_used", 0) / sys_info.get("memory_total", 1)) * 100, 2) if sys_info.get("memory_total") else 0
                    },
                    "disk": {
                        "total": sys_info.get("disk_total", 0),
                        "used": sys_info.get("disk_used", 0),
                        "usage_percent": round((sys_info.get("disk_used", 0) / sys_info.get("disk_total", 1)) * 100, 2) if sys_info.get("disk_total") else 0
                    },
                    "network": {
                        "upload": round(sys_info.get("network_upload", 0), 2),
                        "download": round(sys_info.get("network_download", 0), 2)
                    }
                }

            agents_status[client_id] = agent_data

    # 服务器状态信息
    status = {
        "agents": agents_status
    }

    return status


# 执行命令
@mcp.tool()
def agent_execute_command(command: str) -> dict:
    """Execute a command on the agent"""
    global http_server

    if not http_server or not http_server.running:
        return {"status": "error", "message": "HTTP server is not running"}

    try:
        # 将命令添加到任务队列
        http_server.task_queue.put(command)

        return {
            "status": "success",
            "message": f"Command '{command}' added to queue",
            "queue_size": http_server.task_queue.qsize(),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to execute command: {str(e)}"}


# 添加任务到队列
@mcp.tool()
def add_task_to_queue(command: str) -> dict:
    """Add a task to the HTTP server task queue"""
    global http_server

    if not http_server or not http_server.running:
        return {"status": "error", "message": "HTTP server is not running"}

    try:
        http_server.task_queue.put(command)
        return {
            "status": "success",
            "message": f"Task '{command}' added to queue",
            "queue_size": http_server.task_queue.qsize(),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to add task: {str(e)}"}


# 获取任务状态
@mcp.tool()
def get_task_status() -> dict:
    """Get current task status from HTTP server"""
    global http_server

    if not http_server or not http_server.running:
        return {"status": "error", "message": "HTTP server is not running"}

    try:
        return {
            "status": "success",
            "data": {
                "queue_size": http_server.task_queue.qsize(),
                "pending_tasks": len(http_server.pending_tasks),
                "pending_task_details": http_server.pending_tasks,
            },
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to get task status: {str(e)}"}


# region demo
# Add a dynamic greeting resource，提供资源
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"


# # Add a prompt， 提供回复格式
# @mcp.prompt()
# def greet_user(name: str, style: str = "friendly") -> str:
#     """Generate a greeting prompt"""
#     styles = {
#         "friendly": "Please write a warm, friendly greeting",
#         "formal": "Please write a formal, professional greeting",
#         "casual": "Please write a casual, relaxed greeting",
#     }

#     return f"{styles.get(style, styles['friendly'])} for someone named {name}."
# endregion


# 启动心跳服务器
def start_heartbeat_server():
    """启动心跳服务器"""
    print("启动心跳服务器在 localhost:8888")
    heartbeat_server.start()


# 启动HTTP服务器
def start_http_server():
    """启动HTTP服务器"""
    print("启动HTTP服务器在 localhost:5000")
    http_server.run(debug=False, enable_input=False)


def cleanup():
    """清理函数，在程序退出时调用"""
    global heartbeat_server, http_server
    try:
        if heartbeat_server and heartbeat_server.running:
            heartbeat_server.stop()
        if http_server and http_server.running:
            http_server.stop_input_listener()
    except Exception:
        pass


# Run with streamable HTTP transport
if __name__ == "__main__":
    # 注册清理函数
    atexit.register(cleanup)

    # 在独立线程中启动心跳服务器
    heartbeat_thread = threading.Thread(target=start_heartbeat_server, daemon=True)
    heartbeat_thread.start()

    # 在独立线程中启动HTTP服务器
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # 等待服务器启动
    time.sleep(10)
    get_agent_status()

    print("MCP服务器启动中...")
    print("可用的MCP工具:")
    print("- get_agent_status: 获取agent状态（从心跳服务器）")
    print("- agent_execute_command: 执行命令（添加到HTTP服务器任务队列）")
    print("- add_task_to_queue: 添加任务到队列")
    print("- get_task_status: 获取任务状态")
    print("- stop_servers: 停止服务器")
    print()

    # 启动MCP服务器
    mcp.run(transport="stdio")
