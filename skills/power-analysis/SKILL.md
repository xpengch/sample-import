# Power Analysis Skill

## 描述

分析芯片日志中的电源相关问题，包括欠压、过流、功耗异常等。

## 触发条件

当日志中出现以下关键词时触发：
- `power`, `vdd`, `vcc`, `电源`
- `voltage`, `电压`, `current`, `电流`
- `undervoltage`, `欠压`, `brownout`, `掉电`
- `overcurrent`, `过流`, `short`, `短路`
- `power fail`, `UVLO`, `OCP`

## 分析步骤

1. **识别电源域**
   - 扫描电源轨定义（VDD, VCC, VDDIO 等）
   - 识别不同电压域的边界
   - 记录上电��序

2. **检测电源问题**
   - 搜索电压/电流异常报告
   - 查找电源保护触发记录
   - 识别功耗异常事件

3. **分析根因**
   - 检查电源管理配置
   - 验证 LDO/DCDC 工作状态
   - 分析负载电流分布

4. **生成假设**

   假设格式：
   ```json
   {
     "id": "H2",
     "category": "power",
     "content": "VDD_CORE 电压欠压导致逻辑错误",
     "confidence": 0.85,
     "evidence": ["log_line_789", "log_line_012"],
     "test_history": []
   }
   ```

## 输出

返回分析结果，包含：
- 发现的电源问题列表
- 每个问题的置信度
- 建议的测试方案
- 相关日志行号

## 常见问题模式

1. **欠压问题**
   - 症状：逻辑错误，复位触发
   - 证据：`undervoltage`, `brownout`, `UVLO`
   - 测试：使用 `power_test` 工具，test_case 设为 `undervoltage`

2. **过流问题**
   - 症状：电源跌落，过流保护触发
   - 证据：`overcurrent`, `OCP`, `current limit`
   - 测试：使用 `power_test` 工具，test_case 设为 `overcurrent`

3. **电源异常**
   - 症状：各种电源相关异常
   - 证据：`power fail`, `voltage error`
   - 测试：使用 `power_test` 工具，test_case 设为 `default`

## 支持的测试用例

| test_case | 描述 |
|-----------|------|
| `undervoltage` | 欠压测试 |
| `overcurrent` | 过流测试 |
| `default` | 默认电源测试 |
