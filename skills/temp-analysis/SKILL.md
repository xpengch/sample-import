# Temperature Analysis Skill

## 描述

分析芯片日志中的温度相关问题，包括过热、热循环异常、热关机等。

## 触发条件

当日志中出现以下关键词时触发：
- `temperature`, `temp`, `热`, `温度`
- `overheat`, `过热`, `thermal`
- `thermal shutdown`, `热关机`
- `thermal cycling`, `热循环`
- `junction`, `Tj`, `ambient`, `Ta`

## 分析步骤

1. **识别温度监测点**
   - 扫描温度传感器读数
   - 识别关键热点位置
   - 记录温度阈值配置

2. **检测温���问题**
   - 搜索过温告警/关机记录
   - 查找温度突变事件
   - 识别热保护触发

3. **分析根因**
   - 检查功耗分布
   - 验证散热设计
   - 分析工作占空比

4. **生成假设**

   假设格式：
   ```json
   {
     "id": "H3",
     "category": "temperature",
     "content": "CPU 核心过热导致热节流",
     "confidence": 0.75,
     "evidence": ["log_line_234", "log_line_567"],
     "test_history": []
   }
   ```

## 输出

返回分析结果，包含：
- 发现的温度问题列表
- 每个问题的置信度
- 建议的测试方案
- 相关日志行号

## 常见问题模式

1. **过热问题**
   - 症状：性能下降，热关机
   - 证据：`overheat`, `thermal throttle`, `Tj max`
   - 测试：使用 `temperature_test` 工具，test_case 设为 `overheat`

2. **热循环问题**
   - 症状：焊接疲劳，参数漂移
   - 证据：`thermal cycling`, `cycle count`
   - 测试：使用 `temperature_test` 工具，test_case 设为 `thermal_cycling`

3. **温度异常**
   - 症状：各种温度相关异常
   - 证据：`thermal error`, `sensor warning`
   - 测试：使用 `temperature_test` 工具，test_case 设为 `default`

## 支持的测试用例

| test_case | 描述 |
|-----------|------|
| `overheat` | 过热测试 |
| `thermal_cycling` | 热循环测试 |
| `default` | 默认温度测试 |
