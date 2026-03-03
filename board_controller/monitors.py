"""监控器 - 挂死检测和启动监控"""

import asyncio
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime


class HangMonitor:
    """挂死监控器

    检测单板挂死：
    - 串口无输出超过阈值时间
    - 无法Ping通
    - 两者同时满足才判定为挂死
    """

    def __init__(self, connection_manager):
        """
        Args:
            connection_manager: ConnectionManager 实例
        """
        self.connections = connection_manager
        self.config = {
            "serial_timeout": 60,      # 串口无输出超时(秒)
            "ping_timeout": 10,         # Ping超时(秒)
            "consecutive_failures": 3   # 连续失败次数
        }

    async def detect(
        self,
        timeout: int = 60,
        strict_mode: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """执行挂死检测

        Args:
            timeout: 检测持续时间(秒)
            strict_mode: 严格模式（串口+网络都无响应）

        Returns:
            (is_hung, details): 是否挂死和详细信息
        """
        start_time = datetime.now()
        details = {
            "serial_activity": False,
            "ping_success": False,
            "consecutive_ping_failures": 0,
            "duration_sec": 0
        }

        while (datetime.now() - start_time).total_seconds() < timeout:
            # 检查串口活动
            serial_active = await self._check_serial_activity()
            details["serial_activity"] = serial_active

            # 检查Ping
            ping_ok = await self.connections.ping()
            details["ping_success"] = ping_ok

            if not ping_ok:
                details["consecutive_ping_failures"] += 1
            else:
                details["consecutive_ping_failures"] = 0

            # 判断是否挂死
            is_hung = self._is_hung(details, strict_mode)

            if is_hung:
                details["duration_sec"] = \
                    (datetime.now() - start_time).total_seconds()
                return True, details

            await asyncio.sleep(5)

        details["duration_sec"] = (datetime.now() - start_time).total_seconds()
        return False, details

    async def _check_serial_activity(self) -> bool:
        """检查串口活动"""
        output = await self.connections.read_serial_output(timeout=2)
        if output:
            return True

        # 检查最后活动时间
        activity_age = self.connections.get_serial_activity_age()
        if activity_age is not None and activity_age < self.config["serial_timeout"]:
            return True

        return False

    def _is_hung(self, details: Dict[str, Any], strict_mode: bool) -> bool:
        """判断是否挂死"""
        if strict_mode:
            # 严格模式：串口+网络都无响应
            return (
                not details["serial_activity"] and
                details["consecutive_ping_failures"] >= self.config["consecutive_failures"]
            )
        else:
            # 宽松模式：任一条件满足即判定挂死
            return (
                not details["serial_activity"] or
                details["consecutive_ping_failures"] >= self.config["consecutive_failures"]
            )

    async def quick_check(self) -> bool:
        """快速检查是否挂死（检查10秒）"""
        is_hung, _ = await self.detect(timeout=10, strict_mode=True)
        return is_hung


class BootMonitor:
    """启动监控器

    通过关键字检测系统启动完成
    """

    def __init__(self, connection_manager, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            connection_manager: ConnectionManager 实例
            config: 配置字典
        """
        self.connections = connection_manager
        self.config = config or self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "boot_keywords": ["login:", "root@", "# "],
            "timeout": 300,           # 启动超时(秒)
            "check_interval": 5,       # 检查间隔(秒)
            "require_ping": True,      # 是否需要Ping成功
        }

    async def wait_for_boot(
        self,
        keywords: Optional[List[str]] = None,
        timeout: int = 300,
        verify_ping: bool = True
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """等待系统启动完成

        Args:
            keywords: 启动关键字列表
            timeout: 超时时间(秒)
            verify_ping: 是否验证Ping成功

        Returns:
            (success, output, metrics): 是否成功、输出内容、指标
        """
        keywords = keywords or self.config["boot_keywords"]
        start_time = datetime.now()
        output_buffer = []
        metrics = {
            "keywords_matched": [],
            "ping_verified": False,
            "duration_sec": 0,
            "serial_lines": 0
        }

        # 等待Ping成功（如果需要）
        if verify_ping:
            ping_ok = await self._wait_for_ping(timeout=60)
            if ping_ok:
                metrics["ping_verified"] = True

        # 监控输出
        while True:
            elapsed = (datetime.now() - start_time).total_seconds()

            if elapsed >= timeout:
                return False, "\n".join(output_buffer), {
                    **metrics,
                    "error": "timeout"
                }

            # 读取输出
            output = await self.connections.read_serial_output(timeout=2)
            if output:
                output_buffer.append(output)
                metrics["serial_lines"] += 1

                # 检查关键字
                for keyword in keywords:
                    if keyword in output and keyword not in metrics["keywords_matched"]:
                        metrics["keywords_matched"].append(keyword)

                        # 所有关键字都匹配
                        if len(metrics["keywords_matched"]) == len(keywords):
                            metrics["duration_sec"] = elapsed
                            return True, "\n".join(output_buffer), metrics

            await asyncio.sleep(self.config["check_interval"])

    async def _wait_for_ping(self, timeout: int = 60) -> bool:
        """等待Ping成功"""
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            if await self.connections.ping():
                return True
            await asyncio.sleep(5)

        return False

    async def wait_for_prompt(
        self,
        prompt: str = "# ",
        timeout: int = 60
    ) -> bool:
        """等待命令提示符"""
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            line = await self.connections.read_serial_output(timeout=2)
            if line and prompt in line:
                return True
            await asyncio.sleep(1)

        return False
