"""
Flask HTTP服务器 - 提供HTTP API接口
"""
import json
import logging
import threading
import queue
import time
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request


class HTTPServer:
    """HTTP API服务器"""

    def __init__(self, host: str = "localhost", port: int = 5000):
        self.host = host
        self.port = port

        # 禁用Flask/Werkzeug的默认日志
        self._disable_flask_logging()

        self.app = Flask(__name__)

        # 配置Flask应用不输出日志
        self.app.logger.setLevel(logging.CRITICAL)
        self.app.logger.disabled = True

        # 设置Flask配置以禁用日志
        self.app.config['LOGGER_HANDLER_POLICY'] = 'never'
        self.app.config['DEBUG'] = False
        self.app.config['TESTING'] = False
        self.logger = self._setup_logger()

        # 任务队列和相关状态
        self.task_queue = queue.Queue()
        self.pending_tasks = {}  # 存储待处理任务的任务ID
        self.current_task_id = 0
        self.task_lock = threading.Lock()
        self.input_thread = None
        self.running = False

        self._setup_routes()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        import os
        logger = logging.getLogger("HTTPServer")
        logger.setLevel(logging.INFO)

        # 避免重复添加处理器
        if logger.handlers:
            return logger

        # 使用绝对路径创建logs目录（如果不存在）
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "http_server.log")

        # 只创建文件处理器，不输出到控制台
        file_handler = logging.FileHandler(log_file, encoding="utf-8", mode='a')
        file_handler.setLevel(logging.INFO)

        # 设置立即刷新（设置为0表示立即写入）
        file_handler.stream.reconfigure(line_buffering=True)

        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        # 只添加文件处理器
        logger.addHandler(file_handler)

        # 确保日志立即写入
        logger.propagate = False

        return logger

    def _disable_flask_logging(self):
        """禁用Flask/Werkzeug的默认日志输出"""
        import logging
        # 禁用werkzeug日志
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.CRITICAL)
        werkzeug_logger.disabled = True

        # 禁用flask.app日志
        flask_logger = logging.getLogger('flask.app')
        flask_logger.setLevel(logging.CRITICAL)
        flask_logger.disabled = True

        # 禁用flask日志
        flask_base_logger = logging.getLogger('flask')
        flask_base_logger.setLevel(logging.CRITICAL)
        flask_base_logger.disabled = True

    def _get_next_task(self) -> Dict[str, Any]:
        """获取下一个任务"""
        try:
            # 如果有待完成的任务，返回空任务
            if self.pending_tasks:
                return {
                    "command": "",
                    "buildin": False,
                    "task_id": None
                }

            # 尝试从队列获取任务（非阻塞）
            try:
                command = self.task_queue.get_nowait()
                self.current_task_id += 1
                task_id = self.current_task_id

                # 判断是否为内置命令
                buildin = command.lower() in ["init", "cleanup", "status"]

                # 添加到待处理任务
                self.pending_tasks[task_id] = {
                    "command": command,
                    "buildin": buildin,
                    "assigned_time": datetime.now().isoformat()
                }

                return {
                    "command": command,
                    "buildin": buildin,
                    "task_id": task_id
                }
            except queue.Empty:
                # 没有任务
                return {
                    "command": "",
                    "buildin": False,
                    "task_id": None
                }
        except Exception as e:
            self.logger.error(f"获取任务时出错: {e}")
            return {
                "command": "",
                "buildin": False,
                "task_id": None
            }

    def _handle_task_response(self, task_id: str, command_result: str):
        """处理任务响应"""
        try:
            task_id_int = int(task_id)
            with self.task_lock:
                if task_id_int in self.pending_tasks:
                    task = self.pending_tasks[task_id_int]
                    self.logger.info(f"任务 {task_id_int} 完成: {task['command']} -> {command_result}")
                    del self.pending_tasks[task_id_int]

                    response = {
                        "code": 0,
                        "data": {
                            "buildin": task.get("buildin", False),
                            "command": task.get("command", ""),
                            "message": f"任务 {task_id_int} 完成"
                        }
                    }
                else:
                    response = {
                        "code": 404,
                        "data": {
                            "buildin": False,
                            "command": "",
                            "message": f"任务 {task_id} 不存在或已完成"
                        }
                    }

            return jsonify(response)

        except ValueError:
            error_response = {
                "code": 400,
                "data": {
                    "buildin": False,
                    "command": "",
                    "message": "无效的任务ID"
                }
            }
            return jsonify(error_response), 400
        except Exception as e:
            self.logger.error(f"处理任务响应时出错: {e}")
            error_response = {
                "code": 500,
                "data": {
                    "buildin": False,
                    "command": "",
                    "message": "服务器内部错误"
                }
            }
            return jsonify(error_response), 500

    def _user_input_listener(self):
        """监听用户输入的线程函数"""
        self.logger.info("开始监听用户输入，输入命令添加到任务队列...")
        while self.running:
            try:
                user_input = input().strip()
                if user_input and self.running:
                    self.task_queue.put(user_input)
                    self.logger.info(f"添加命令到队列: {user_input}")
            except EOFError:
                # 输入结束（如Ctrl+D）
                self.logger.info("用户输入结束")
                break
            except KeyboardInterrupt:
                self.logger.info("收到中断信号，停止输入监听")
                break
            except Exception as e:
                self.logger.error(f"读取用户输入时出错: {e}")
                time.sleep(1)

    def start_input_listener(self):
        """启动用户输入监听"""
        self.running = True
        self.input_thread = threading.Thread(target=self._user_input_listener)
        self.input_thread.daemon = True
        self.input_thread.start()

    def stop_input_listener(self):
        """停止用户输入监听"""
        self.running = False

    def _setup_routes(self):
        """设置路由"""

        @self.app.route('/worker2/command', methods=['GET'])
        def worker2_command():
            """处理worker2 command请求"""
            try:
                # 获取查询参数
                task_id = request.args.get('task_id')
                command_result = request.args.get('command_result')

                # 如果是任务结果响应
                if task_id and command_result:
                    self.logger.info(f"任务结果: {task_id} -> {command_result}")
                    return self._handle_task_response(task_id, command_result)

                # 获取下一个任务
                task_info = self._get_next_task()
                response = {
                    "code": 0,
                    "data": {
                        "buildin": task_info["buildin"],
                        "command": task_info["command"],
                        "task_id": task_info["task_id"]
                    }
                }

                # 只有当有任务时才记录日志
                if task_info["command"]:
                    self.logger.info(f"分配任务: {response}")

                return jsonify(response)

            except Exception as e:
                self.logger.error(f"处理 /worker2/command 请求时出错: {e}")
                error_response = {
                    "code": 500,
                    "data": {
                        "buildin": False,
                        "command": None,
                        "task_id": None
                    }
                }
                return jsonify(error_response), 500

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康检查接口"""
            try:
                response = {
                    "code": 200,
                    "data": {
                        "status": "healthy",
                        "timestamp": datetime.now().isoformat(),
                        "server": "HTTPServer"
                    }
                }
                return jsonify(response)
            except Exception as e:
                self.logger.error(f"健康检查出错: {e}")
                return jsonify({"code": 500, "data": {"status": "unhealthy"}}), 500

        @self.app.route('/tasks', methods=['GET'])
        def get_tasks():
            """获取当前任务状态"""
            try:
                queue_size = self.task_queue.qsize()
                pending_count = len(self.pending_tasks)

                response = {
                    "code": 200,
                    "data": {
                        "queue_size": queue_size,
                        "pending_tasks": pending_count,
                        "pending_task_details": self.pending_tasks
                    }
                }
                return jsonify(response)
            except Exception as e:
                self.logger.error(f"获取任务状态时出错: {e}")
                return jsonify({"code": 500, "data": {"error": str(e)}}), 500

        @self.app.route('/tasks/add', methods=['POST'])
        def add_task():
            """添加任务到队列"""
            try:
                task_data = request.get_json()
                if not task_data or 'command' not in task_data:
                    return jsonify({
                        "code": 400,
                        "data": {"message": "缺少command参数"}
                    }), 400

                command = task_data['command']
                self.task_queue.put(command)
                self.logger.info(f"通过API添加命令到队列: {command}")

                response = {
                    "code": 200,
                    "data": {
                        "message": f"命令 '{command}' 已添加到队列",
                        "queue_size": self.task_queue.qsize()
                    }
                }
                return jsonify(response)
            except Exception as e:
                self.logger.error(f"添加任务时出错: {e}")
                return jsonify({"code": 500, "data": {"error": str(e)}}), 500

        @self.app.route('/', methods=['GET'])
        def index():
            """根路径"""
            response = {
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
            return jsonify(response)

        # 添加请求日志中间件
        @self.app.before_request
        def log_request():
            self.logger.info(f"收到请求: {request.method} {request.path} from {request.remote_addr}")

        @self.app.after_request
        def log_response(response):
            self.logger.info(f"响应状态: {response.status_code} for {request.method} {request.path}")
            return response

    def run(self, debug: bool = False, enable_input: bool = True):
        """启动HTTP服务器"""
        self.logger.info(f"启动HTTP服务器在 {self.host}:{self.port}")

        if enable_input:
            print("=== HTTP服务器已启动 ===")
            print(f"服务地址: http://{self.host}:{self.port}")
            print("=== 任务队列输入模式 ===")
            print("您可以在此输入命令，命令将被添加到任务队列中：")
            print("  - 输入 'init'、'cleanup'、'status' 将设置 buildin=true")
            print("  - 输入 'quit' 或按 Ctrl+C 退出")
            print("=== 命令输入 ===")

            # 启动用户输入监听
            self.start_input_listener()

        try:
            self.app.run(host=self.host, port=self.port, debug=debug, threaded=True)
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在停止HTTP服务器...")
        finally:
            if enable_input:
                self.stop_input_listener()

    def get_app(self):
        """获取Flask应用实例（用于部署）"""
        return self.app


def main():
    """主函数"""
    server = HTTPServer(host="localhost", port=5000)
    server.run(debug=True)


if __name__ == "__main__":
    main()