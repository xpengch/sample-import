"""连接管理器 - 统一管理串口和网络连接"""

import asyncio
import subprocess
import platform
from typing import Dict, Any, Optional, Tuple
from enum import Enum


class ConnectionType(Enum):
    """连接类型"""
    SERIAL = "serial"
    SSH = "ssh"
    PING = "ping"


class ConnectionStatus(Enum):
    """连接状态"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"


class ConnectionManager:
    """连接管理器

    统一管理串口和网络连接，支持本地和远程模式
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 配置字典
            {
                "mode": "local" or "remote",
                "serial": {
                    "port": str,           # 如 "COM3" 或 "/dev/ttyUSB0"
                    "baudrate": int,       # 如 115200
                    "timeout": int
                },
                "ssh": {
                    "host": str,
                    "port": int,
                    "username": str,
                    "password": str,
                    "timeout": int
                },
                "ping": {
                    "host": str,
                    "timeout": int
                }
            }
        """
        self.config = config
        self.mode = config.get("mode", "local")

        # 连接配置
        self.serial_config = config.get("serial", {})
        self.ssh_config = config.get("ssh", {})
        self.ping_config = config.get("ping", {})

        # 连接状态
        self.serial_connected = False
        self.ssh_connected = False
        self.last_serial_activity: Optional[float] = None
        self.last_ping_success: Optional[float] = None

        # 串口连接对象（延迟初始化）
        self._serial_conn = None

        # SSH连接对象（延迟初始化）
        self._ssh_conn = None

    async def initialize(self) -> bool:
        """初始化连接"""
        try:
            if self.mode == "local":
                # 初始化串口连接
                self.serial_connected = await self._connect_serial()
            else:
                # 初始化SSH连接
                self.ssh_connected = await self._connect_ssh()

            # 测试Ping
            ping_ok = await self.ping()
            if ping_ok:
                self.last_ping_success = asyncio.get_event_loop().time()

            return True
        except Exception as e:
            print(f"连接初始化失败: {e}")
            return False

    async def _connect_serial(self) -> bool:
        """连接串口"""
        try:
            import serial

            port = self.serial_config.get("port", "COM3")
            baudrate = self.serial_config.get("baudrate", 115200)
            timeout = self.serial_config.get("timeout", 1)

            self._serial_conn = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stop_bits=serial.STOPBITS_ONE
            )

            # 清空缓冲区
            self._serial_conn.reset_input_buffer()
            self._serial_conn.reset_output_buffer()

            return True
        except ImportError:
            print("pyserial 未安装，串口功能不可用")
            return False
        except Exception as e:
            print(f"串口连接失败: {e}")
            return False

    async def _connect_ssh(self) -> bool:
        """连接SSH"""
        try:
            import asyncssh

            host = self.ssh_config.get("host", "localhost")
            port = self.ssh_config.get("port", 22)
            username = self.ssh_config.get("username", "root")
            password = self.ssh_config.get("password", "")
            timeout = self.ssh_config.get("timeout", 30)

            self._ssh_conn = await asyncio.wait_for(
                asyncssh.connect(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    known_hosts=None
                ),
                timeout=timeout
            )

            return True
        except ImportError:
            print("asyncssh 未安装，SSH功能不可用")
            return False
        except Exception as e:
            print(f"SSH连接失败: {e}")
            return False

    async def send_serial_command(
        self,
        command: str,
        timeout: int = 10
    ) -> str:
        """通过串口发送命令"""
        if self._serial_conn is None or not self.serial_connected:
            raise RuntimeError("串口未连接")

        try:
            # 发送命令
            self._serial_conn.write((command + "\n").encode())
            self.last_serial_activity = asyncio.get_event_loop().time()

            # 读取响应
            response = b""
            start_time = asyncio.get_event_loop().time()

            while (asyncio.get_event_loop().time() - start_time) < timeout:
                if self._serial_conn.in_waiting > 0:
                    data = self._serial_conn.read(self._serial_conn.in_waiting)
                    response += data
                    # 检查是否有提示符
                    if b"#" in response or b"$" in response:
                        break

                await asyncio.sleep(0.1)

            return response.decode('utf-8', errors='ignore').strip()

        except Exception as e:
            print(f"串口命令发送失败: {e}")
            return ""

    async def send_ssh_command(
        self,
        command: str,
        timeout: int = 30
    ) -> str:
        """通过SSH发送命令"""
        if self._ssh_conn is None or not self.ssh_connected:
            raise RuntimeError("SSH未连接")

        try:
            result = await asyncio.wait_for(
                self._ssh_conn.run(command),
                timeout=timeout
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"SSH命令发送失败: {e}")
            return ""

    async def ping(self, timeout: int = 5) -> bool:
        """Ping测试"""
        host = self.ping_config.get("host", "localhost")

        try:
            if platform.system() == "Windows":
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), host]
            else:
                cmd = ["ping", "-c", "1", "-W", str(timeout), host]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await asyncio.wait_for(
                process.communicate(),
                timeout=timeout + 1
            )

            if process.returncode == 0:
                self.last_ping_success = asyncio.get_event_loop().time()
                return True

            return False
        except Exception:
            return False

    async def read_serial_output(self, timeout: int = 2) -> Optional[str]:
        """读取串口输出"""
        if self._serial_conn is None or not self.serial_connected:
            return None

        try:
            if self._serial_conn.in_waiting > 0:
                data = self._serial_conn.read(self._serial_conn.in_waiting)
                self.last_serial_activity = asyncio.get_event_loop().time()
                return data.decode('utf-8', errors='ignore')
            return None
        except Exception as e:
            print(f"读取串口输出失败: {e}")
            return None

    def get_serial_activity_age(self) -> Optional[float]:
        """获取串口活动时间（秒）"""
        if self.last_serial_activity is None:
            return None

        return asyncio.get_event_loop().time() - self.last_serial_activity

    def get_ping_activity_age(self) -> Optional[float]:
        """获取Ping活动时间（秒）"""
        if self.last_ping_success is None:
            return None

        return asyncio.get_event_loop().time() - self.last_ping_success

    async def disconnect(self) -> bool:
        """断开所有连接"""
        try:
            if self._serial_conn is not None and self.serial_connected:
                self._serial_conn.close()
                self.serial_connected = False

            if self._ssh_conn is not None and self.ssh_connected:
                self._ssh_conn.close()
                self.ssh_connected = False

            return True
        except Exception as e:
            print(f"断开连接失败: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """获取连接状态"""
        return {
            "mode": self.mode,
            "serial_connected": self.serial_connected,
            "ssh_connected": self.ssh_connected,
            "last_serial_activity": self.last_serial_activity,
            "last_ping_success": self.last_ping_success,
            "serial_activity_age": self.get_serial_activity_age(),
            "ping_activity_age": self.get_ping_activity_age()
        }
