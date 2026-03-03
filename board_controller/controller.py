"""统一单板控制器"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum

from .connections import ConnectionManager
from .monitors import HangMonitor, BootMonitor
from .resume import ResumeManager


class BoardMode(Enum):
    """单板模式"""
    LOCAL = "local"
    REMOTE = "remote"


class RestartType(Enum):
    """重启类型"""
    SOFT = "soft"
    HARD = "hard"
    POWER_CYCLE = "power_cycle"


class BoardController:
    """统一单板控制器

    支持本地和远程单板控制
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 配置字典
            {
                "mode": "local" or "remote",
                "serial": {...},
                "ssh": {...},
                "ping": {...},
                "boot": {...}
            }
        """
        self.config = config
        self.mode = BoardMode(config.get("mode", "local"))

        # 初始化组件
        self.connections = ConnectionManager(config)
        self.hang_monitor = HangMonitor(self.connections)
        self.boot_monitor = BootMonitor(
            self.connections,
            config.get("boot")
        )
        self.resume_manager = ResumeManager()

        self.current_status = "unknown"
        self._initialized = False

    async def initialize(self) -> bool:
        """初始化控制器"""
        self._initialized = await self.connections.initialize()
        return self._initialized

    async def restart_board(
        self,
        restart_type: str = "soft",
        wait_for_boot: bool = True,
        timeout: int = 300,
        boot_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """重启单板

        完整流程：
        1. 保存检查点
        2. 执行重启命令
        3. 等待启动完成
        4. 验证启动成功
        5. 保存检查点

        Args:
            restart_type: 重启类型 (soft/hard/power_cycle)
            wait_for_boot: 是否等待启动完成
            timeout: 启动超时时间(秒)
            boot_keywords: 启动完成关键字列表

        Returns:
            执行结果
        """
        result = {
            "success": False,
            "output": "",
            "metrics": {},
            "error": None
        }

        try:
            # 1. 保存检查点
            self.resume_manager.save_checkpoint("before_restart", {
                "action": "restart",
                "type": restart_type,
                "timestamp": datetime.now().isoformat()
            })

            # 2. 执行重启命令
            if self.mode == BoardMode.LOCAL:
                await self.connections.send_serial_command(
                    self._get_restart_command(restart_type)
                )
            else:
                await self.connections.send_ssh_command(
                    self._get_restart_command(restart_type)
                )

            result["output"] = f"重启命令已发送: {restart_type}"

            # 等待一下让重启开始
            await asyncio.sleep(2)

            # 3. 等待启动完成
            if wait_for_boot:
                self.current_status = "booting"

                boot_success, boot_output, boot_metrics = \
                    await self.boot_monitor.wait_for_boot(
                        keywords=boot_keywords,
                        timeout=timeout,
                        verify_ping=True
                    )

                result["success"] = boot_success
                result["output"] += f"\n启动输出:\n{boot_output}"
                result["metrics"] = boot_metrics

                if boot_success:
                    self.current_status = "online"

                    # 4. 验证启动成功
                    verified = await self._verify_boot()
                    if not verified:
                        result["error"] = "启动验证失败"
                        result["success"] = False

                    # 5. 保存检查点
                    self.resume_manager.save_checkpoint("after_restart", {
                        "action": "restart",
                        "status": "completed",
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    self.current_status = "offline"
                    result["error"] = boot_metrics.get("error", "启动超时")
            else:
                result["success"] = True

            return result

        except Exception as e:
            result["error"] = str(e)
            self.current_status = "error"
            return result

    async def detect_hang(
        self,
        detection_time: int = 60,
        strict_mode: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """检测单板挂死

        Args:
            detection_time: 检测持续时间(秒)
            strict_mode: 严格模式（串口+网络都无响应）

        Returns:
            (is_hung, details): 是否挂死和详细信息
        """
        return await self.hang_monitor.detect(
            timeout=detection_time,
            strict_mode=strict_mode
        )

    async def wait_for_boot(
        self,
        keywords: Optional[List[str]] = None,
        timeout: int = 300,
        verify_ping: bool = True
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """等待系统启动完成

        Args:
            keywords: 启动关键字
            timeout: 超时时间(秒)
            verify_ping: 是否验证Ping

        Returns:
            (success, output, metrics)
        """
        return await self.boot_monitor.wait_for_boot(
            keywords=keywords,
            timeout=timeout,
            verify_ping=verify_ping
        )

    async def execute_command(
        self,
        command: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """执行命令

        Args:
            command: 要执行的命令
            timeout: 超时时间(秒)

        Returns:
            执行结果
        """
        start_time = datetime.now()
        result = {
            "success": False,
            "output": "",
            "error": None
        }

        try:
            if self.mode == BoardMode.LOCAL:
                output = await self.connections.send_serial_command(
                    command,
                    timeout=timeout
                )
            else:
                output = await self.connections.send_ssh_command(
                    command,
                    timeout=timeout
                )

            result["success"] = True
            result["output"] = output
            result["duration"] = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            result["error"] = str(e)

        return result

    async def check_status(self) -> Dict[str, Any]:
        """检查单板状态

        Returns:
            状态信息
        """
        # 快速挂死检查
        is_hung = await self.hang_monitor.quick_check()

        # Ping测试
        ping_ok = await self.connections.ping()

        # 连接状态
        conn_status = self.connections.get_status()

        return {
            "status": "hung" if is_hung else ("online" if ping_ok else "offline"),
            "is_hung": is_hung,
            "ping_ok": ping_ok,
            "connection": conn_status,
            "mode": self.mode.value
        }

    def save_checkpoint(
        self,
        checkpoint_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """保存检查点"""
        return self.resume_manager.save_checkpoint(checkpoint_id, data)

    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """加载检查点"""
        return self.resume_manager.load_checkpoint(checkpoint_id)

    def can_resume(self) -> bool:
        """检查是否可以恢复"""
        return self.resume_manager.has_checkpoint()

    async def resume_from_checkpoint(self) -> Dict[str, Any]:
        """从检查点恢复"""
        return await self.resume_manager.resume()

    def get_checkpoint_info(self) -> Optional[Dict[str, Any]]:
        """获取检查点信息"""
        return self.resume_manager.get_checkpoint_info()

    def list_all_checkpoints(self) -> List[Dict[str, Any]]:
        """列出所有检查点"""
        return self.resume_manager.list_checkpoints()

    def delete_checkpoint(self) -> bool:
        """删除当前会话的检查点"""
        return self.resume_manager.delete_checkpoint()

    async def disconnect(self) -> bool:
        """断开所有连接"""
        self.current_status = "disconnected"
        return await self.connections.disconnect()

    def _get_restart_command(self, restart_type: str) -> str:
        """获取重启命令"""
        commands = {
            "soft": "reboot",
            "hard": "reboot -f",
            "power_cycle": "power_cycle_command"  # 根据实际硬件配置
        }
        return commands.get(restart_type, "reboot")

    async def _verify_boot(self) -> bool:
        """验证启动成功"""
        # 检查Ping
        ping_ok = await self.connections.ping()
        if not ping_ok:
            return False

        # 检查响应
        try:
            if self.mode == BoardMode.LOCAL:
                response = await self.connections.send_serial_command(
                    "echo OK\n",
                    timeout=5
                )
            else:
                response = await self.connections.send_ssh_command(
                    "echo OK",
                    timeout=5
                )

            return "OK" in (response or "")
        except:
            return False

    def get_status(self) -> Dict[str, Any]:
        """获取控制器状态"""
        return {
            "mode": self.mode.value,
            "current_status": self.current_status,
            "initialized": self._initialized,
            "connection": self.connections.get_status(),
            "can_resume": self.can_resume(),
            "session_id": self.resume_manager.session_id
        }
