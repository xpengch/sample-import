# Hypothesis Manager Skill (Meta-Skill)

## 描述

**这是元技能**，用于引导 Claude Code 完成完整的假设迭代分析流程。

它不直接分析日志，而是：
1. 指导 Claude Code 选择合适的分析 Skill
2. 协调假设生成、测试、更新的迭代过程
3. 管理状态文件（state.json）
4. 控制流程推进和结束条件

## 使用场景

当用户说：
- "帮我定位这个故障：[日志]"
- "分析这个芯片问题"
- "继续分析"

## 工作流程

### 阶段 A：初始分析

**目标**：从日志中生成初始假设

**步骤**：
1. 使用 state_manager 创建新状态：
   ```python
   sm = StateManager()
   state = sm.create(log_file_path)
   ```

2. 调用分析 Skills：
   - 让 Claude Code 分析日志
   - 使用 `clock-analysis`、`power-analysis`、`temp-analysis`、`general-diagnose`
   - 每个分析生成 1-3 个假设

3. 添加假设到状态：
   ```python
   for hypothesis in hypotheses:
       sm.add_hypothesis(hypothesis)
   ```

4. 进入阶段 B

### 阶段 B：假设评估

**目标**：选择最有希望的假设进行测试

**步骤**：
1. 获取活跃假设：
   ```python
   active_hypotheses = sm.get_active_hypotheses()
   ```

2. 选择测试目标：
   - 优先选择高置信度的假设
   - 或选择容易验证的假设
   - 记录选择理由

3. 进入阶段 C

### 阶段 C：测试规划

**目标**：为选中的假设设计测试

**步骤**：
1. 使用 `test-planner` Skill 生成测试计划

2. 确定测试工具和参数

3. 进入阶段 D

### 阶段 D：测试执行

**目标**：执行测试并收集结果

**步骤**：
1. 使用 MCP Server 执行测试：
   ```python
   from mcp_server.server import get_server
   server = get_server()
   result = server.execute_tool_sync(tool_name, params)
   ```

2. 记录测试结果：
   ```python
   sm.add_test_result(result)
   ```

3. 进入阶段 E

### 阶段 E：结果分析

**目标**：根据测试结果更新假设置信度

**步骤**：
1. 分析测试结果：
   - 如果测试失败 → 支持假设，提高置信度
   - 如果测试通过 → 不支持假设，降低置信度

2. 更新假设：
   ```python
   if test_failed:
       sm.update_hypothesis(h_id, {
           "confidence": min(0.95, confidence + 0.2),
           "status": "confirmed" if confidence >= 0.9 else "testing"
       })
   else:
       sm.update_hypothesis(h_id, {
           "confidence": max(0.0, confidence - 0.3),
           "status": "rejected" if confidence < 0.1 else "testing"
       })
   ```

3. 记录决策：
   ```python
   sm.log_decision(f"测试 {test_id} {result}，更新 {h_id} 置信度到 {new_conf}")
   ```

4. 进入阶段 F

### 阶段 F：继续判断

**目标**：决定是否继续迭代

**步骤**：
1. 检查解决状态：
   ```python
   if sm.is_solved():
       进入阶段 G  # 已解决
   ```

2. 检查迭代上限：
   ```python
   if state["iteration"] >= state["max_iterations"]:
       进入阶段 G  # 达到上限
   ```

3. 增加迭代计数：
   ```python
   sm.increment_iteration()
   ```

4. 返回阶段 B

### 阶段 G：生成报告

**目标**：生成最终分析报告

**步骤**：
1. 获取最终状态：
   ```python
   state = sm.get()
   confirmed = sm.get_confirmed_hypothesis()
   ```

2. 生成报告内容：
   - 故障根因（最高置信度假设）
   - 分析过程摘要
   - 测试结果汇总
   - 建议的修复措施

3. 设置状态为完成：
   ```python
   sm.set_status("completed")
   ```

4. 输出报告给用户

## 状态文件结构

state.json 存储在：`~/.chip-fault-locator/state.json`

```json
{
  "session_id": "20260303-143000",
  "log_file": "path/to/log.txt",
  "status": "in_progress",
  "current_phase": "B",
  "iteration": 2,
  "hypotheses": [
    {
      "id": "H1",
      "category": "clock",
      "content": "CDC 同步问题",
      "confidence": 0.85,
      "status": "testing",
      "evidence": [...],
      "test_history": [...]
    }
  ],
  "test_results": [...],
  "decision_log": [...]
}
```

## 关键决策点

1. **假设生成控制**：
   - 最多 5 个并发假设
   - 置信度 < 0.1 标记为 rejected
   - 置信度 >= 0.9 标记为 confirmed

2. **迭代终止条件**：
   - 有假设置信度 >= 0.9 → 已解决
   - 迭代次数 >= max_iterations → 达上限
   - 所有假设都被拒绝 → 无结论

3. **测试优先级**：
   - 优先测试高置信度假设
   - 优先测试容易验证的假设
   - 优先测试可隔离的假设

## 与 Claude Code 的交互

**不要**：
- ❌ 尝试直接"调用"其他 Skill
- ❌ 编写代码来实现 Skill 逻辑

**要**：
- ✅ 引导 Claude Code 使用某个 Skill
- ✅ 描述需要做什么，让 Claude Code 执行
- ✅ 使用 state_manager 管理状态
- ✅ 使用 MCP Server 执行测试

## 示例对话

**用户**：帮我定位这个故障：[日志内容]

**Claude Code（使用 hypothesis-manager）**：
1. 我会帮你分析这个故障。首先创建分析会话...
2. 让我分析日志中的时钟相关问题...
3. 让我分析日志中的电源相关问题...
4. 生成了 3 个初始假设，让我开始测试...
5. 使用 test-planner 为假设 H1 设计测试...
6. 执行测试...
7. 测试失败，支持假设 H1，更新置信度...
8. 继续下一个假设...
9. 已找到根因：CDC 同步问题（置信度 0.92）
10. 生成最终报告...
