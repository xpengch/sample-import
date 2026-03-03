# SIOH Analysis Skill

## 描述

分析芯片日志中的 SIOH（System I/O Hub，系统 I/O 集线器）相关问题，包括 I/O 接口错误、PCIe/SATA/USB 等接口异常等。

## 触发条件

当日志中出现以下关键词时触发：
- `SIOH`, `IOH`, `I/O hub`
- `PCIe`, `PCI`, `PCI express`
- `SATA`, `AHCI`
- `USB`, `xHCI`
- `IO error`, `link down`, `link training`
- `SIOH reset`, `IO timeout`

## 分析步骤

1. **识别 SIOH 相关组件**
   - 扫描 SIOH 寄存器访问记录
   - 识别 I/O 接口类型和通道
   - 记录 SIOH 配置状态

2. **检测 SIOH 问题**
   - 搜索链路训练失败记录
   - 查找 I/O 事务错误
   - 识别 SIOH 复位事件

3. **分析根因**
   - 检查 SIOH 电源和时钟
   - 验证链路参数配置
   - 分析 SIOH 固件状态

4. **生成假设**

   假设格式：
   ```json
   {
     "id": "H40",
     "category": "sioh",
     "content": "PCIe Gen4 链路训练失败",
     "confidence": 0.8,
     "evidence": ["log_line_xxx", "log_line_yyy"],
     "test_history": []
   }
   ```

## 输出

返回分析结果，包含：
- 发现的 SIOH 问题列表
- 每个问题的置信度
- 建议的测试方案
- 相关日志行号

## 常见问题模式

1. **PCIe 链路失败**
   - 症状：链路无法建立或降速
   - 证据：`link training fail`, `LTSSM`
   - 测试：待补充

2. **SATA 链路问题**
   - 症状：硬盘无法识别
   - 证据：`COMRESET`, `no device`
   - 测试：待补充

3. **USB 控制器异常**
   - 症状：USB 设备无法识别
   - 证据：`xHCI error`, `port status`
   - 测试：待补充

4. **SIOH 复位异常**
   - 症状：I/O 功能全部失效
   - 证据：`SIOH reset`, `IO hang`
   - 测试：待补充

5. **I/O 事务超时**
   - 症状：访问外设无响应
   - 证据：`IO timeout`, `completion timeout`
   - 测试：待补充

6. **MSI/MSI-X 中断问题**
   - 症状：中断无法送达
   - 证据：`MSI error`, `interrupt lost`
   - 测试：待补充

## 待补充内容

- 具体测试用例
- 各接口的调试方法
- SIOH 寄存器关键字段
