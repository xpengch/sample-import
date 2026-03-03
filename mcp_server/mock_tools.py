"""Mock implementations of MCP tools for testing and development.

This module provides mock implementations of testing tools that can be used
when real hardware is not available.
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from mcp_server.tools import (
    ClockTestTool, PowerTestTool, TemperatureTestTool, GeneralTestTool,
    BoardControlTool,
    TestResult, TestStatus, register_tool
)


class MockClockTestTool(ClockTestTool):
    """时钟域测试工具 Mock 实现"""

    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行时钟域测试（Mock）"""
        start_time = time.time()

        # 模拟测试逻辑
        test_case = params.get("test_case", "default")

        # 模拟不同测试场景的结果
        if "crosstalk" in test_case.lower():
            status = TestStatus.FAILED
            output = "检测到时钟串扰问题"
            metrics = {
                "skew_ps": 150,
                "jitter_ps": 45,
                "crosstalk_db": -20
            }
        elif "setup_violation" in test_case.lower():
            status = TestStatus.FAILED
            output = "检测到建立时间违例"
            metrics = {
                "setup_margin_ps": -25,
                "hold_margin_ps": 30
            }
        elif "hold_violation" in test_case.lower():
            status = TestStatus.FAILED
            output = "检测到保持时间违例"
            metrics = {
                "setup_margin_ps": 20,
                "hold_margin_ps": -15
            }
        else:
            status = TestStatus.PASSED
            output = "时钟域测试通过"
            metrics = {
                "skew_ps": random.uniform(10, 50),
                "jitter_ps": random.uniform(5, 20)
            }

        duration_ms = int((time.time() - start_time) * 1000)

        return TestResult(
            test_id=params.get("test_id", f"clock_{int(time.time())}"),
            test_type=self.get_name(),
            status=status,
            output=output,
            metrics=metrics,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat()
        )

    def is_available(self) -> bool:
        """Mock 工具始终可用"""
        return True


class MockPowerTestTool(PowerTestTool):
    """电源测试工具 Mock 实现"""

    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行电源测试（Mock）"""
        start_time = time.time()

        test_case = params.get("test_case", "default")

        # 模拟不同测试场景的结果
        if "undervoltage" in test_case.lower():
            status = TestStatus.FAILED
            output = "检测到欠压问题"
            metrics = {
                "voltage_v": 0.95,
                "current_ma": 120,
                "power_mw": 114
            }
        elif "overcurrent" in test_case.lower():
            status = TestStatus.FAILED
            output = "检测到过流问题"
            metrics = {
                "voltage_v": 1.2,
                "current_ma": 350,
                "power_mw": 420
            }
        else:
            status = TestStatus.PASSED
            output = "电源测试通过"
            metrics = {
                "voltage_v": random.uniform(1.1, 1.25),
                "current_ma": random.uniform(100, 150),
                "power_mw": random.uniform(110, 190)
            }

        duration_ms = int((time.time() - start_time) * 1000)

        return TestResult(
            test_id=params.get("test_id", f"power_{int(time.time())}"),
            test_type=self.get_name(),
            status=status,
            output=output,
            metrics=metrics,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat()
        )

    def is_available(self) -> bool:
        """Mock 工具始终可用"""
        return True


class MockTemperatureTestTool(TemperatureTestTool):
    """温度测试工具 Mock 实现"""

    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行温度测试（Mock）"""
        start_time = time.time()

        test_case = params.get("test_case", "default")

        # 模拟不同测试场景的结果
        if "overheat" in test_case.lower():
            status = TestStatus.FAILED
            output = "检测到过热问题"
            metrics = {
                "temperature_c": 95,
                "thermal_gradient_c_per_cm": 15
            }
        elif "thermal_cycling" in test_case.lower():
            status = TestStatus.FAILED
            output = "检测到热循环异常"
            metrics = {
                "temperature_c": 75,
                "cycle_count": 1000,
                "drift_percent": 5.2
            }
        else:
            status = TestStatus.PASSED
            output = "温度测试通过"
            metrics = {
                "temperature_c": random.uniform(45, 65),
                "thermal_gradient_c_per_cm": random.uniform(2, 8)
            }

        duration_ms = int((time.time() - start_time) * 1000)

        return TestResult(
            test_id=params.get("test_id", f"temp_{int(time.time())}"),
            test_type=self.get_name(),
            status=status,
            output=output,
            metrics=metrics,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat()
        )

    def is_available(self) -> bool:
        """Mock 工具始终可用"""
        return True


