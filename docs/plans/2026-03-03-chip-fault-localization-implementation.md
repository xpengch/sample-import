# 芯片样片问题定位系统 - 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 构建一个基于 Python 的芯片故障智能分析系统，支持日志解析、LLM 驱动分析、测试执行、人工干预和智能回溯。

**架构:** 基于 Skills 的模块化架构，每个技能独立实现并按需调用 LLM。工作流引擎协调技能执行，支持双重暂停机制和智能回溯。

**技术栈:** Python 3.10+, Claude API, subprocess, pytest, YAML

---

## 第一阶段：MVP

### Task 1: 项目初始化

**Files:**
- Create: `requirements.txt`
- Create: `config.yaml`
- Create: `README.md`
- Create: `.gitignore`
- Create: `tests/__init__.py`
- Create: `core/__init__.py`
- Create: `skills/__init__.py`
- Create: `cli/__init__.py`

**Step 1: 创建 requirements.txt**

```txt
anthropic>=0.18.0
pyyaml>=6.0
pytest>=7.4.0
pytest-cov>=4.1.0
```

**Step 2: 创建 config.yaml**

```yaml
llm:
  api_key: "${ANTHROPIC_AUTH_TOKEN}"
  base_url: "${ANTHROPIC_BASE_URL}"
  model: "claude-3-5-sonnet-20241022"

workflow:
  max_iterations: 10
  enable_rewind: true

skills:
  log_parser:
    enabled: true
  fault_detector:
    enabled: true
    use_llm: true
```

**Step 3: 创建 README.md**

```markdown
# 芯片样片问题定位系统

基于 Skills 架构的智能芯片故障分析系统。

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python -m cli.main analyze logs/sample.log
```
```

**Step 4: 创建 .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
.coverage
.venv/
*.log
config.local.yaml
```

**Step 5: 创建 __init__.py 文件**

```bash
mkdir -p core skills cli tests
touch core/__init__.py skills/__init__.py cli/__init__.py tests/__init__.py
```

**Step 6: 初始化 Git 仓库并提交**

```bash
git init
git add .
git commit -m "chore: initialize project structure"
```

---

### Task 2: Context 类实现

**Files:**
- Create: `core/context.py`
- Create: `tests/test_context.py`

**Step 1: 编写测试**

```python
# tests/test_context.py
import pytest
from core.context import Context, Decision

def test_context_initialization():
    ctx = Context(raw_log="test log")
    assert ctx.raw_log == "test log"
    assert ctx.parsed_data is None
    assert len(ctx.user_inputs) == 0

def test_add_user_input():
    ctx = Context(raw_log="test")
    ctx.add_user_input("芯片批次有已知问题")
    assert len(ctx.user_inputs) == 1
    assert "芯片批次" in ctx.user_inputs[0]

def test_add_decision():
    ctx = Context(raw_log="test")
    decision = Decision(
        step=1,
        decision="问题类型=时钟故障",
        assumption="时钟未更换"
    )
    ctx.add_decision(decision)
    assert len(ctx.decision_history) == 1
    assert ctx.decision_history[0].decision == "问题类型=时钟故障"

def test_no_conflict_by_default():
    ctx = Context(raw_log="test")
    conflict = ctx.check_conflict("新信息")
    assert conflict is None
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_context.py -v
```

**Expected:** FAIL - Module not found

**Step 3: 实现最小代码使测试通过**

```python
# core/context.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Decision:
    """决策记录"""
    step: int
    decision: str
    assumption: str
    timestamp: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())

@dataclass
class Conflict:
    """冲突信息"""
    conflicting_decision: Decision
    reason: str

class Context:
    """分析上下文"""

    def __init__(self, raw_log: str):
        self.raw_log = raw_log
        self.parsed_data = None
        self.detected_faults = []
        self.test_results = []
        self.user_inputs = []
        self.decision_history = []

    def add_user_input(self, info: str):
        """记录用户输入"""
        self.user_inputs.append(info)

    def add_decision(self, decision: Decision):
        """记录决策"""
        self.decision_history.append(decision)

    def check_conflict(self, new_info: str) -> Optional[Conflict]:
        """检查新信息是否与当前路径冲突"""
        # MVP 版本：暂不实现复杂冲突检测
        return None

    def has_conflict(self) -> bool:
        """是否存在冲突"""
        return False
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_context.py -v
```

