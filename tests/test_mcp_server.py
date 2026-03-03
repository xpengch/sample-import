"""Tests for MCP Server."""
import pytest
from mcp_server.tools import (
    ClockTestTool, PowerTestTool, TemperatureTestTool, GeneralTestTool,
    TestStatus, register_tool, get_tool, list_tools, execute_test,
    TOOL_REGISTRY
)
from mcp_server.mock_tools import (
    MockClockTestTool, MockPowerTestTool,
    MockTemperatureTestTool, MockGeneralTestTool,
    initialize_mock_tools
)


@pytest.fixture(autouse=True)
def clear_registry():
    """每个测试前清理工具注册表"""
    TOOL_REGISTRY.clear()
    yield
    TOOL_REGISTRY.clear()


def test_mock_clock_tool():
    """测试时钟域 Mock 工具"""
    tool = MockClockTestTool()
    assert tool.get_name() == "clock_test"
    assert tool.is_available()

    result = tool.execute({
        "test_id": "test_001",
        "test_case": "crosstalk"
    })

    assert result.test_id == "test_001"
    assert result.test_type == "clock_test"
    assert result.status == TestStatus.FAILED
    assert "时钟串扰" in result.output
    assert result.metrics["skew_ps"] == 150


def test_mock_power_tool():
    """测试电源 Mock 工具"""
    tool = MockPowerTestTool()
    assert tool.get_name() == "power_test"
    assert tool.is_available()

    result = tool.execute({
        "test_id": "test_002",
        "test_case": "undervoltage"
    })

    assert result.test_id == "test_002"
    assert result.status == TestStatus.FAILED
    assert "欠压" in result.output
    assert result.metrics["voltage_v"] == 0.95


def test_mock_temperature_tool():
    """测试温度 Mock 工具"""
    tool = MockTemperatureTestTool()
    assert tool.get_name() == "temperature_test"
    assert tool.is_available()

    result = tool.execute({
        "test_id": "test_003",
        "test_case": "overheat"
    })

    assert result.test_id == "test_003"
    assert result.status == TestStatus.FAILED
    assert "过热" in result.output
    assert result.metrics["temperature_c"] == 95


def test_mock_general_tool():
    """测试通用 Mock 工具"""
    tool = MockGeneralTestTool()
    assert tool.get_name() == "general_test"
    assert tool.is_available()

    result = tool.execute({
        "test_id": "test_004",
        "test_type": "basic",
        "test_data": {"key": "value"}
    })

    assert result.test_id == "test_004"
    assert result.status == TestStatus.PASSED
    assert result.metrics["data_points"] == 1


def test_tool_registry():
    """测试工具注册表"""
    tool = MockClockTestTool()
    register_tool(tool)

    assert "clock_test" in list_tools()
    retrieved = get_tool("clock_test")
    assert retrieved is tool


def test_execute_test_through_registry():
    """测试通过注册表执行测试"""
    initialize_mock_tools()

    result = execute_test("clock_test", {
        "test_id": "test_005",
        "test_case": "setup_violation"
    })

    assert result.test_id == "test_005"
    assert result.status == TestStatus.FAILED
    assert "建立时间违例" in result.output


def test_execute_nonexistent_tool():
    """测试执行不存在的工具"""
    initialize_mock_tools()

    with pytest.raises(ValueError, match="工具 'nonexistent' 不存在"):
        execute_test("nonexistent", {})


def test_server_initialization():
    """测试服务器初始化"""
    from mcp_server.server import ChipFaultLocatorServer

    server = ChipFaultLocatorServer(mock_mode=True)
    tools = server.list_available_tools()

    assert "clock_test" in tools
    assert "power_test" in tools
    assert "temperature_test" in tools
    assert "general_test" in tools


def test_server_sync_execution():
    """测试服务器同步执行"""
    from mcp_server.server import ChipFaultLocatorServer

    server = ChipFaultLocatorServer(mock_mode=True)
    result = server.execute_tool_sync("clock_test", {
        "test_id": "test_006",
        "test_case": "default"
    })

    assert result["test_id"] == "test_006"
    assert result["status"] == "passed"
    assert "通过" in result["output"]
