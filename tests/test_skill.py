# tests/test_skill.py
import pytest
from abc import ABC
from core.skill import Skill, SkillResult

def test_skill_result_initialization():
    result = SkillResult(success=True, data={"faults": []})
    assert result.success is True
    assert result.uncertain is False
    assert result.data == {"faults": []}

def test_skill_result_uncertain():
    result = SkillResult(
        success=False,
        uncertain=True,
        uncertainty_reason="无法确定故障类型",
        options=["选项A", "选项B"]
    )
    assert result.uncertain is True
    assert result.uncertainty_reason == "无法确定故障类型"
    assert len(result.options) == 2

def test_skill_is_abstract():
    with pytest.raises(TypeError):
        Skill()  # 不能直接实例化抽象类
