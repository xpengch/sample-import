# 芯片样片问题定位系统 - ��计文档

**日期:** 2026-03-03
**版本:** 1.0

---

## 1. 系统概述

### 1.1 目标
构建一个基于纯 Python 的智能分析系统，通过输入日志、分析、执行测试、反复迭代的方式，最终给出芯片故障定位结果。

### 1.2 核心理念
- **基于 Skills 的模块化架构** - 每个功能作为独立技能实现
- **Skill 内部调用 LLM** - 需要智能分析的技能调用 Claude API
- **双重暂停机制** - 用户主动暂停 + 系统自动暂停
- **智能回溯** - 检测冲突后支持路径回溯和重规划

---

## 2. 系统架构

### 2.1 目录结构

```
sample_import/
├── skills/                    # 技能定义目录
│   ├── log_parser/           # 日志解析（纯规则）
│   ├── fault_detector/       # 故障检测（LLM）
│   ├── test_planner/         # 测试规划（LLM）
│   ├── test_executor/        # 测试执行（外部工具）
│   ├── result_analyzer/      # 结果分析（LLM）
│   └── report_generator/     # 报告生成（LLM+模板）
│
├── core/                      # 核心引擎
│   ├── llm_client.py         # LLM 客户端
│   ├── skill_manager.py      # 技能加载与调用
│   ├── workflow.py           # 工作流编排
│   ├── context.py            # 上下文与决策历史
│   ├── conflict_detector.py  # 冲突检测
│   └── replanner.py          # 路径重规划
│
├── cli/                       # 命令行接口
│   ├── main.py               # 主入口
│   └── interactive.py        # 交互模式
│
├── tests/                     # 测试
├── docs/                      # 文档
│   └── plans/                # 设计文档
├── logs/                      # 示例日志
├── config.yaml                # 配置文件
└── requirements.txt           # 依赖
```

### 2.2 工作流程

```
用户输入日志
    ↓
[skill_manager] 加载相关 skills
    ↓
[workflow] 执行技能链:
    log-parser → fault-detector → test-planner
         ↓
    test-executor → result-analyzer
         ↓ (未定位)
    循环: test-planner → test-executor → result-analyzer
         ↓ (已定位)
    report-generator → 输出结果
```

---

## 3. 核心组件设计

### 3.1 Skill 接口

```python
class Skill(ABC):
    """技能基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称"""

    @property
    def use_llm(self) -> bool:
        """是否使用 LLM"""
        return False

    @abstractmethod
    def can_handle(self, context: Context) -> bool:
        """判断当前技能是否适用于该上下文"""

    @abstractmethod
    def execute(self, context: Context) -> SkillResult:
        """执行技能，返回结果"""
```

### 3.2 SkillResult

```python
@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    data: Any = None
    uncertain: bool = False
    uncertainty_reason: str = None
    options: list[str] = None
```

### 3.3 LLM Client

```python
class LLMClient:
    """Claude API 客户端"""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.conversation_history: list[dict] = []

    def chat(self, messages: list, system_prompt: str = None) -> str:
        """调用 LLM"""

    def add_context(self, info: str):
        """添加上下文供后续调用使用"""
        self.conversation_history.append({
            "role": "user",
            "content": f"[上下文信息] {info}"
        })
```

### 3.4 Context

```python
class Context:
    """分析上下文"""

    raw_log: str
    parsed_data: dict
    detected_faults: list
    test_results: list
    user_inputs: list           # 用户注入的信息
    decision_history: list      # 决策历史（用于回溯）

    def add_user_input(self, info: str):
        """记录用户输入"""

    def check_conflict(self, new_info: str) -> Optional[Conflict]:
        """检查新信息是否与当前路径冲突"""
```

### 3.5 Workflow Engine

```python
class WorkflowEngine:
    """工作流引擎"""

    def __init__(self, llm_client: LLMClient, skills: list[Skill]):
        self.llm = llm_client
        self.skills = skills
        self.user_pause_requested = False

    def run(self, log_file: str):
        """主执行流程"""
        while not done:
            # 1. 选择下一个技能
            skill = self.select_next_skill(context)

            # 2. 执行技能
            result = skill.execute(context)

            # 3. 检查用户暂停 (Ctrl+C)
            if self.user_pause_requested:
                self.pause_mode(reason="user_request")

            # 4. 检查系统自动暂停 (无法判断)
            if result.uncertain:
                self.pause_mode(reason="uncertain", result=result)

            # 5. 检查冲突与回溯
            if context.has_conflict():
                self.handle_conflict()

    def pause_mode(self, reason: str, result: SkillResult = None):
        """暂停模式，等待用户输入"""
```

---

## 4. Skills 设计

### 4.1 Skills 与 LLM 映射

| Skill | 调用 LLM | 说明 |
|-------|---------|------|
| `log_parser` | ❌ | 正则/规则解析日志文件 |
| `fault_detector` | ✅ | 理解日志语义，识别异常模式 |
| `test_planner` | ✅ | 根据分析结果智能规划测试 |
| `test_executor` | ❌ | 调用外部工具执行测试 |
| `result_analyzer` | ✅ | 判断测试结果是否充分 |
| `report_generator` | ✅ | 生成可读性强的报告 |

