# 芯片样片问题定位系统 - 安装与使用指南

## 目录

- [快速开始](#快速开始)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [MCP Server 配置](#mcp-server-配置)
- [故障排查](#故障排查)

---

## 快速开始

### 方式一：直接作为 Claude Code 项目使用（推荐）

这是最简单的使用方式，不需要额外的 MCP 配置。

1. **确保项目在正确的位置**
   ```bash
   # 项目应位于你想要分析芯片问题的目录下
   cd /path/to/your/work
   # sample_import 项目应该在这里或其父目录
   ```

2. **在 Claude Code 对话中使用**
   ```
   请帮我分析这个芯片故障问题：[粘贴日志或问题描述]
   ```

3. **Claude Code 会自动：**
   - 发现并加载 `skills/` 目录下的所有技能
   - 根据问题类型自动选择合适的分析技能
   - 执行假设生成、测试规划、验证迭代

### 方式二：使用 MCP Server（高级用户）

如果你想要将工具暴露给其他 MCP 客户端，可以配置 MCP Server。

---

## 安装步骤

### 1. 环境准备

确保你已经安装：
- Python 3.8 或更高版本
- Claude Code CLI

### 2. 安装 Python 依赖

```bash
# 进入项目目录
cd D:\ai_dir\sample_import

# 安装依赖
pip install -r requirements.txt

# 如果需要真实硬件测试，还需要：
pip install pyserial asyncssh
```

### 3. 验证安装

```bash
# 运行测试
pytest tests/ -v

# 应该看到所有测试通过 (34 tests)
```

### 4. 检查 Skills

```bash
# 检查 skills 目录结构
ls skills/

# 应该看到：
# - hypothesis-manager/    (元技能，控制迭代流程)
# - test-planner/          (测试规划)
# - clock-analysis/        (时钟域分析)
# - power-analysis/        (电源分析)
# - temp-analysis/         (温度分析)
# - signal-analysis/       (信号完整性分析)
# - memory-analysis/       (内存分析)
# - hang-analysis/         (挂死问题分析)
# - crash-analysis/        (崩溃问题分析)
# - performance-analysis/  (性能分析)
# - general-diagnose/      (通用诊断)
```

---

## 配置说明

### 单板配置 (可选，仅真实硬件测试需要)

如果你有真实硬件需要测试，配置单板参数：

```bash
# 编辑配置文件
# Windows: notepad config\board_config.yaml
# Linux/Mac: vim config/board_config.yaml
```

配置示例：
```yaml
local_board:
  mode: local
  board_id: board_001
  serial:
    port: COM3           # Windows: COM3, Linux: /dev/ttyUSB0
    baudrate: 115200
  ping:
    host: 192.168.1.100
```

### Claude Code 配置

在项目的 `.claude/settings.local.json` 中，已经配置了基本的权限。

如果需要添加更多权限，编辑此文件：
```json
{
  "permissions": {
    "allow": [
      "Bash(echo:*)",
      "WebSearch",
      "Skill(code-review:code-review)",
      "Skill(feature-dev:feature-dev)"
    ]
  }
}
```

---

## 使用方法

### 基础使用示例

#### 1. 时钟域问题分析

```
请帮我分析这个时钟问题：
系统在 100MHz 到 200MHz 时钟切换时出现数据错误，
错误日志显示时钟偏斜超过 200ps
```

Claude 会自动：
1. 调用 `hypothesis-manager` 启动分析流程
2. 使用 `clock-analysis` 技能分析时钟问题
3. 生成假设（如：时钟串扰、建立时间违例等）
4. 调用 `test-planner` 规划测试
5. 通过 MCP 工具执行测试
6. 迭代验证直到定位根因

#### 2. 挂死问题分析

```
我的单板运行一段时间后挂死了，
串口没有输出，Ping 也不同了，
请帮我分析可能的原因
```

Claude 会自动：
1. 使用 `hang-analysis` 技能
2. 通过 `board_control` 工具检测挂死状态
3. 保存检查点，重启单板
4. 分析挂死前的日志和状态
5. 生成诊断报告

#### 3. 电源问题分析

```
芯片在满载时电压降到 0.95V，
出现功能异常，请分析原因
```

#### 4. 通用故障诊断

```
请帮我诊断这个故障：
[粘贴完整的错误日志或问题描述]
```

### 高级使用

#### 指定使用特定技能

```
请使用 power-analysis 技能分析这个电源问题：
[问题描述]
```

#### 查看当前状态

```
请显示当前的故障分析状态和迭代历史
```

#### 继续之前的分析

```
请继续之前的故障分析，显示当前假设和待验证项
```

---

## MCP Server 配置

如果你想要在其他 MCP 客户端中使用这个系统的工具：

### 1. 启动 MCP Server

```bash
# Mock 模式（默认，不需要硬件）
python -m mcp_server.server

# 真实模式（需要硬件连接）
python -m mcp_server.server --real
```

### 2. 在 Claude Desktop 中配置

编辑 Claude Desktop 配置文件：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

添加以下配置：
```json
{
  "mcpServers": {
    "chip-fault-locator": {
      "command": "python",
      "args": [
        "-m", "mcp_server.server",
        "--mock"  // 或者 "--real" 使用真实硬件
      ],
      "cwd": "D:\\ai_dir\\sample_import"
    }
  }
}
```

### 3. 可用的 MCP 工具

配置成功后，以下工具将可用：

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `board_control` | 单板控制（重启、挂死检测等） | `action`, `restart_type`, `wait_for_boot` |
| `clock_test` | 时钟域测试 | `test_id`, `test_case` |
| `power_test` | 电源测试 | `test_id`, `test_case` |
| `temp_test` | 温度测试 | `test_id`, `test_case` |
| `general_test` | 通用测试 | `test_id`, `test_type`, `test_data` |

---

## 状态文件位置

系统会自动保存状态到：

```
~/.chip-fault-locator/
├── state.json              # 当前分析状态
├── checkpoints/            # 检查点（断点续传）
│   └── {session_id}.json
└── history/               # 历史记录
    └── {session_id}.json
```

**Windows**: `C:\Users\{用户名}\.chip-fault-locator\`
**Mac/Linux**: `~/.chip-fault-locator/`

---

## 使用技巧

### 1. 提供详细信息

为了获得更好的分析结果，提供尽可能多的信息：
- 完整的错误日志
- 问题发生时的操作步骤
- 硬件配置信息
- 测试环境描述
- 期望行为 vs 实际行为

### 2. 分阶段描述

对于复杂问题，可以分阶段描述：
```
第一阶段：问题描述
[描述问题现象]

第二阶段：环境信息
[硬件配置、软件版本等]

第三阶段：已尝试的方案
[已经做过的测试和排查]
```

### 3. 交互式分析

Claude 会通过假设迭代的方式进行分析，你可以：
- 确认或否定假设
- 提供额外的测试结果
- 要求更详细的解释
- 请求特定的测试

---

## 故障排查

### 问题 1: Skills 没有被识别

**症状**: Claude Code 无法使用分析技能

**解决**:
1. 确认在正确的项目目录中
2. 检查 `skills/` 目录是否存在
3. 检查每个技能目录下是否有 `SKILL.md` 文件
4. 重启 Claude Code

### 问题 2: 测试失败

**症状**: `pytest tests/` 失败

**解决**:
1. 确认已安装所有依赖：`pip install -r requirements.txt`
2. 检查 Python 版本 >= 3.8
3. 查看具体错误信息，可能需要安装额外依赖

### 问题 3: MCP Server 无法启动

**症状**: `python -m mcp_server.server` 报错

**解决**:
1. 检查是否安装了 mcp SDK (可选)：`pip install mcp`
2. 如果没有 SDK，服务器会以 standalone 模式运行
3. 查看日志输出了解具体错误

### 问题 4: 硬件连接失败

**症状**: 真实硬件测试时连接失败

**解决**:
1. 检查串口/SSH 配置是否正确
2. 确认硬件设备已连接
3. 检查网络连接（Ping）
4. 查看防火墙设置
5. 使用 Mock 模式测试：`python -m mcp_server.server --mock`

---

## 测试系统

### 快速验证

```bash
# 1. 运行所有测试
pytest tests/ -v

# 2. 测试特定模块
pytest tests/test_board_controller.py -v
pytest tests/test_mcp_server.py -v
pytest tests/test_state_manager.py -v

# 3. 查看测试覆盖
pytest tests/ --cov=. --cov-report=html
```

### 交互式测试

在 Claude Code 中测试：

```
# 测试 MCP 工具
请使用 board_control 工具检查单板状态

# 测试分析流程
请分析这个假设的故障：系统温度达到 95°C 时性能下降
```

---

## 下一步

1. **真实硬件测试**: 如果有真实硬件，配置单板参数进行测试
2. **自定义技能**: 根据你的具体需求修改或添加新技能
3. **扩展工具**: 在 `mcp_server/tools.py` 中添加新的测试工具
4. **集成 CI/CD**: 将测试集成到你的开发流程中

---

## 更多信息

- [架构文档](architecture.md)
- [实现计划 v6](plans/2026-03-03-implementation-v6.md)
- [项目 README](../README.md)
