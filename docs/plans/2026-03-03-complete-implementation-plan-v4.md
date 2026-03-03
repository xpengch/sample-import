# 芯片样片问题定位系统 - 完整实施计划 v4

## 架构概述

### 核心设计原则
- **hypothesis-manager 是 Skill (Markdown)**，不是 Python Subagent
- **Claude Code 是主控**，负责所有编排工作
- **所有"调用"都是引导/提示 Claude Code**，不是代码调用
- **所有 Skills 都是 Markdown**，Claude Code 读取并执行

### 系统组件

#### 1. Skills (Markdown)
所有技能定义在 `skills/` 目录下，每个技能一个 Markdown 文件：

```
skills/
├── clock-analysis/SKILL.md      # 时钟域分析
├── power-analysis/SKILL.md       # 电源分析
├── temp-analysis/SKILL.md        # 温度分析
├── general-diagnose/SKILL.md     # 通用诊断
├── test-planner/SKILL.md         # 测试规划
└── hypothesis-manager/SKILL.md   # 假设管理器 (元技能)
```

#### 2. MCP Tools (Python)
测试工具接口，当前使用 Mock，预留真实接口：

```
mcp_server/
├── server.py          # MCP 服务器主入口
├── tools.py           # 工具接口定义
└── mock_tools.py      # Mock 实现
```

#### 3. State Management (Python)
状态管理器，负责持久化和恢复：

```
core_utils/
└── state_manager.py   # 状态管理器

state/
└── state.json         # 状态文件 (用户目录: ~/.chip-fault-locator/)
```

#### 4. Configuration
```yaml
session:
  max_iterations: 10
  max_hypotheses: 5

hypotheses:
  min_confidence: 0.9
  reject_threshold: 0.05

testing:
  mock_mode: true

state:
  directory: ~/.chip-fault-locator
  auto_save: true
```

## 状态文件结构

```json
{
  "session_id": "20260303-143000",
  "log_file": "path/to/log.txt",
  "start_time": "2026-03-03T14:30:00",
  "status": "in_progress|completed|failed",
  "current_phase": "A|B|C|D|E|F|G",
  "iteration": 0,
  "max_iterations": 10,
  "hypotheses": [
    {
      "id": "H1",
      "content": "时钟域交叉问题",
      "confidence": 0.7,
      "status": "pending|testing|confirmed|rejected",
      "evidence": ["证据1", "证据2"],
      "test_history": []
    }
  ],
  "analysis_results": {},
  "test_results": [],
  "decision_log": [
    {
      "iteration": 0,
      "timestamp": "2026-03-03T14:30:00",
      "decision": "初始分析完成，生成3个假设"
    }
  ],
  "final_conclusion": null
}
```

## hypothesis-manager 工作流程

hypothesis-manager 是一个元技能，引导 Claude Code 完成整个迭代过程：

### 阶段 A: 初始分析
- 读取日志文件
- 调用分析技能生成初始假设
- 记录到 state.json

### 阶段 B: 假设评估
- 评估当前所有假设
- 选择置信度最高的进行测试

### 阶段 C: 测试规划
- 调用 test-planner 生成测试计划
- 执行测试 (通过 MCP Tools)

### 阶段 D: 结果分析
- 分析测试结果
- 更新假设置信度

### 阶段 E: 判断
- 检查是否已解决 (confidence >= 0.9)
- 检查是否需要继续迭代

### 阶段 F: 继续或结束
- 如果未解决且未达上限，回到阶段 B
- 如果已解决或达上限，进入阶段 G

### 阶段 G: 生成报告
- 生成最终结论
- 保存报告文件

## 实施状态

### 已完成 ✅
- [x] 架构设计 v4
- [x] 目录结构创建
- [x] state_manager.py 实现（含异常处理和 fsync）
- [x] state_manager.py 测试（7/7 通过）
- [x] config.yaml 配置
- [x] README.md 项目说明
- [x] requirements.txt 依赖
- [x] MCP Server 框架（tools.py, mock_tools.py, server.py）
- [x] MCP Server 测试（9/9 通过）
- [x] 所有 Skills (Markdown)
  - [x] clock-analysis/SKILL.md
  - [x] power-analysis/SKILL.md
  - [x] temp-analysis/SKILL.md
  - [x] general-diagnose/SKILL.md
  - [x] test-planner/SKILL.md
  - [x] hypothesis-manager/SKILL.md

### 待完成 📋

#### Phase 3: 集成与完善
- [ ] 端到端集成测试
- [ ] 用户使用文档
- [ ] 示例对话脚本

## 使用方式

在 Claude Code 对话中直接使用：

```
请帮我定位这个故障：[粘贴日志]
```

系统将：
1. 自动选择合适的分析 Skill
2. 生成故障假设
3. 规划并执行测试
4. 迭代验证直到定位成功