**Expected:** PASS

**Step 5: 提交**

```bash
git add core/context.py tests/test_context.py
git commit -m "feat: implement Context class with decision history"
```

---

### Task 3: LLM Client 实现

**Files:**
- Create: `core/llm_client.py`
- Create: `tests/test_llm_client.py`

**Step 1: 编写测试**

```python
# tests/test_llm_client.py
import pytest
from unittest.mock import Mock, patch
from core.llm_client import LLMClient

def test_llm_client_initialization():
    client = LLMClient(
        api_key="test_key",
        base_url="https://api.test.com",
        model="claude-3-5-sonnet-20241022"
    )
    assert client.api_key == "test_key"
    assert client.model == "claude-3-5-sonnet-20241022"
    assert len(client.conversation_history) == 0

def test_add_context():
    client = LLMClient(api_key="test", base_url="https://test.com", model="test")
    client.add_context("芯片批次有已知问题")
    assert len(client.conversation_history) == 1
    assert "芯片批次" in client.conversation_history[0]["content"]

@patch('core.llm_client.anthropic.Anthropic')
def test_chat_call(mock_anthropic):
    mock_response = Mock()
    mock_response.content = [Mock(text="测试响应")]
    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    client = LLMClient(api_key="test", base_url="https://test.com", model="test")
    result = client.chat([{"role": "user", "content": "测试"}])

    assert result == "测试响应"
    mock_client.messages.create.assert_called_once()
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_llm_client.py -v
```

**Expected:** FAIL - Module not found

**Step 3: 实现最小代码**

```python
# core/llm_client.py
import os
from typing import Optional
import anthropic

class LLMClient:
    """Claude API 客户端"""

    def __init__(self, api_key: str, base_url: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.conversation_history = []
        self._client = anthropic.Anthropic(
            api_key=api_key,
            base_url=base_url
        )

    def chat(self, messages: list, system_prompt: Optional[str] = None) -> str:
        """调用 LLM"""
        # 构建完整消息列表（包含历史上下文）
        all_messages = self.conversation_history + messages

        kwargs = {
            "model": self.model,
            "messages": all_messages,
            "max_tokens": 4096
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)
        return response.content[0].text

    def add_context(self, info: str):
        """添加上下文供后续调用使用"""
        self.conversation_history.append({
            "role": "user",
            "content": f"[上下文信息] {info}"
        })

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
```

**Step 4: 更新 requirements.txt（如果需要）**

确保 `anthropic>=0.18.0` 在 requirements.txt 中

**Step 5: 运行测试验证通过**

```bash
pytest tests/test_llm_client.py -v
```

**Expected:** PASS

**Step 6: 提交**

```bash
git add core/llm_client.py tests/test_llm_client.py requirements.txt
git commit -m "feat: implement LLMClient with Claude API support"
```

---

### Task 4: Skill 基类与接口

**Files:**
- Create: `core/skill.py`
- Create: `tests/test_skill.py`

**Step 1: 编写测试**

```python
# tests/test_skill.py
import pytest
from abc import ABC
from core.skill import Skill, SkillResult

def test_skill_result_initialization():
    result = SkillResult(success=True, data={"faults": []})
    assert result.success is True
    assert result.uncertain is False
    assert result.data == {"faults": []}

def test_skill_result_uncertain():
    result = SkillResult(
        success=False,
        uncertain=True,
        uncertainty_reason="无法确定故障类型",
        options=["选项A", "选项B"]
    )
    assert result.uncertain is True
    assert result.uncertainty_reason == "无法确定故障类型"
    assert len(result.options) == 2

def test_skill_is_abstract():
    with pytest.raises(TypeError):
        Skill()  # 不能直接实例化抽象类
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_skill.py -v
```

