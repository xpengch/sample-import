"""MCP Server for chip fault localization.

This module provides a Model Context Protocol (MCP) server that exposes
testing tools for validating hypotheses about chip faults.

The server can run in two modes:
1. Mock mode: Uses mock implementations for development and testing
2. Real mode: Uses real hardware tools (when available)
"""

import asyncio
import json
import logging
from typing import Any, Optional
from datetime import datetime

# MCP SDK imports (when available)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP SDK not available, running in standalone mode")

from mcp_server.tools import execute_test, list_tools, get_tool
from mcp_server.mock_tools import initialize_mock_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChipFaultLocatorServer:
    """芯片故障定位 MCP 服务器"""

    def __init__(self, mock_mode: bool = True):
        """初始化服务器

        Args:
            mock_mode: 是否使用 Mock 模式
        """
        self.mock_mode = mock_mode
        self.server = None
        self._initialize()

    def _initialize(self):
        """初始化服务器和工具"""
        if self.mock_mode:
            logger.info("Initializing in Mock mode")
            initialize_mock_tools()
        else:
            logger.info("Initializing in Real mode")
            # TODO: 初始化真实工具
            pass

        if MCP_AVAILABLE:
            self.server = Server("chip-fault-locator")
            self._setup_handlers()
        else:
            logger.warning("MCP SDK not available, running in standalone mode")

    def _setup_handlers(self):
        """设置 MCP 处理器"""
        if not self.server:
            return

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """列出所有可用工具"""
            tools = []
            for tool_name in list_tools():
                tool = get_tool(tool_name)
                if tool:
                    tools.append(Tool(
                        name=tool.get_name(),
                        description=tool.get_description(),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "test_id": {"type": "string"},
                                "test_case": {"type": "string"}
                            },
                            "required": ["test_id"]
                        }
                    ))
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Any) -> list[TextContent]:
            """执行工具调用"""
            try:
                result = execute_test(name, arguments)
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "test_id": result.test_id,
                        "test_type": result.test_type,
                        "status": result.status.value,
                        "output": result.output,
                        "metrics": result.metrics,
                        "duration_ms": result.duration_ms,
                        "timestamp": result.timestamp
                    }, ensure_ascii=False, indent=2)
                )]
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e)
                    }, ensure_ascii=False)
                )]

    async def run(self):
        """运行服务器"""
        if MCP_AVAILABLE and self.server:
            logger.info("Starting MCP server...")
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        else:
            logger.info("Running in standalone mode (no MCP server)")
            # Standalone mode for testing
            await self._run_standalone()

    async def _run_standalone(self):
        """独立模式运行（用于测试）"""
        logger.info("Available tools: %s", list_tools())
        logger.info("Server ready for direct API calls")

    def list_available_tools(self) -> list[str]:
        """列出可用工具（同步接口）"""
        return list_tools()

    def execute_tool_sync(self, tool_name: str, params: dict) -> dict:
        """同步执行工具（用于非 MCP 场景）"""
        try:
            result = execute_test(tool_name, params)
            return {
                "test_id": result.test_id,
                "test_type": result.test_type,
                "status": result.status.value,
                "output": result.output,
                "metrics": result.metrics,
                "duration_ms": result.duration_ms,
                "timestamp": result.timestamp
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"error": str(e)}


# 全局服务器实例
_server_instance: Optional[ChipFaultLocatorServer] = None


def get_server(mock_mode: bool = True) -> ChipFaultLocatorServer:
    """获取服务器实例"""
    global _server_instance
    if _server_instance is None:
        _server_instance = ChipFaultLocatorServer(mock_mode=mock_mode)
    return _server_instance


async def main():
    """主入口"""
    import sys

    # 检查命令行参数
    mock_mode = True
    if "--real" in sys.argv:
        mock_mode = False

    server = get_server(mock_mode=mock_mode)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
