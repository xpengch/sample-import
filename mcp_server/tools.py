"""MCP Tools for chip fault localization.

This module defines the interface for testing tools that can be used
to validate hypotheses about chip faults.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    """测试结果数据类"""
    test_id: str
    test_type: str
    status: TestStatus
    output: str
    metrics: Dict[str, Any]
    duration_ms: int
    error_message: Optional[str] = None
    timestamp: Optional[str] = None


class ToolInterface(ABC):
    """测试工具接口基类"""

    @abstractmethod
    def get_name(self) -> str:
        """获取工具名称"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """获取工具描述"""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行测试

        Args:
            params: 测试参数

        Returns:
            TestResult: 测试结果
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查工具是否可用"""
        pass


class ClockTestTool(ToolInterface):
    """时钟域测试工具接口"""

    def get_name(self) -> str:
        return "clock_test"

    def get_description(self) -> str:
        return "测试时钟域相关问题，包括时钟偏斜、跨时钟域等"

    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行时钟域测试"""
        raise NotImplementedError("请在子类中实现")

    def is_available(self) -> bool:
        raise NotImplementedError("请在子类中实现")


class PowerTestTool(ToolInterface):
    """电源测试工具接口"""

    def get_name(self) -> str:
        return "power_test"

    def get_description(self) -> str:
        return "测试电源相关问题，包括电压、电流、功耗等"

    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行电源测试"""
        raise NotImplementedError("请在子类中实现")

    def is_available(self) -> bool:
        raise NotImplementedError("请在子类中实现")


class TemperatureTestTool(ToolInterface):
    """温度测试工具接口"""

    def get_name(self) -> str:
        return "temperature_test"

    def get_description(self) -> str:
        return "测试温度相关问题，包括过热、热梯度等"

    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行温度测试"""
        raise NotImplementedError("请在子类中实现")

    def is_available(self) -> bool:
        raise NotImplementedError("请在子类中实现")


class GeneralTestTool(ToolInterface):
    """通用测试工具接口"""

    def get_name(self) -> str:
        return "general_test"

    def get_description(self) -> str:
        return "通用测试工具，用于常规功能验证"

    def execute(self, params: Dict[str, Any]) -> TestResult:
        """执行通用测试"""
        raise NotImplementedError("请在子类中实现")

    def is_available(self) -> bool:
        raise NotImplementedError("请在子类中实现")


# 测试工具注册表
TOOL_REGISTRY: Dict[str, ToolInterface] = {}


def register_tool(tool: ToolInterface) -> None:
    """注册测试工具"""
    TOOL_REGISTRY[tool.get_name()] = tool


def get_tool(name: str) -> Optional[ToolInterface]:
    """获取测试工具"""
    return TOOL_REGISTRY.get(name)


def list_tools() -> List[str]:
    """列出所有可用工具"""
    return list(TOOL_REGISTRY.keys())


def execute_test(tool_name: str, params: Dict[str, Any]) -> TestResult:
    """执行测试

    Args:
        tool_name: 工具名称
        params: 测试参数

    Returns:
        TestResult: 测试结果

    Raises:
        ValueError: 如果工具不存在或不可用
    """
    tool = get_tool(tool_name)
    if tool is None:
        raise ValueError(f"工具 '{tool_name}' 不存在")

    if not tool.is_available():
        raise ValueError(f"工具 '{tool_name}' 不可用")

    return tool.execute(params)
