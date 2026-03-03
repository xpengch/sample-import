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


def initialize_mock_tools() -> None:
    """初始化并注册所有 Mock 工具"""
    register_tool(MockClockTestTool())
    register_tool(MockPowerTestTool())
    register_tool(MockTemperatureTestTool())
    register_tool(MockGeneralTestTool())


# 自动初始化
initialize_mock_tools()