**Expected:** FAIL

**Step 3: 实现最小代码**

```python
# core/skill.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from core.context import Context

@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    data: Any = None
    uncertain: bool = False
    uncertainty_reason: Optional[str] = None
    options: list[str] = field(default_factory=list)

class Skill(ABC):
    """技能基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称"""
        pass

    @property
    def use_llm(self) -> bool:
        """是否使用 LLM"""
        return False

    @abstractmethod
    def can_handle(self, context: Context) -> bool:
        """判断当前技能是否适用于该上下文"""
        pass

    @abstractmethod
    def execute(self, context: Context) -> SkillResult:
        """执行技能，返回结果"""
        pass
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_skill.py -v
```

**Expected:** PASS

**Step 5: 提交**

```bash
git add core/skill.py tests/test_skill.py
git commit -m "feat: implement Skill base class and SkillResult"
```

---

### Task 5: LogParserSkill 实现

**Files:**
- Create: `skills/log_parser/skill.py`
- Create: `skills/log_parser/__init__.py`
- Create: `tests/test_log_parser.py`

**Step 1: 创建示例日志**

```bash
mkdir -p logs
```

创建 `logs/sample.log`:
```
2026-03-03 10:00:00 [INFO] System initialized
2026-03-03 10:00:05 [ERROR] Clock signal abnormal: value=0x0000 expected=0xFFFF
2026-03-03 10:00:10 [WARN] Voltage fluctuation: 3.2V (range: 3.0-3.6V)
2026-03-03 10:00:15 [ERROR] Timeout waiting for response from peripheral
```

**Step 2: 编写测试**

```python
# tests/test_log_parser.py
import pytest
from skills.log_parser.skill import LogParserSkill
from core.context import Context

def test_log_parser_skill_name():
    skill = LogParserSkill()
    assert skill.name == "log_parser"
    assert skill.use_llm is False

def test_log_parser_can_handle():
    skill = LogParserSkill()
    ctx = Context(raw_log="some log")
    assert skill.can_handle(ctx) is True

def test_log_parser_execute():
    skill = LogParserSkill()
    ctx = Context(raw_log="2026-03-03 [ERROR] Clock signal abnormal")

    result = skill.execute(ctx)

    assert result.success is True
    assert ctx.parsed_data is not None
    assert "errors" in ctx.parsed_data
    assert len(ctx.parsed_data["errors"]) > 0
```

**Step 3: 运行测试验证失败**

```bash
pytest tests/test_log_parser.py -v
```

**Expected:** FAIL

**Step 4: 实现最小代码**

```python
# skills/log_parser/__init__.py
from skills.log_parser.skill import LogParserSkill

__all__ = ['LogParserSkill']
```

```python
# skills/log_parser/skill.py
import re
from datetime import datetime
from typing import Dict, List
from core.skill import Skill, SkillResult
from core.context import Context

class LogParserSkill(Skill):
    """日志解析技能 - 使用纯规则解析"""

    @property
    def name(self) -> str:
        return "log_parser"

    def can_handle(self, context: Context) -> bool:
        return context.raw_log is not None and len(context.raw_log) > 0

    def execute(self, context: Context) -> SkillResult:
        """解析日志文件"""
        parsed = {
            "errors": [],
            "warnings": [],
            "info": [],
            "timestamps": [],
            "raw_lines": []
        }

        # 基本解析模式
        error_pattern = r'\[ERROR\]\s*(.+)'
        warn_pattern = r'\[WARN\]\s*(.+)'
        info_pattern = r'\[INFO\]\s*(.+)'
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'

        for line in context.raw_log.split('\n'):
            line = line.strip()
            if not line:
                continue

            parsed["raw_lines"].append(line)

            # 提取时间戳
            ts_match = re.search(timestamp_pattern, line)
            if ts_match:
                parsed["timestamps"].append(ts_match.group(1))

            # 提取错误
            if '[ERROR]' in line:
                match = re.search(error_pattern, line)
                if match:
                    parsed["errors"].append({
                        "message": match.group(1),
                        "line": line
                    })

            # 提取警告
            elif '[WARN]' in line:
                match = re.search(warn_pattern, line)
                if match:
                    parsed["warnings"].append({
                        "message": match.group(1),
                        "line": line
                    })

            # 提取信息
            elif '[INFO]' in line:
                match = re.search(info_pattern, line)
                if match:
                    parsed["info"].append(match.group(1))

        context.parsed_data = parsed

        return SkillResult(
            success=True,
            data={
                "total_lines": len(parsed["raw_lines"]),
                "error_count": len(parsed["errors"]),
                "warning_count": len(parsed["warnings"]),
                "info_count": len(parsed["info"])
            }
        )
```

