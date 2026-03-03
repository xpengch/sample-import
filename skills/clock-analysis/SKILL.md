# Clock Analysis Skill

## 描述

分析芯片日志中的时钟域相关问题，包括时钟偏斜、跨时钟域、时钟串扰、建立/保持时间违例等。

## 触发条件

当日志中出现以下关键词时触发：
- `clock`, `clk`, `时钟`
- `skew`, `jitter`, `偏斜`, `抖动`
- `setup`, `hold`, `建立时间`, `保持时间`
- `crosstalk`, `串扰`
- `CDC`, `跨时钟域`
- `metastability`, `亚稳态`

## 分析步骤

1. **识别时钟域**
   - 扫描日志中的时钟信号定义
   - 识别不同时钟域的边界
   - 记录时钟频率和相位关系

2. **检测时钟问题**
   - 搜索时序违例报告
   - 查找 CDC 跨时钟域��号
   - 识别时钟树问题

3. **分析根因**
   - 检查时钟源配置
   - 验证时钟分频/倍频逻辑
   - 分析时钟树综合结果

4. **生成假设**

   假设格式：
   ```json
   {
     "id": "H1",
     "category": "clock",
     "content": "时钟域A到域B的CDC同步不当",
     "confidence": 0.8,
     "evidence": ["log_line_123", "log_line_456"],
     "test_plan": {
       "tool": "clock_test",
       "test_case": "cdc_violation",
       "expected": "fail"
     }
   }
   ```

## 输出

返回分析结果，包含：
- 发现的时钟问题列表
- 每个问题的置信度
- 建议的测试方案
- 相关日志行号

## 常见问题模式

1. **时钟偏斜过大**
   - 症状：时序违例，数据采样错误
   - 证据：`setup violation`, `hold violation`
   - 测试：使用 `clock_test` 工具，test_case 设为 `skew`

2. **CDC 同步问题**
   - 症状：亚稳态，随机错误
   - 证据：`metastability`, `async reset`
   - 测试：使用 `clock_test` 工具，test_case 设为 `cdc_violation`

3. **时钟串扰**
   - 症状：时钟抖动增加
   - 证据：`jitter`, `crosstalk`
   - 测试：使用 `clock_test` 工具，test_case 设为 `crosstalk`

4. **时钟缺失/错误**
   - 症状：模块无响应
   - 证据：`no clock`, `clock stuck`
   - 测试：使用 `clock_test` 工具，test_case 设为 `clock_missing`
