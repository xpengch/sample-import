# tests/test_context.py
import pytest
from core.context import Context, Decision

def test_context_initialization():
    ctx = Context(raw_log="test log")
    assert ctx.raw_log == "test log"
    assert ctx.parsed_data is None
    assert len(ctx.user_inputs) == 0

def test_add_user_input():
    ctx = Context(raw_log="test")
    ctx.add_user_input("芯片批次有已知问题")
    assert len(ctx.user_inputs) == 1
    assert "芯片批次" in ctx.user_inputs[0]

def test_add_decision():
    ctx = Context(raw_log="test")
    decision = Decision(
        step=1,
        decision="问题类型=时钟故障",
        assumption="时钟未更换"
    )
    ctx.add_decision(decision)
    assert len(ctx.decision_history) == 1
    assert ctx.decision_history[0].decision == "问题类型=时钟故障"

def test_no_conflict_by_default():
    ctx = Context(raw_log="test")
    conflict = ctx.check_conflict("新信息")
    assert conflict is None
