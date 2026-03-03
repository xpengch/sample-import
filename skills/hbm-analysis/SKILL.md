# HBM Analysis Skill

## 描述

分析芯片日志中的 HBM（High Bandwidth Memory）相关问题，包括 HBM 访问错误、性能降级、训练失败等。

## 触发条件

当日志中出现以下关键词时触发：
- `HBM`, `high bandwidth memory`
- `HBM training`, `training fail`
- `HBM access`, `HBM read`, `HBM write`
- `HBM error`, `HBM timeout`
- `DDR`, `DRAM`, `memory channel`
- `HBM temperature`, `HBM thermal`

## 分析步骤

1. **识别 HBM 相关组件**
   - 扫描 HBM 堆栈标识
   - 识别 HBM 控制器和通道
   - 记录 HBM 配置参数

2. **检测 HBM 问题**
   - 搜索 HBM 训练失败记录
   - 查找 HBM 访问错误
   - 识别 HBM 性能异常

3. **分析根因**
   - 检查 HBM 电源和时钟
   - 验证 HBM 温度状态
   - 分析 HBM 时序参数

4. **生成假设**

   假设格式：
   ```json
   {
     "id": "H10",
     "category": "hbm",
     "content": "HBM Stack 0 训练失败",
     "confidence": 0.8,
     "evidence": ["log_line_xxx", "log_line_yyy"],
     "test_history": []
   }
   ```

## 输出

返回分析结果，包含：
- 发现的 HBM 问题列表
- 每个问题的置信度
- 建议的测试方案
- 相关日志行号

## 常见问题模式

1. **HBM 训练失败**
   - 症状：系统初始化失败
   - 证据：`training fail`, `calibration error`
   - 测试：待补充

2. **HBM 访问错误**
   - 症状：读写错误，数据损坏
   - 证据：`access error`, `parity error`
   - 测试：待补充

3. **HBM 性能降级**
   - 症状：带宽下降，延迟增加
   - 证据：`performance degrade`, `low bandwidth`
   - 测试：待补充

4. **HBM 过热**
   - 症状：节流，错误增加
   - 证据：`HBM overheat`, `thermal throttle`
   - 测试：待补充

5. **HBM 电源问题**
   - 症状：HBM 无响应
   - 证据：`HBM power fail`, `VDDQ`
   - 测试：待补充

## 待补充内容

- 具体测试用例
- 阈值参数
- 与其他模块的关联分析
