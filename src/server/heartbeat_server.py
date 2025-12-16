"""
TCP Socket服务器 - 接收客户端心跳信息
"""
import socket
import threading
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class HeartbeatMessage:
    """心跳消息数据结构"""
    code: int
    data: str
    message: str


class HeartbeatServer:
    """心跳服务器"""

    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # 存储客户端信息
        self.running = False
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("HeartbeatServer")
        logger.setLevel(logging.INFO)

        # 创建文件处理器
        file_handler = logging.FileHandler("logs/heartbeat_server.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def start(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 设置socket超时，这样可以定期检查self.running状态
            self.server_socket.settimeout(1.0)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            self.logger.info(f"心跳服务器启动在 {self.host}:{self.port}")

            while self.running:
                try:
                    # 接受客户端连接（有超时，可以定期检查running状态）
                    try:
                        client_socket, client_address = self.server_socket.accept()
                        self.logger.info(f"新客户端连接: {client_address}")

                        # 设置客户端socket超时
                        client_socket.settimeout(1.0)

                        # 为每个客户端创建处理线程
                        client_thread = threading.Thread(
                            target=self._handle_client,
                            args=(client_socket, client_address)
                        )
                        client_thread.daemon = True
                        client_thread.start()

                    except socket.timeout:
                        # 超时是正常的，继续循环检查running状态
                        continue

                except OSError as e:
                    if self.running:
                        self.logger.error(f"接受连接时出错: {e}")

        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在停止服务器...")
        except Exception as e:
            self.logger.error(f"启动服务器失败: {e}")
        finally:
            self.stop()

    def _handle_client(self, client_socket: socket.socket, client_address: tuple):
        """处理客户端连接"""
        client_id = None

        try:
            while self.running:
                try:
                    # 接收数据（有超时设置）
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    try:
                        # 解析心跳消息
                        heartbeat = self._parse_heartbeat_message(data.decode('utf-8'))
                        if heartbeat:
                            client_id = f"{client_address[0]}:{client_address[1]}"
                            self._process_heartbeat(heartbeat, client_address)

                            # 发送确认响应
                            response = {
                                "code": 200,
                                "data": "success",
                                "message": "socket接收成功"
                            }
                            client_socket.send(json.dumps(response, ensure_ascii=False).encode('utf-8'))

                    except json.JSONDecodeError as e:
                        self.logger.error(f"解析socket消息失败: {e}")
                        error_response = {
                            "code": 400,
                            "data": "error",
                            "message": "消息格式错误"
                        }
                        client_socket.send(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

                except socket.timeout:
                    # 超时是正常的，继续循环检查running状态
                    continue
                except ConnectionResetError:
                    self.logger.info(f"客户端 {client_address} 断开连接")
                    break

        except Exception as e:
            if self.running:  # 只在服务器还在运行时记录错误
                self.logger.error(f"处理客户端 {client_address} 时出错: {e}")
        finally:
            if client_id:
                self._remove_client(client_id)
            try:
                client_socket.close()
            except Exception:
                pass
            if self.running:
                self.logger.info(f"客户端 {client_address} 连接关闭")

    def _parse_heartbeat_message(self, data: str) -> Optional[HeartbeatMessage]:
        """解析心跳消息"""
        try:
            message_dict = json.loads(data)

            # 验证必要字段
            required_fields = ['code', 'data', 'message']
            for field in required_fields:
                if field not in message_dict:
                    self.logger.error(f"心跳消息缺少必要字段: {field}")
                    return None

            return HeartbeatMessage(
                code=message_dict['code'],
                data=message_dict['data'],
                message=message_dict['message']
            )

        except Exception as e:
            self.logger.error(f"解析心跳消息时出错: {e}")
            return None

    def _process_heartbeat(self, heartbeat: HeartbeatMessage, client_address: tuple):
        """处理心跳消息"""
        # 使用客户端地址作为唯一标识
        client_id = f"{client_address[0]}:{client_address[1]}"

        # 更新客户端信息
        self.clients[client_id] = {
            "last_heartbeat": datetime.now().isoformat(),
            "code": heartbeat.code,
            "data": heartbeat.data,
            "message": heartbeat.message,
            "client_address": client_address,
            "server_received_time": datetime.now().isoformat()
        }

        self.logger.info(
            f"收到心跳 - 客户端: {client_id}, "
            f"代码: {heartbeat.code}, "
            f"数据: {heartbeat.data}, "
            f"消息: {heartbeat.message}, "
            f"地址: {client_address}"
        )

    def _remove_client(self, client_id: str):
        """移除客户端"""
        if client_id in self.clients:
            del self.clients[client_id]
            self.logger.info(f"客户端 {client_id} 已移除")

    def get_clients(self) -> Dict[str, Any]:
        """获取所有活跃客户端信息"""
        return self.clients

    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            try:
                # 首先关闭socket
                self.server_socket.close()
            except Exception as e:
                self.logger.error(f"关闭服务器socket时出错: {e}")

        # 等待所有客户端线程结束
        time.sleep(0.1)  # 给客户端处理线程一点时间完成清理

        self.logger.info("心跳服务器已停止")


def main():
    """主函数"""
    server = HeartbeatServer(host="localhost", port=8888)

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        server.stop()