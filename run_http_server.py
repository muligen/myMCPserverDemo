"""
运行HTTP服务器的入口脚本
"""
import sys
import os
import argparse

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server.http_server import HTTPServer


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="HTTP API服务器")
    parser.add_argument("--host", default="localhost", help="服务器地址")
    parser.add_argument("--port", type=int, default=5000, help="服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--no-input", dest="input", action="store_false", default=True, help="禁用用户输入监听")

    args = parser.parse_args()

    print(f"启动HTTP服务器...")
    print(f"启动参数: host={args.host}, port={args.port}, debug={args.debug}, input={args.input}")
    if not args.input:
        print("注意: 用户输入监听已禁用")
        print()
        print("可用的API端点:")
        print(f"  GET http://{args.host}:{args.port}/")
        print(f"  GET http://{args.host}:{args.port}/worker2/command")
        print(f"  GET http://{args.host}:{args.port}/health")
        print(f"  GET http://{args.host}:{args.port}/tasks")
        print(f"  POST http://{args.host}:{args.port}/tasks/add - 添加任务")
        print()

    # 创建并启动HTTP服务器
    server = HTTPServer(host=args.host, port=args.port)

    try:
        server.run(debug=args.debug, enable_input=args.input)
    except KeyboardInterrupt:
        print("\n正在停止HTTP服务器...")


if __name__ == "__main__":
    main()