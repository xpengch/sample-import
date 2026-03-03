# Hang Analysis Skill

## 描述

分析芯片日志中的系统挂死/死锁问题，包括硬件死锁、软件死锁、总线挂起等。

## 触发条件

当日志中出现以下关键词时触发：
- `hang`, `freeze`, `lockup`, `deadlock`
- `stuck`, `no response`, `timeout`
- `watchdog`, `WDT`, `watchdog reset`
- `system halt`, `stop`, `pause`
- `infinite loop`, `spin`

## 分析步骤

1. **识别挂死类型**
   - 确定挂死发生的时间点
   - 识别最后正常活动的日志
   - 定位挂死影响的功能模块

2. **检测挂死特征**
   - 搜索 Watchdog 触发记录
   - 查找心跳停止证据
   - 识别中断/响应异常

3. **分析根因**
   - 检查是否存在资源竞争
   - 验证锁和信号量使用
   - 分析 DMA 和总线状态

4. **生成假设**

   假设格式：
   ```json
   {
     "id": "H20",
     "category": "hang",
     "content": "DMA 控制器死锁导致总线挂起",
     "confidence": 0.75,
     "evidence": ["log_line_xxx", "log_line_yyy"],
     "test_history": []
   }
   ```

## 输出

返回分析结果，包含：
- 发现的挂死问题列表
- 每个问题的置信度
- 建议的测试方案
- 相关日志行号

## 常见问题模式

1. **硬件死锁**
   - 症状：系统完全无响应
   - 证据：`hard lockup`, `CPU stuck`
   - 测试：待补充

2. **软件死锁**
   - 症状：特定任务无响应
   - 证据：`deadlock`, `mutex`, `spinlock`
   - 测试：待补充

3. **总线挂起**
   - 症状：总线事务超时
   - 证据：`bus hang`, `AXI timeout`
   - 测试：待补充

4. **DMA 死锁**
   - 症状：DMA 传输卡死
   - 证据：`DMA hang`, `channel stuck`
   - 测试：待补充

5. **中断风暴**
   - 症状：CPU 被中断占满
   - 证据：`interrupt storm`, `IRQ flood`
   - 测试：待补充

6. **看门狗触发**
   - 症状：系统复位
   - 证据：`WDT timeout`, `watchdog reset`
   - 测试：待补充

## 待补充内容

- 具体测试用例
- 死锁检测方法
- 不同类型挂死的区分标准
