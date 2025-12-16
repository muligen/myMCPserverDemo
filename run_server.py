"""
运行心跳服务器的入口脚本
"""
import sys
import os
import argparse

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server.heartbeat_server import HeartbeatServer
from config.server_config import ServerConfig


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="心跳服务器")
    parser.add_argument("--host", default=ServerConfig.HOST, help="服务器地址")
    parser.add_argument("--port", type=int, default=ServerConfig.PORT, help="服务器端口")

    args = parser.parse_args()

    print(f"启动心跳服务器...")
    print(f"配置信息: {ServerConfig.get_server_info()}")
    print(f"启动参数: host={args.host}, port={args.port}")
    print("按 Ctrl+C 停止服务器")

    # 创建并启动服务器
    server = HeartbeatServer(host=args.host, port=args.port)

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        server.stop()


if __name__ == "__main__":
    main()