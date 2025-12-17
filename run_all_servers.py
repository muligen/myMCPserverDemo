"""
同时启动心跳服务器和HTTP服务器
"""
import threading
import time
import sys
import os
import argparse
import signal

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server.heartbeat_server import HeartbeatServer
from server.http_server import HTTPServer


class ServerManager:
    """服务器管理器"""

    def __init__(self):
        self.heartbeat_server = None
        self.http_server = None
        self.running = False

    def start_heartbeat_server(self, host="localhost", port=8888):
        """启动心跳服务器"""
        self.heartbeat_server = HeartbeatServer(host=host, port=port)
        try:
            self.heartbeat_server.start()
        except Exception as e:
            print(f"心跳服务器启动失败: {e}")

    def start_http_server(self, host="localhost", port=5000, debug=False):
        """启动HTTP服务器"""
        self.http_server = HTTPServer(host=host, port=port)
        try:
            self.http_server.run(debug=debug)
        except Exception as e:
            print(f"HTTP服务器启动失败: {e}")

    def stop_all(self):
        """停止所有服务器"""
        print("\n正在停止所有服务器...")
        self.running = False

        if self.heartbeat_server:
            self.heartbeat_server.stop()

        # HTTP服务器通过Ctrl+C自动停止
        print("所有服务器已停止")

    def run(self, heartbeat_host="localhost", heartbeat_port=8888,
            http_host="localhost", http_port=5000, debug=False):
        """同时运行两个服务器"""
        self.running = True

        print("启动多服务器系统...")
        print("=" * 50)
        print(f"心跳服务器: {heartbeat_host}:{heartbeat_port}")
        print(f"HTTP服务器:  {http_host}:{http_port}")
        print("=" * 50)
        print("按 Ctrl+C 停止所有服务器")
        print()

        # 创建心跳服务器线程
        heartbeat_thread = threading.Thread(
            target=self.start_heartbeat_server,
            args=(heartbeat_host, heartbeat_port)
        )
        heartbeat_thread.daemon = True

        # 创建HTTP服务器线程
        http_thread = threading.Thread(
            target=self.start_http_server,
            args=(http_host, http_port, debug)
        )
        http_thread.daemon = True

        try:
            # 启动心跳服务器
            heartbeat_thread.start()
            time.sleep(1)  # 等待心跳服务器启动

            # 启动HTTP服务器
            http_thread.start()

            # 设置信号处理
            signal.signal(signal.SIGINT, lambda signum, frame: self.stop_all())

            # 保持主线程运行
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            self.stop_all()
        except Exception as e:
            print(f"服务器系统出错: {e}")
            self.stop_all()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="同时启动心跳服务器和HTTP服务器")
    parser.add_argument("--heartbeat-host", default="localhost", help="心跳服务器地址")
    parser.add_argument("--heartbeat-port", type=int, default=8888, help="心跳服务器端口")
    parser.add_argument("--http-host", default="localhost", help="HTTP服务器地址")
    parser.add_argument("--http-port", type=int, default=8080, help="HTTP服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用HTTP服务器调试模式")

    args = parser.parse_args()

    # 创建并运行服务器管理器
    manager = ServerManager()
    manager.run(
        heartbeat_host=args.heartbeat_host,
        heartbeat_port=args.heartbeat_port,
        http_host=args.http_host,
        http_port=args.http_port,
        debug=args.debug
    )


if __name__ == "__main__":
    main()