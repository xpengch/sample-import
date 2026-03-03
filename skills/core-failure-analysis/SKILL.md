# Core Failure Analysis Skill

## 描述

分析芯片日志中的计算核失效问题，包括 CPU/GPU/其他计算核的功能异常、性能异常、不可纠正错误等。

## 触发条件

当日志中出现以下关键词时触发：
- `core`, `CPU`, `GPU`, `compute`
- `core failure`, `core disable`, `core offline`
- `uncorrectable error`, `UE`, `UC`
- `correctable error`, `CE`, `ECC`
- `core hang`, `core stuck`
- `core reset`, `core reboot`

## 分析步骤

1. **识别失效核心**
   - 扫描核心标识和编号
   - 识别失效类型（功能/性能/错误）
   - 记录核心状态（active/disable/failed）

2. **检测失效特征**
   - 搜索不可纠正错误记录
   - 查找核心复位事件
   - 识别性能降级证据

3. **分析根因**
   - 检查核心电源域
   - 验证核心时钟和复位
   - 分析内存和缓存错误

4. **生成假设**

   假设格式：
   ```json
   {
     "id": "H50",
     "category": "core_failure",
     "content": "Core 3 发生不可纠正内存错误",
     "confidence": 0.9,
     "evidence": ["log_line_xxx", "log_line_yyy"],
     "test_history": []
   }
   ```

## 输出

返回分析结果，包含：
- 发现的核心失效问题列表
- 每个问题的置信度
- 建议的测试方案
- 相关日志行号

## 常见问题模式

1. **不可纠正错误（UE）**
   - 症状：核心被禁用或系统重启
   - 证据：`uncorrectable`, `UE`, `fatal error`
   - 测试：待补充

2. **可纠正错误（CE）溢出**
   - 症状：性能下降，可能发展为 UE
   - 证据：`correctable error`, `ECC`, `CE`
   - 测试：待补充

3. **核心挂死**
   - 症状：单个核心无响应
   - 证据：`core hang`, `core stuck`
   - 测试：待补充

4. **核心性能异常**
   - 症状：核心运行缓慢
   - 证据：`frequency drop`, `throttle`
   - 测试：待补充

5. **核心电源故障**
   - 症状：核心无法启动
   - 证据：`core power fail`, `VDD_Failure`
   - 测试：待补充

6. **核心热失效**
   - 症状：核心因过热被禁用
   - 证据：`core thermal`, `hot plugging`
   - 测试：待补充

7. **核心熔丝/配置错误**
   - 症状：核心初始化失败
   - 证据：`fuse error`, `config mismatch`
   - 测试：待补充

## 待补充内容

- 具体测试用例
- 错误注入方法
- 核心隔离和恢复策略