**Step 5: 运行测试验证通过**

```bash
pytest tests/test_log_parser.py -v
```

**Expected:** PASS

**Step 6: 提交**

```bash
git add skills/log_parser/ tests/test_log_parser.py logs/
git commit -m "feat: implement LogParserSkill with regex-based parsing"
```

---

### Task 6: FaultDetectorSkill 实现（LLM）

**Files:**
- Create: `skills/fault_detector/skill.py`
- Create: `skills/fault_detector/__init__.py`
- Create: `skills/fault_detector/prompts.py`
- Create: `tests/test_fault_detector.py`

**Step 1: 编写测试**

```python
# tests/test_fault_detector.py
import pytest
from unittest.mock import Mock, patch
from skills.fault_detector.skill import FaultDetectorSkill
from core.context import Context

@pytest.fixture
def mock_llm():
    mock = Mock()
    mock.chat.return_value = """{
  "faults": [
    {
      "type": "clock_signal",
      "severity": "high",
      "confidence": 0.85,
      "evidence": ["Clock signal abnormal at 10:00:05"]
    }
  ],
  "summary": "检测到时钟信号异常"
}"""
    return mock

def test_fault_detector_name():
    skill = FaultDetectorSkill(llm_client=Mock())
    assert skill.name == "fault_detector"
    assert skill.use_llm is True

def test_fault_detector_can_handle():
    skill = FaultDetectorSkill(llm_client=Mock())
    ctx = Context(raw_log="test")
    ctx.parsed_data = {"errors": [{"message": "Clock abnormal"}]}
    assert skill.can_handle(ctx) is True

def test_fault_detector_execute(mock_llm):
    skill = FaultDetectorSkill(llm_client=mock_llm)
    ctx = Context(raw_log="test")
    ctx.parsed_data = {"errors": [{"message": "Clock abnormal"}]}

    result = skill.execute(ctx)

    assert result.success is True
    assert len(ctx.detected_faults) > 0
    mock_llm.chat.assert_called_once()

def test_fault_detector_uncertain():
    mock_llm = Mock()
    mock_llm.chat.return_value = """{
  "uncertain": true,
  "reason": "多个故障信号概率接近",
  "faults": [
    {"type": "clock", "confidence": 0.48},
    {"type": "power", "confidence": 0.47}
  ],
  "options": ["优先检查时钟", "优先检查电源"]
}"""

    skill = FaultDetectorSkill(llm_client=mock_llm)
    ctx = Context(raw_log="test")
    ctx.parsed_data = {"errors": [{"message": "Multiple issues"}]}

    result = skill.execute(ctx)

    assert result.uncertain is True
    assert "概率接近" in result.uncertainty_reason
    assert len(result.options) > 0
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_fault_detector.py -v
```

**Expected:** FAIL

**Step 3: 实现最小代码**

```python
# skills/fault_detector/__init__.py
from skills.fault_detector.skill import FaultDetectorSkill

__all__ = ['FaultDetectorSkill']
```