class MockGeneralTestTool(GeneralTestTool):
    """通用测试工具 Mock 实现"""

    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行通用测试（Mock）"""
        start_time = time.time()

        test_type = params.get("test_type", "basic")
        test_data = params.get("test_data", {})

        # 模拟测试执行
        status = TestStatus.PASSED
        output = f"通用测试 ({test_type}) 通过"

        metrics = {
            "test_type": test_type,
            "data_points": len(test_data),
            "execution_time_ms": int((time.time() - start_time) * 1000)
        }

        duration_ms = int((time.time() - start_time) * 1000)

        return TestResult(
            test_id=params.get("test_id", f"general_{int(time.time())}"),
            test_type=self.get_name(),
            status=status,
            output=output,
            metrics=metrics,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat()
        )

    def is_available(self) -> bool:
        """Mock 工具始终可用"""
        return True


class MockBoardControlTool(BoardControlTool):
    """单板控制工具 Mock 实现"""

    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行单板控制操作（Mock）"""
        start_time = time.time()
        action = params.get("action", "")

        # 模拟不同操作的结果
        if action == "restart":
            status = TestStatus.PASSED
            output = "Mock: 单板重启成功"
            metrics = {
                "restart_type": params.get("restart_type", "soft"),
                "boot_duration_sec": random.uniform(30, 90)
            }
        elif action == "detect_hang":
            # 模拟挂死检测
            is_hung = params.get("simulate_hang", False)
            status = TestStatus.PASSED
            output = f"Mock: 挂死检测完成 - {'检测到挂死' if is_hung else '单板正常'}"
            metrics = {
                "is_hung": is_hung,
                "serial_active": not is_hung,
                "ping_success": not is_hung
            }
        elif action == "wait_boot":
            status = TestStatus.PASSED
            output = "Mock: 等待启动完成"
            metrics = {
                "boot_duration_sec": random.uniform(30, 90),
                "keywords_matched": ["login:", "root@"]
            }
        elif action == "check_status":
            status = TestStatus.PASSED
            output = "Mock: 单板状态检查完成"
            metrics = {
                "status": "online",
                "ping_ok": True,
                "serial_connected": True
            }
        elif action == "save_checkpoint":
            status = TestStatus.PASSED
            output = f"Mock: 检查点已保存 - {params.get('checkpoint_id', 'unknown')}"
            metrics = {
                "checkpoint_id": params.get("checkpoint_id"),
                "saved": True
            }
        elif action == "load_checkpoint":
            status = TestStatus.PASSED
            output = f"Mock: 检查点已加载 - {params.get('checkpoint_id', 'unknown')}"
            metrics = {
                "checkpoint_id": params.get("checkpoint_id"),
                "loaded": True
            }
        else:
            status = TestStatus.ERROR
            output = f"Mock: 未知操作 - {action}"
            metrics = {}
            return TestResult(
                test_id=params.get("test_id", f"board_{int(time.time())}"),
                test_type=self.get_name(),
                status=status,
                output=output,
                metrics=metrics,
                duration_ms=0,
                error_message=f"Unknown action: {action}",
                timestamp=datetime.now().isoformat()
            )

        duration_ms = int((time.time() - start_time) * 1000)

        return TestResult(
            test_id=params.get("test_id", f"board_{action}_{int(time.time())}"),
            test_type=self.get_name(),
            status=status,
            output=output,
            metrics=metrics,
            duration_ms=duration_ms,
            timestamp=datetime.now().isoformat()
        )

    def is_available(self) -> bool:
        """Mock 工具始终可用"""
        return True


def initialize_mock_tools() -> None:
    """初始化并注册所有 Mock 工具"""
    register_tool(MockClockTestTool())
    register_tool(MockPowerTestTool())
    register_tool(MockTemperatureTestTool())
    register_tool(MockGeneralTestTool())
    register_tool(MockBoardControlTool())


# 自动初始化
initialize_mock_tools()
