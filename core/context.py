# core/context.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Decision:
    """决策记录"""
    step: int
    decision: str
    assumption: str
    timestamp: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())

@dataclass
class Conflict:
    """冲突信息"""
    conflicting_decision: Decision
    reason: str

class Context:
    """分析上下文"""

    def __init__(self, raw_log: str):
        self.raw_log = raw_log
        self.parsed_data = None
        self.detected_faults = []
        self.test_results = []
        self.user_inputs = []
        self.decision_history = []

    def add_user_input(self, info: str):
        """记录用户输入"""
        self.user_inputs.append(info)

    def add_decision(self, decision: Decision):
        """记录决策"""
        self.decision_history.append(decision)

    def check_conflict(self, new_info: str) -> Optional[Conflict]:
        """检查新信息是否与当前路径冲突"""
        # MVP 版本：暂不实现复杂冲突检测
        return None

    def has_conflict(self) -> bool:
        """是否存在冲突"""
        return False
