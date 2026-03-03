import os
import json
from datetime import datetime
from pathlib import Path

class StateManager:
    """状态管理器 - 管理假设迭代过程的状态"""

    # state.json 存储在用户目录
    STATE_DIR = os.path.expanduser("~/.chip-fault-locator")
    STATE_FILE = os.path.join(STATE_DIR, "state.json")

    def __init__(self):
        """初始化状态管理器"""
        os.makedirs(self.STATE_DIR, exist_ok=True)

    def create(self, log_file: str) -> dict:
        """创建新的状态"""
        return {
            "session_id": datetime.now().strftime('%Y%m%d-%H%M%S'),
            "log_file": log_file,
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
            "current_phase": "A",
            "iteration": 0,
            "max_iterations": 10,
            "hypotheses": [],
            "analysis_results": {},
            "test_results": [],
            "decision_log": [],
            "final_conclusion": None
        }

    def load(self) -> dict:
        """加载状态"""
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save(self, state: dict):
        """保存状态"""
        with open(self.STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def get(self) -> dict:
        """获取当前状态，如果不存在则返回 None"""
        return self.load()

    def update(self, updates: dict) -> dict:
        """更新状态"""
        state = self.get()
        if state is None:
            raise ValueError("状态不存在，请先使用 create() 创建")
        state.update(updates)
        self.save(state)
        return state

    def add_hypothesis(self, hypothesis: dict) -> dict:
        """添加假设"""
        state = self.get()
        if state is None:
            raise ValueError("状态不存在，请先使用 create() 创建状态")
        state["hypotheses"].append(hypothesis)
        self.save(state)
        return state

    def update_hypothesis(self, hypothesis_id: str, updates: dict) -> dict:
        """更新特定假设"""
        state = self.get()
        if state is None:
            raise ValueError("状态不存在，请先使用 create() 创建状态")

        for h in state["hypotheses"]:
            if h["id"] == hypothesis_id:
                h.update(updates)
                break

        self.save(state)
        return state

    def add_test_result(self, result: dict) -> dict:
        """添加测试结果"""
        state = self.get()
        if state is None:
            raise ValueError("状态不存在，请先使用 create() 创建状态")
        state["test_results"].append(result)
        self.save(state)
        return state

    def log_decision(self, decision: str) -> dict:
        """记录决策"""
        state = self.get()
        if state is None:
            raise ValueError("状态不存在，请先使用 create() 创建状态")

        state["decision_log"].append({
            "iteration": state.get("iteration", 0),
            "timestamp": datetime.now().isoformat(),
            "decision": decision
        })
        self.save(state)
        return state

    def increment_iteration(self) -> dict:
        """增加迭代计数"""
        state = self.get()
        if state is None:
            raise ValueError("状态不存在，请先使用 create() 创建状态")
        state["iteration"] = state.get("iteration", 0) + 1
        self.save(state)
        return state

    def set_phase(self, phase: str) -> dict:
        """设置当前阶段"""
        return self.update({"current_phase": phase})

    def set_status(self, status: str) -> dict:
        """设置状态"""
        return self.update({"status": status})

    def get_hypotheses(self) -> list:
        """获取所有假设"""
        state = self.get()
        return state["hypotheses"] if state else []

    def get_active_hypotheses(self) -> list:
        """获取未被排除的假设"""
        hypotheses = self.get_hypotheses()
        return [h for h in hypotheses if h.get("status") != "rejected"]

    def get_confirmed_hypothesis(self) -> dict:
        """获取已确认的假设（置信度最高）"""
        active = self.get_active_hypotheses()
        if not active:
            return None

        # 返回置信度最高的
        return max(active, key=lambda h: h.get("confidence", 0))

    def is_solved(self) -> bool:
        """判断是否已解决"""
        state = self.get()
        if not state:
            return False

        # 检查是否有高置信度假设
        confirmed = self.get_confirmed_hypothesis()
        if confirmed and confirmed.get("confidence", 0) >= 0.9:
            return True

        # 检查是否达到迭代上限
        if state.get("iteration", 0) >= state.get("max_iterations", 10):
            return True

        return False

    def get_progress_summary(self) -> str:
        """获取进度摘要"""
        state = self.get()
        if not state:
            return "状态未初始化"

        hypotheses = self.get_hypotheses()
        active = self.get_active_hypotheses()

        return f"""
进度摘要:
- 会话ID: {state.get('session_id')}
- 当前阶段: {state.get('current_phase')}
- 迭代次数: {state.get('iteration')}/{state.get('max_iterations')}
- 状态: {state.get('status')}
- 假设数量: {len(hypotheses)}
- 活跃假设: {len(active)}
- 是否已解决: {'是' if self.is_solved() else '否'}
        """.strip()
