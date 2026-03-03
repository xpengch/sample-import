"""Tests for board_controller module."""

import pytest
import tempfile
import json
from pathlib import Path
from board_controller.connections import ConnectionManager, ConnectionType
from board_controller.monitors import HangMonitor, BootMonitor
from board_controller.resume import ResumeManager
from board_controller.controller import BoardController, BoardMode


class TestConnectionManager:
    """测试连接管理器（需要硬件，使用Mock模式）"""

    def test_init_local_mode(self):
        """测试本地模式初始化"""
        config = {
            "mode": "local",
            "serial": {"port": "COM3", "baudrate": 115200},
            "ping": {"host": "192.168.1.100", "timeout": 5}
        }
        cm = ConnectionManager(config)

        assert cm.mode == "local"
        assert cm.serial_config["port"] == "COM3"
        assert cm.ping_config["host"] == "192.168.1.100"

    def test_init_remote_mode(self):
        """测试远程模式初始化"""
        config = {
            "mode": "remote",
            "ssh": {
                "host": "192.168.1.101",
                "port": 22,
                "username": "root",
                "password": "password"
            },
            "ping": {"host": "192.168.1.101", "timeout": 5}
        }
        cm = ConnectionManager(config)

        assert cm.mode == "remote"
        assert cm.ssh_config["host"] == "192.168.1.101"

    def test_get_status(self):
        """测试获取连接状态"""
        config = {
            "mode": "local",
            "serial": {"port": "COM3"},
            "ping": {"host": "192.168.1.100"}
        }
        cm = ConnectionManager(config)

        status = cm.get_status()
        assert "mode" in status
        assert "serial_connected" in status
        assert "ping_activity_age" in status


class TestHangMonitor:
    """测试挂死监控器"""

    def test_init(self):
        """测试初始化"""
        class MockConnection:
            async def ping(self):
                return True

            async def read_serial_output(self, timeout=2):
                return None

            def get_serial_activity_age(self):
                return 10

        mock_conn = MockConnection()
        monitor = HangMonitor(mock_conn)

        assert monitor.config["serial_timeout"] == 60
        assert monitor.config["consecutive_failures"] == 3

    def test_is_hung_strict_mode(self):
        """测试严格模式挂死判断"""
        monitor = HangMonitor(None)

        # 严格模式：串口和网络都无响应
        details = {
            "serial_activity": False,
            "ping_success": False,
            "consecutive_ping_failures": 3
        }
        assert monitor._is_hung(details, strict_mode=True) is True

        # 有任何响应则不是挂死
        details["serial_activity"] = True
        assert monitor._is_hung(details, strict_mode=True) is False

    def test_is_hung_loose_mode(self):
        """测试宽松模式挂死判断"""
        monitor = HangMonitor(None)

        # 宽松模式：任一条件满足即挂死
        details = {
            "serial_activity": False,
            "ping_success": True,
            "consecutive_ping_failures": 0
        }
        # 串口无活动也算挂死
        assert monitor._is_hung(details, strict_mode=False) is True


class TestBootMonitor:
    """测试启动监控器"""

    def test_init(self):
        """测试初始化"""
        class MockConnection:
            pass

        mock_conn = MockConnection()
        monitor = BootMonitor(mock_conn)

        assert monitor.config["boot_keywords"] == ["login:", "root@", "# "]
        assert monitor.config["timeout"] == 300

    def test_init_with_config(self):
        """测试带配置的初始化"""
        class MockConnection:
            pass

        mock_conn = MockConnection()
        config = {
            "boot_keywords": ["OK", "Ready"],
            "timeout": 600
        }
        monitor = BootMonitor(mock_conn, config)

        assert monitor.config["boot_keywords"] == ["OK", "Ready"]
        assert monitor.config["timeout"] == 600


class TestResumeManager:
    """测试断点续传管理器"""

    def test_init(self):
        """测试初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            rm = ResumeManager()
            # 验证目录创建
            assert rm.checkpoint_dir.exists()

    def test_save_and_load_checkpoint(self):
        """测试保存和加载检查点"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path
            rm = ResumeManager("test_session")
            rm.checkpoint_dir = Path(tmpdir)

            # 保存检查点
            data = {"test": "data", "value": 123}
            success = rm.save_checkpoint("test_checkpoint", data)
            assert success is True

            # 加载检查点
            loaded = rm.load_checkpoint("test_checkpoint")
            assert loaded is not None
            assert loaded["test"] == "data"
            assert loaded["value"] == 123

            # 验证文件存在
            checkpoint_file = rm._get_checkpoint_file()
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                assert checkpoint["session_id"] == "test_session"
                assert checkpoint["checkpoint_id"] == "test_checkpoint"

    def test_has_checkpoint(self):
        """测试检查点存在性检查"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path
            rm = ResumeManager("test_session")
            rm.checkpoint_dir = Path(tmpdir)

            # 初始没有检查点
            assert rm.has_checkpoint() is False

            # 保存检查点后
            rm.save_checkpoint("test", {"data": "test"})
            assert rm.has_checkpoint() is True

    def test_get_checkpoint_info(self):
        """测试获取检查点信息"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path
            rm = ResumeManager("test_session")
            rm.checkpoint_dir = Path(tmpdir)

            # 没有检查点时
            info = rm.get_checkpoint_info()
            assert info is None

            # 保存检查点后
            rm.save_checkpoint("test", {"data": "test"})
            info = rm.get_checkpoint_info()
            assert info is not None
            assert info["session_id"] == "test_session"
            assert info["has_checkpoint"] is True

    def test_delete_checkpoint(self):
        """测试删除检查点"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path
            rm = ResumeManager("test_session")
            rm.checkpoint_dir = Path(tmpdir)

            # 保存检查点
            rm.save_checkpoint("test", {"data": "test"})
            assert rm.has_checkpoint() is True

            # 删除检查点
            success = rm.delete_checkpoint()
            assert success is True
            assert rm.has_checkpoint() is False


class TestBoardController:
    """测试统一控制器"""

    def test_init_local_mode(self):
        """测试本地模式初始化"""
        config = {
            "mode": "local",
            "serial": {"port": "COM3"},
            "ping": {"host": "192.168.1.100"},
            "boot": {"keywords": ["login:"]}
        }
        controller = BoardController(config)

        assert controller.mode == BoardMode.LOCAL
        assert controller.current_status == "unknown"

    def test_init_remote_mode(self):
        """测试远程模式初始化"""
        config = {
            "mode": "remote",
            "ssh": {
                "host": "192.168.1.101",
                "port": 22,
                "username": "root",
                "password": "password"
            },
            "ping": {"host": "192.168.1.101"},
            "boot": {"keywords": ["login:"]}
        }
        controller = BoardController(config)

        assert controller.mode == BoardMode.REMOTE

    def test_get_restart_command(self):
        """测试获取重启命令"""
        config = {"mode": "local"}
        controller = BoardController(config)

        assert controller._get_restart_command("soft") == "reboot"
        assert controller._get_restart_command("hard") == "reboot -f"
        assert controller._get_restart_command("power_cycle") == "power_cycle_command"

    def test_get_status(self):
        """测试获取控制器状态"""
        config = {
            "mode": "local",
            "serial": {"port": "COM3"},
            "ping": {"host": "192.168.1.100"}
        }
        controller = BoardController(config)

        status = controller.get_status()
        assert status["mode"] == "local"
        assert status["current_status"] == "unknown"
        assert status["initialized"] is False
        assert "connection" in status
