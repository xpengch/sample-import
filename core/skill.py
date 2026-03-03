# core/skill.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from core.context import Context

@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    data: Any = None
    uncertain: bool = False
    uncertainty_reason: Optional[str] = None
    options: list[str] = field(default_factory=list)

class Skill(ABC):
    """技能基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称"""
        pass

    @property
    def use_llm(self) -> bool:
        """是否使用 LLM"""
        return False

    @abstractmethod
    def can_handle(self, context: Context) -> bool:
        """判断当前技能是否适用于该上下文"""
        pass

    @abstractmethod
    def execute(self, context: Context) -> SkillResult:
        """执行技能，返回结果"""
        pass