```python
# skills/fault_detector/prompts.py
SYSTEM_PROMPT = """你是一个芯片故障诊断专家。分析日志数据，识别故障模式。

输出格式为 JSON，包含以下字段：
- faults: 故障列表，每个故障包含 type, severity, confidence, evidence
- summary: 分析摘要
- uncertain: 是否存在不确定性（可选）
- reason: 不确定原因（当 uncertain=true 时）
- options: 建议的选项列表（当 uncertain=true 时）
"""

USER_PROMPT_TEMPLATE = """请分析以下日志数据，识别潜在的芯片故障：

错误信息：
{errors}

警告信息：
{warnings}

请以 JSON 格式返回分析结果。
"""
```

```python
# skills/fault_detector/skill.py
import json
from typing import Dict, Any
from core.skill import Skill, SkillResult
from core.context import Context
from core.llm_client import LLMClient
from skills.fault_detector.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

class FaultDetectorSkill(Skill):
    """故障检测技能 - 使用 LLM 分析"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.system_prompt = SYSTEM_PROMPT

    @property
    def name(self) -> str:
        return "fault_detector"

    @property
    def use_llm(self) -> bool:
        return True

    def can_handle(self, context: Context) -> bool:
        return context.parsed_data is not None and \
               len(context.parsed_data.get("errors", [])) > 0

    def execute(self, context: Context) -> SkillResult:
        """执行故障检测"""
        # 准备输入
        errors = context.parsed_data.get("errors", [])
        warnings = context.parsed_data.get("warnings", [])

        # 构建 prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            errors=json.dumps(errors, ensure_ascii=False, indent=2),
            warnings=json.dumps(warnings, ensure_ascii=False, indent=2)
        )

        # 调用 LLM
        messages = [{"role": "user", "content": user_prompt}]

        # 添加用户输入作为上下文
        for user_input in context.user_inputs:
            self.llm.add_context(user_input)

        response = self.llm.chat(messages, system_prompt=self.system_prompt)

        # 解析响应
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取 JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                result = json.loads(response[start:end])
            else:
                return SkillResult(
                    success=False,
                    uncertain=True,
                    uncertainty_reason="LLM 返回格式错误",
                    options=["重试", "手动分析"]
                )

        # 处理不确定情况
        if result.get("uncertain", False):
            context.detected_faults = result.get("faults", [])
            return SkillResult(
                success=False,
                uncertain=True,
                uncertainty_reason=result.get("reason", "无法确定"),
                options=result.get("options", [])
            )

        # 正常情况
        context.detected_faults = result.get("faults", [])

        return SkillResult(
            success=True,
            data={
                "faults": context.detected_faults,
                "summary": result.get("summary", "")
            }
        )
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_fault_detector.py -v
```

**Expected:** PASS

**Step 5: 提交**

```bash
git add skills/fault_detector/ tests/test_fault_detector.py
git commit -m "feat: implement FaultDetectorSkill with LLM analysis"
```

---

### Task 7: Workflow Engine 基础实现

**Files:**
- Create: `core/workflow.py`
- Create: `tests/test_workflow.py`

**Step 1: 编写测试**

```python
# tests/test_workflow.py
import pytest
from unittest.mock import Mock, patch
from core.workflow import WorkflowEngine
from core.context import Context
from core.llm_client import LLMClient

@pytest.fixture
def mock_skills():
    return [Mock(), Mock()]

@pytest.fixture
def mock_llm():
    return Mock(spec=LLMClient)

def test_workflow_initialization(mock_llm, mock_skills):
    engine = WorkflowEngine(llm_client=mock_llm, skills=mock_skills)
    assert engine.llm == mock_llm
    assert len(engine.skills) == 2

def test_workflow_select_next_skill(mock_llm, mock_skills):
    mock_skills[0].can_handle.return_value = False
    mock_skills[1].can_handle.return_value = True

    engine = WorkflowEngine(llm_client=mock_llm, skills=mock_skills)
    ctx = Context(raw_log="test")

    skill = engine.select_next_skill(ctx)
    assert skill == mock_skills[1]

@patch('core.workflow.WorkflowEngine.run')
def test_workflow_run(mock_run, mock_llm, mock_skills):
    """测试工作流可以被调用"""
    engine = WorkflowEngine(llm_client=mock_llm, skills=mock_skills)
    engine.run("test.log")
    mock_run.assert_called_once_with("test.log")
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_workflow.py -v
```

