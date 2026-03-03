# 芯片样片问题定位系统 - 实施计划 v6

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v6 | 2026-03-03 | 实现方案3：单板控制模块 (board_controller) |
| v5 | 2026-03-03 | 添加5个专项分析 Skill 框架 |
| v4 | 2026-03-03 | Skills 文档与实现对齐 |
| v3 | 2026-03-03 | MCP Server 框架 |
| v2 | 2026-03-03 | State Manager 实现 |
| v1 | 2026-03-03 | 初始架构设计 |

## v6 新增功能：单板控制模块

### 方案选择：方案3（实用平衡方案）

在三种方案中选择方案3，在清晰性和实现难度之间取得平衡。

### 新增模块：board_controller

```
board_controller/
├── __init__.py              # 模块初始化
├── connections.py           # 双通道连接管理（串口+SSH+Ping）
├── monitors.py              # 监控器（挂死检测+启动监控）
├── resume.py                # 断点续传管理器
└── controller.py            # 统一控制器
```

### 核心功能

| 功能 | 实现方式 | 说明 |
|------|---------|------|
| **双通道控制** | ConnectionManager | 串口(console) + SSH + Ping 统一管理 |
| **挂死检测** | HangMonitor | 串口无输出 + Ping失败 → 判定挂死 |
| **启动监控** | BootMonitor | 关键字检测 + 超时控制 |
| **断点续传** | ResumeManager | 检查点保存/恢复，支持测试中断恢复 |
| **统一控制** | BoardController | 整合所有功能，提供统一接口 |

### 主要接口

```python
# 初始化控制器
controller = BoardController(config)
await controller.initialize()

# 重启单板
result = await controller.restart_board(
    restart_type="soft",      # soft/hard/power_cycle
    wait_for_boot=True,
    timeout=300,
    boot_keywords=["login:", "root@"]
)

# 挂死检测
is_hung, details = await controller.detect_hang(
    detection_time=60,
    strict_mode=True  # 串口+网络都检查
)

# 等待启动
success, output, metrics = await controller.wait_for_boot(
    keywords=["login:", "root@"],
    timeout=300,
    verify_ping=True
)

# 断点续传
controller.save_checkpoint("before_restart", {...})
data = controller.load_checkpoint("before_restart")
```

### MCP Tools 扩展

新增 `board_control` 工具：

```python
# 通过 MCP 调用
result = server.execute_tool_sync("board_control", {
    "test_id": "test_001",
    "action": "restart",
    "restart_type": "soft",
    "wait_for_boot": True,
    "timeout": 300
})
```

支持的操作：
- `restart`: 重启单板
- `detect_hang`: 检测挂死
- `wait_boot`: 等待启动
- `check_status`: 检查状态
- `save_checkpoint`: 保存检查点
- `load_checkpoint`: 加载检查点
- `can_resume`: 检查是否可恢复

### 配置文件

`config/board_config.yaml` 包含：
- 默认配置
- 本地单板配置示例
- 远程单板配置示例
- 测试配置
- 断点续传配置

## 完整目录结构

```
sample_import/
├── board_controller/               # 新增 v6
│   ├── __init__.py
│   ├── connections.py
│   ├── monitors.py
│   ├── resume.py
│   └── controller.py
├── mcp_server/
│   ├── tools.py                    # 扩展 v6
│   ├── mock_tools.py               # 扩展 v6
│   └── server.py
├── config/
│   └── board_config.yaml          # 新增 v6
├── skills/                        # 11 个 Skills
├── core_utils/
│   └── state_manager.py
├── tests/
│   ├── test_state_manager.py      # 7 个测试
│   ├── test_mcp_server.py         # 10 个测试
│   └── test_board_controller.py  # 新增 v6: 17 个测试
└── README.md
```

## 测试覆盖

| 模块 | 测试数 | 状态 |
|------|--------|------|
| state_manager | 7 | ✅ |
| mcp_server | 10 | ✅ |
| board_controller | 17 | ✅ |
| **总计** | **34** | ✅ |

## 使用示例

### 基础使用

```python
from board_controller import BoardController

# 配置
config = {
    "mode": "local",
    "serial": {
        "port": "COM3",
        "baudrate": 115200
    },
    "ping": {
        "host": "192.168.1.100"
    },
    "boot": {
        "keywords": ["login:", "root@"]
    }
}

# 创建控制器
controller = BoardController(config)
await controller.initialize()

# 重启单板并等待启动
result = await controller.restart_board(
    restart_type="soft",
    wait_for_boot=True,
    timeout=300
)

if result["success"]:
    print("单板重启成功")
else:
    print(f"重启失败: {result['error']}")
```

### 挂死问题分析流程

```python
# 1. 检测挂死
is_hung, details = await controller.detect_hang(
    detection_time=60,
    strict_mode=True
)

if is_hung:
    print("检测到单板挂死")
    print(f"  串口活动: {details['serial_activity']}")
    print(f"  Ping成功: {details['ping_success']}")

    # 2. 保存检查点
    controller.save_checkpoint("before_restart", {
        "detected_hang": True,
        "details": details
    })

    # 3. 重启单板
    result = await controller.restart_board(
        restart_type="hard",  # 挂死后需要硬重启
        wait_for_boot=True,
        timeout=300
    )

    # 4. 验证恢复
    if result["success"]:
        controller.save_checkpoint("after_restart", {
            "status": "recovered",
            "timestamp": datetime.now().isoformat()
        })
```

## 下一步

1. **真实硬件测试**：在真实单板上测试连接和监控功能
2. **依赖安装**：pyserial、asyncssh
3. **Skill 更新**：更新 hang-analysis Skill 使用新的 board_controller
4. **异常处理**：添加更完善的异常处理和日志记录
5. **性能优化**：优化长时间等待的资源占用
