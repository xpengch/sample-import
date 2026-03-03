# 芯片样片问题定位系统 - 实施计划 v5

## 架构概述

### 核心设计原则
- **hypothesis-manager 是 Skill (Markdown)**，不是 Python Subagent
- **Claude Code 是主控**，负责所有编排工作
- **所有"调用"都是引导/提示 Claude Code**，不是代码调用
- **所有 Skills 都是 Markdown**，Claude Code 读取并执行

### 系统组件

#### 1. Skills (Markdown)
所有技能定义在 `skills/` 目录下，每个技能一个 Markdown 文件：

**专业领域分析 (4个)**
```
skills/
├── clock-analysis/SKILL.md      # 时钟域分析
├── power-analysis/SKILL.md       # 电源分析
├── temp-analysis/SKILL.md        # 温度分析
└── general-diagnose/SKILL.md     # 通用诊断
```

**专项问题分析 (5个)**
```
skills/
├── hbm-analysis/SKILL.md         # HBM 问题分析
├── hang-analysis/SKILL.md        # 挂死问题分析
├── silent-analysis/SKILL.md      # 静默失败分析
├── sioh-analysis/SKILL.md        # SIOH 问题分析
└── core-failure-analysis/SKILL.md # 核失效问题分析
```

**流程控制 (2个)**
```
skills/
├── test-planner/SKILL.md         # 测试规划
└── hypothesis-manager/SKILL.md   # 假设管理器 (元技能)
```

#### 2. MCP Tools (Python)
测试工具接口，当前使用 Mock，预留真实接口：

```
mcp_server/
├── server.py          # MCP 服务器主入口
├── tools.py           # 工具接口定义
└── mock_tools.py      # Mock 实现 (4种工具)
```

支持的测试工具：
- `clock_test`: crosstalk, setup_violation, hold_violation, default
- `power_test`: undervoltage, overcurrent, default
- `temperature_test`: overheat, thermal_cycling, default
- `general_test`: 任意 test_case

#### 3. State Management (Python)
状态管理器，负责持久化和恢复：

```
core_utils/
└── state_manager.py   # 状态管理器 (含 fsync、异常处理)

state/
└── state.json         # 状态文件 (用户目录: ~/.chip-fault-locator/)
```

## 实施状态 v5

### 已完成 ✅
- [x] 架构设计 v4
- [x] 目录结构创建
- [x] state_manager.py 实现（含异常处理和 fsync）
- [x] state_manager.py 测试（7/7 通过）
- [x] MCP Server 框架（tools.py, mock_tools.py, server.py）
- [x] MCP Server 测试（10/10 通过）
- [x] 基础 Skills (Markdown) - 6个
- [x] 专项 Skills (Markdown) - 5个框架
- [x] Skills 文档与实现对齐
- [x] 配置文件 (config.yaml)
- [x] 项目文档 (README.md)

### 测试覆盖

| 模块 | 测试数 | 状态 |
|------|--------|------|
| state_manager | 7 | ✅ |
| mcp_server | 10 | ✅ |
| **总计** | **17** | ✅ |

### 目录结构

```
sample_import/
├── core_utils/
│   └── state_manager.py
├── mcp_server/
│   ├── __init__.py
│   ├── server.py
│   ├── tools.py
│   └── mock_tools.py
├── skills/
│   ├── clock-analysis/SKILL.md
│   ├── power-analysis/SKILL.md
│   ├── temp-analysis/SKILL.md
│   ├── general-diagnose/SKILL.md
│   ├── test-planner/SKILL.md
│   ├── hypothesis-manager/SKILL.md
│   ├── hbm-analysis/SKILL.md
│   ├── hang-analysis/SKILL.md
│   ├── silent-analysis/SKILL.md
│   ├── sioh-analysis/SKILL.md
│   └── core-failure-analysis/SKILL.md
├── tests/
│   ├── test_state_manager.py
│   └── test_mcp_server.py
├── docs/
│   └── plans/
│       └── 2026-03-03-complete-implementation-plan-v5.md
├── logs/README.md
├── state/README.md
├── config.yaml
├── requirements.txt
└── README.md
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v5 | 2026-03-03 | 添加5个专项分析 Skill 框架，修复 Skills 文档对齐 |
| v4 | 2026-03-03 | 完整 Skills 架构实现 |
| v3 | 2026-03-03 | MCP Server 框架 |
| v2 | 2026-03-03 | State Manager 实现 |
| v1 | 2026-03-03 | 初始架构设计 |

## 下一版开发建议

1. **完善专项 Skills**：补充5个新 Skill 的具体测试用例和参数
2. **真实 MCP Tools**：实现真实硬件测试工具接口
3. **端到端测试**：创建完整场景的集成测试
4. **用户文档**：编写使用手册和示例对话