**Expected:** FAIL

**Step 3: 实现最小代码**

```python
# core/workflow.py
from typing import List, Optional
from core.context import Context
from core.llm_client import LLMClient
from core.skill import Skill

class WorkflowEngine:
    """工作流引擎"""

    def __init__(self, llm_client: LLMClient, skills: List[Skill]):
        self.llm = llm_client
        self.skills = skills
        self.user_pause_requested = False

    def select_next_skill(self, context: Context) -> Optional[Skill]:
        """选择下一个可执行的技能"""
        for skill in self.skills:
            if skill.can_handle(context):
                return skill
        return None

    def run(self, log_file: str):
        """执行工作流"""
        # 读取日志文件
        with open(log_file, 'r', encoding='utf-8') as f:
            raw_log = f.read()

        # 初始化上下文
        context = Context(raw_log=raw_log)

        # 主循环
        iteration = 0
        max_iterations = 10

        while iteration < max_iterations:
            iteration += 1

            # 选择技能
            skill = self.select_next_skill(context)
            if not skill:
                print(f"[系统] 没有可执行的技能，分析结束")
                break

            print(f"[系统] 执行技能: {skill.name}")

            # 执行技能
            result = skill.execute(context)

            if result.uncertain:
                print(f"[系统] 需要人工判断: {result.uncertainty_reason}")
                # MVP 版本：暂时打印选项
                for i, opt in enumerate(result.options, 1):
                    print(f"  {i}. {opt}")
                break

            if not result.success:
                print(f"[系统] 技能执行失败")
                break

            print(f"[系统] 技能执行成功")

            # 简单完成条件
            if skill.name == "fault_detector" and result.success:
                print(f"[系统] 故障检测完成")
                break

        print(f"[系统] 工作流结束，迭代次数: {iteration}")
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_workflow.py -v
```

**Expected:** PASS

**Step 5: 提交**

```bash
git add core/workflow.py tests/test_workflow.py
git commit -m "feat: implement basic WorkflowEngine"
```

---

### Task 8: CLI 主入口

**Files:**
- Create: `cli/main.py`
- Create: `tests/test_main.py`

**Step 1: 编写测试**

```python
# tests/test_main.py
import pytest
from unittest.mock import patch, Mock
from cli.main import main

@patch('cli.main.WorkflowEngine')
@patch('cli.main.load_skills')
@patch('cli.main.load_config')
@patch('sys.argv', ['main.py', 'analyze', 'test.log'])
def test_main_analyze_command(mock_config, mock_skills, mock_engine):
    mock_config.return_value = {"llm": {"model": "test"}}
    mock_skills.return_value = [Mock()]
    mock_engine_instance = Mock()
    mock_engine.return_value = mock_engine_instance

    main()

    mock_engine_instance.run.assert_called_once_with('test.log')
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_main.py -v
```

**Expected:** FAIL

**Step 3: 实现最小代码**