### 4.2 LogParserSkill

**职责:** 解析日志文件，提取关键信息

**输入:** 原始日志文件路径
**输出:** 解析后的结构化数据

**实现:** 纯规则，使用正则表达式

---

### 4.3 FaultDetectorSkill

**职责:** 识别日志中的异常模式

**输入:** 解析后的日志数据
**输出:** 检测到的故障列表

**实现:** 调用 LLM 进行语义分析

---

### 4.4 TestPlannerSkill

**职责:** 根据分析结果生成测试计划

**输入:** 检测到的故障
**输出:** 测试计划（步骤、参数）

**实现:** 调用 LLM 生成测试方案

---

### 4.5 TestExecutorSkill

**职责:** 执行测试

**输入:** 测试计划
**输出:** 测试结果

**实现:** 通过 subprocess 调用外部工具

---

### 4.6 ResultAnalyzerSkill

**职责:** 分析测试结果，判断是否需要继续

**输入:** 测试结果
**输出:** 分析结论（是否定位成功/需要继续测试）

**实现:** 调用 LLM 分析结果

---

### 4.7 ReportGeneratorSkill

**职责:** 生成最终定位报告

**输入:** 所有分析数据
**输出:** Markdown 格式报告

**实现:** LLM + 模板

---

## 5. 交互设计

### 5.1 双重暂停机制

| 触发方式 | 场景 | 行为 |
|---------|------|------|
| **用户主动** | 随时按 `Ctrl+C` | 立即暂停，等待用户输入 |
| **系统主动** | 遇到无法判断的问题 | 自动暂停，请求用户指示 |

### 5.2 暂停时可用命令

```bash
# 查看类
status           - 查看当前状态
context          - 查看所有上下文
history          - 查看决策历史

# 输入类
add-info <信息>  - 添加背景信息
choose <选项>    - 选择一个选项（自动暂停时）

# 控制类
continue / c     - 继续分析
skip             - 跳过当前步骤
rewind <步骤>    - 回溯到指定步骤
quit / q         - 退出分析
```

### 5.3 交互示例

```bash
$ python main.py analyze chip.log

[系统] 开始分析...
[系统] 步骤1: 解析日志 ✓
[系统] 步骤2: 故障检测...

[系统] === 需要人工判断 ===
问题: 检测到多个故障信号，概率接近
当前分析:
  - 时钟信号异常: 48%
  - 电源模块波动: 47%

可选方向:
  1. 优先检查时钟
  2. 优先检查电源
  3. 并行检查两者

请选择或输入指令:
> 2
[系统] 已记录: 优先检查电源
[系统] 继续分析...
```

---

## 6. 回溯机制

### 6.1 冲突检测

当用户注入新信息时，系统检查：
1. 新信息是否与之前的决策假设冲突
2. 当前分析路径是否仍然有效

### 6.2 回溯流程

```
检测冲突
    ↓
提示用户
    ↓
用户选择:
    - 回溯到冲突点前重新规划
    - 忽略冲突，继续当前路径
    - 手动选择回溯点
    ↓
重新规划路径
    ↓
继续执行
```

### 6.3 决策历史

```python
decision_history = [
    {
        "step": 2,
        "timestamp": "...",
        "decision": "问题类型 = 时钟模块故障",
        "assumption": "时钟模块未更换",
        "context": {...}
    },
    ...
]
```

---

## 7. 技术栈

| 组件 | 选择 |
|------|------|
| 语言 | Python 3.10+ |
| LLM | Claude API |
| 外部工具调用 | subprocess |
| 配置 | YAML |
| 测试 | pytest |
| 报告格式 | Markdown |

---

## 8. 实现阶段

### 第一阶段（MVP）
- [ ] Context 类
- [ ] Skill 基类与接口
- [ ] LLMClient 基础实现
- [ ] LogParserSkill（纯规则）
- [ ] FaultDetectorSkill（LLM）
- [ ] 基础工作流
- [ ] 简单 CLI

### 第二阶段
- [ ] TestPlannerSkill（LLM）
- [ ] TestExecutorSkill（外部工具）
- [ ] ResultAnalyzerSkill（LLM）
- [ ] 双重暂停机制
- [ ] 决策历史记录

### 第三阶段
- [ ] 冲突检测
- [ ] 智能回溯
- [ ] 路径重规划
- [ ] ReportGeneratorSkill（LLM）

---

## 9. 关键设计决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 架构模式 | Skills 模块化 | 易于扩展和测试 |
| LLM 交互 | Skill 内部调用 | 成本可控，逻辑清晰 |
| 人工干预 | 双重暂停 | 平衡自动化与控制 |
| 回溯机制 | 智能回溯 | 支持动态调整分析方向 |
| 技术栈 | 纯 Python | 简单、易维护 |

---

**文档状态:** 待批准
