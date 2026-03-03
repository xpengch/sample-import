# Test Planner Skill

## 描述

根据假设生成具体的测试计划，指导 Claude Code 使用 MCP 工具执行测试并收集结果。

## 触发条件

- 需要验证某个假设
- 需要设计测试用例
- 需要选择合适的测试工具

## 测试规划流程

1. **分析假设**
   - 读取假设的 category、content、evidence
   - 理解假设的核心问题
   - 识别关键验证点

2. **选择测试工具**
   - 根据假设类别选择工具：
     - `clock` → `clock_test`
     - `power` → `power_test`
     - `temperature` → `temperature_test`
     - `general` → `general_test`

3. **设计测试用例**
   - 基于假设内容设计 test_case
   - 确定预期结果（pass/fail）
   - 定义必要的测试参数

4. **生成测试计划**

   测试计划格式：
   ```json
   {
     "plan_id": "TP001",
     "hypothesis_id": "H1",
     "tests": [
       {
         "test_id": "T001",
         "tool": "clock_test",
         "params": {
           "test_case": "cdc_violation",
           "clock_domain_a": "clk_sys",
           "clock_domain_b": "clk_per"
         },
         "expected_outcome": "fail",
         "rationale": "如果 CDC 问题存在，此测试应失败"
       }
     ],
     "execution_order": ["T001"],
     "success_criteria": "至少一个测试按预期失败"
   }
   ```

## 测试用例设计指南

### 时钟域测试

| 假设内容 | test_case | 关键参数 |
|---------|-----------|----------|
| 时钟串扰 | `crosstalk` | affected_signals |
| 建立时间违例 | `setup_violation` | path_delay |
| 保持时间违例 | `hold_violation` | path_delay |
| CDC 同步问题 | `default` | clock_domain_a, clock_domain_b |

### 电源测试

| 假设内容 | test_case | 关键参数 |
|---------|-----------|----------|
| 欠压 | `undervoltage` | rail_name, threshold_v |
| 过流 | `overcurrent` | rail_name, max_current_ma |
| 其他电源问题 | `default` | rail_name |

### 温度测试

| 假设内容 | test_case | 关键参数 |
|---------|-----------|----------|
| 过热 | `overheat` | sensor_location, max_temp_c |
| 热循环 | `thermal_cycling` | cycle_count |
| 其他温度问题 | `default` | sensor_location |

### 通用测试

通用测试使用 `general_test` 工具，可传递任何 test_case 和相关参数。

## 测试执行指导

1. **使用 MCP Server 执行测试**
   ```python
   from mcp_server.server import get_server
   server = get_server()
   result = server.execute_tool_sync(tool_name, params)
   ```

2. **收集测试结果**
   - 记录测试状态（passed/failed/error）
   - 保存输出信息
   - 记录关键指标

3. **分析测试结果**
   - 与预期结果对比
   - 判断假设是否得到支持
   - 确定置信度调整

4. **更新状态**
   - 使用 state_manager 记录测试结果
   - 更新假设置信度
   - 记录决策日志

## 输出

返回包含以下内容的测试计划：
- 测试 ID 和序列
- 每个测试的工具、参数、预期结果
- 执行顺序
- 成功标准
- 测试结果记录模板