```python
# cli/main.py
import sys
import yaml
import os
from pathlib import Path
from core.workflow import WorkflowEngine
from core.llm_client import LLMClient

def load_config(config_path: str = "config.yaml") -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 环境变量替换
    if "llm" in config:
        for key in ["api_key", "base_url"]:
            if key in config["llm"]:
                value = config["llm"][key]
                if isinstance(value, str) and value.startswith("${"):
                    env_var = value[2:-1]
                    config["llm"][key] = os.environ.get(env_var, value)

    return config

def load_skills(config: dict, llm_client: LLMClient) -> list:
    """加载技能"""
    skills = []

    if config.get("skills", {}).get("log_parser", {}).get("enabled", True):
        from skills.log_parser import LogParserSkill
        skills.append(LogParserSkill())

    if config.get("skills", {}).get("fault_detector", {}).get("enabled", True):
        from skills.fault_detector import FaultDetectorSkill
        skills.append(FaultDetectorSkill(llm_client=llm_client))

    return skills

def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: python -m cli.main analyze <log_file>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: python -m cli.main analyze <log_file>")
            sys.exit(1)

        log_file = sys.argv[2]

        # 检查文件存在
        if not Path(log_file).exists():
            print(f"错误: 日志文件不存在: {log_file}")
            sys.exit(1)

        # 加载配置
        config = load_config()

        # 初始化 LLM 客户端
        llm_config = config.get("llm", {})
        llm_client = LLMClient(
            api_key=llm_config.get("api_key", ""),
            base_url=llm_config.get("base_url", ""),
            model=llm_config.get("model", "claude-3-5-sonnet-20241022")
        )

        # 加载技能
        skills = load_skills(config, llm_client)

        # 运行工作流
        engine = WorkflowEngine(llm_client=llm_client, skills=skills)
        engine.run(log_file)

    else:
        print(f"未知命令: {command}")
        print("可用命令: analyze")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_main.py -v
```

**Expected:** PASS

**Step 5: 手动测试**

```bash
python -m cli.main analyze logs/sample.log
```

**Expected:**
```
[系统] 执行技能: log_parser
[系统] 技能执行成功
[系统] 执行技能: fault_detector
[系统] 技能执行成功
[系统] 故障检测完成
[系统] 工作流结束
```

**Step 6: 提交**

```bash
git add cli/ tests/test_main.py
git commit -m "feat: implement CLI main entry point"
```

---

### Task 9: 集成测试

**Files:**
- Create: `tests/integration/test_full_workflow.py`

**Step 1: 编写集成测试**

```python
# tests/integration/test_full_workflow.py
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_full_workflow_with_sample_log():
    """测试完整工作流"""
    from cli.main import load_config, load_skills
    from core.workflow import WorkflowEngine
    from core.llm_client import LLMClient

    # 加载配置
    config = load_config()

    # 初始化 LLM 客户端（使用 mock）
    llm_client = LLMClient(
        api_key=os.environ.get("ANTHROPIC_AUTH_TOKEN", "test"),
        base_url=os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        model=config["llm"]["model"]
    )

    # 加载技能
    skills = load_skills(config, llm_client)

    # 创建工作流引擎
    engine = WorkflowEngine(llm_client=llm_client, skills=skills)

    # 执行
    log_file = "logs/sample.log"
    if Path(log_file).exists():
        engine.run(log_file)
    else:
        pytest.skip(f"Sample log file not found: {log_file}")
```

**Step 2: 运行集成测试**

```bash
pytest tests/integration/test_full_workflow.py -v -s
```

**Step 3: 提交**

```bash
git add tests/integration/
git commit -m "test: add integration test for full workflow"
```

---

## 第一阶段总结

完成以上 9 个任务后，第一阶段 MVP 完成，包含：

- ✅ 项目结构和配置
- ✅ Context 类（上下文管理）
- ✅ LLM Client（Claude API）
- ✅ Skill 基类（技能接口）
- ✅ LogParserSkill（日志解析）
- ✅ FaultDetectorSkill（故障检测，LLM）
- ✅ WorkflowEngine（工作流引擎）
- ✅ CLI 主入口
- ✅ 集成测试

---

## 第二阶段预告

第二阶段将实现：
- TestPlannerSkill（测试规划，LLM）
- TestExecutorSkill（测试执行，外部工具）
- ResultAnalyzerSkill（结果分析，LLM）
- 双重暂停机制
- 决策历史记录

---

## 记住

- **DRY** - 不要重复代码
- **YAGNI** - 只实现当前需要的功能
- **TDD** - 先写测试，再写实现
- **频繁提交** - 每个任务完成后提交
- **精确文件路径** - 所有路径都是相对于项目根目录
