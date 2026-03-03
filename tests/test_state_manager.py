"""Tests for core utilities."""
import pytest
import os
import tempfile
import json
from core_utils.state_manager import StateManager

def test_state_manager_initialization():
    """测试状态管理器初始化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 修改路径指向临时目录
        original_dir = StateManager.STATE_DIR
        StateManager.STATE_DIR = tmpdir
        StateManager.STATE_FILE = os.path.join(tmpdir, "test_state.json")

        try:
            sm = StateManager()
            state = sm.create("test.log")

            assert state["session_id"]
            assert state["log_file"] == "test.log"
            assert state["status"] == "in_progress"
            assert len(state["hypotheses"]) == 0
            assert state["iteration"] == 0
        finally:
            StateManager.STATE_DIR = original_dir
            StateManager.STATE_FILE = os.path.join(original_dir, "state.json")

def test_create_and_load_state():
    """测试创建和加载状态"""
    with tempfile.TemporaryDirectory() as tmpdir:
        StateManager.STATE_DIR = tmpdir
        StateManager.STATE_FILE = os.path.join(tmpdir, "test_state.json")

        try:
            sm = StateManager()
            created = sm.create("test.log")
            sm.save(created)

            loaded = sm.load()
            assert loaded["session_id"] == created["session_id"]
            assert loaded["log_file"] == "test.log"
        finally:
            StateManager.STATE_DIR = StateManager.STATE_DIR
            StateManager.STATE_FILE = os.path.join(StateManager.STATE_DIR, "state.json")

def test_add_hypothesis():
    """测试添加假设"""
    with tempfile.TemporaryDirectory() as tmpdir:
        StateManager.STATE_DIR = tmpdir
        StateManager.STATE_FILE = os.path.join(tmpdir, "test_state.json")

        try:
            sm = StateManager()
            state = sm.create("test.log")

            # 添加假设
            state = sm.add_hypothesis({
                "id": "H1",
                "content": "测试假设",
                "confidence": 0.7,
                "status": "pending",
                "evidence": [],
                "test_history": []
            })

            assert len(state["hypotheses"]) == 1
            assert state["hypotheses"][0]["id"] == "H1"

            # 加载验证
            loaded = sm.load()
            assert len(loaded["hypotheses"]) == 1
        finally:
            StateManager.STATE_DIR = StateManager.STATE_DIR
            StateManager.STATE_FILE = os.path.join(StateManager.STATE_DIR, "state.json")

def test_update_hypothesis():
    """测试更新假设"""
    with tempfile.TemporaryDirectory() as tmpdir:
        StateManager.STATE_DIR = tmpdir
        StateManager.STATE_FILE = os.path.join(tmpdir, "test_state.json")

        try:
            sm = StateManager()
            state = sm.create("test.log")
            state = sm.add_hypothesis({"id": "H1", "confidence": 0.7, "status": "pending"})

            # 更新置信度
            state = sm.update_hypothesis("H1", {"confidence": 0.95, "status": "confirmed"})

            hypotheses = sm.get_hypotheses()
            assert hypotheses[0]["confidence"] == 0.95
            assert hypotheses[0]["status"] == "confirmed"
        finally:
            StateManager.STATE_DIR = StateManager.STATE_DIR
            StateManager.STATE_FILE = os.path.join(StateManager.STATE_DIR, "state.json")

def test_iteration_management():
    """测试迭代管理"""
    with tempfile.TemporaryDirectory() as tmpdir:
        StateManager.STATE_DIR = tmpdir
        StateManager.STATE_FILE = os.path.join(tmpdir, "test_state.json")

        try:
            sm = StateManager()
            state = sm.create("test.log")

            assert state["iteration"] == 0

            state = sm.increment_iteration()
            assert state["iteration"] == 1

            state = sm.increment_iteration()
            assert state["iteration"] == 2

            # 检查是否已解决（默认未解决）
            assert not sm.is_solved()
        finally:
            StateManager.STATE_DIR = StateManager.STATE_DIR
            StateManager.STATE_FILE = os.path.join(StateManager.STATE_DIR, "state.json")

def test_progress_summary():
    """测试进度摘要"""
    with tempfile.TemporaryDirectory() as tmpdir:
        StateManager.STATE_DIR = tmpdir
        StateManager.STATE_FILE = os.path.join(tmpdir, "test_state.json")

        try:
            sm = StateManager()
            state = sm.create("test.log")
            state = sm.add_hypothesis({"id": "H1", "confidence": 0.95, "status": "confirmed"})

            summary = sm.get_progress_summary()

            assert "会话ID" in summary
            assert "迭代次数: 0" in summary
            assert "是否已解决: 是" in summary
        finally:
            StateManager.STATE_DIR = StateManager.STATE_DIR
            StateManager.STATE_FILE = os.path.join(StateManager.STATE_DIR, "state.json")
