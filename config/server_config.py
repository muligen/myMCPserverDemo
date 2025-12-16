"""
服务器配置文件
"""
import os
from typing import Dict, Any


class ServerConfig:
    """服务器配置类"""

    # 服务器基本配置
    HOST = os.getenv("HEARTBEAT_HOST", "localhost")
    PORT = int(os.getenv("HEARTBEAT_PORT", "8888"))

    # 日志配置
    LOG_DIR = "logs"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

    # 客户端管理配置
    CLIENT_TIMEOUT = 30  # 客户端超时时间（秒）
    MAX_CLIENTS = 100  # 最大客户端连接数

    # 心跳配置
    EXPECTED_HEARTBEAT_INTERVAL = 5  # 期望的心跳间隔（秒）
    MAX_MISSED_HEARTBEATS = 3  # 最大丢失心跳次数

    # 消息配置
    MAX_MESSAGE_SIZE = 1024  # 最大消息大小（字节）
    SOCKET_TIMEOUT = 10  # Socket超时时间（秒）

    # 数据库配置（如果需要持久化）
    DB_CONFIG = {
        "type": "sqlite",
        "path": "data/heartbeat.db"
    }

    @classmethod
    def get_server_info(cls) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "max_clients": cls.MAX_CLIENTS,
            "client_timeout": cls.CLIENT_TIMEOUT,
            "expected_heartbeat_interval": cls.EXPECTED_HEARTBEAT_INTERVAL,
            "max_missed_heartbeats": cls.MAX_MISSED_HEARTBEATS
        }