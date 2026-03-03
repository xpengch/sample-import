# 芯片样片问题定位系统

基于 Claude Code Skills 的芯片故障智能分析系统。

## 架构

- **Skills (Markdown)**: 分析知识和流程定义
- **MCP Tools**: 测试工具接口
- **Claude Code**: 主控，自动选择和执行

## 使用

在 Claude Code 对话中直接使用：

```
请帮我定位这个故障：[粘贴日志]
```

系统将：
1. 自动选择合适的分析 Skill
2. 生成故障假设
3. 规划并执行测试
4. 迭代验证直到定位成功

## 状态

状态文件保存在：`~/.chip-fault-locator/state.json`

## 开发

```bash
# 安装依赖
pip install -r requirements.txt

# 测试 MCP Server
python -m mcp_server.server
```
