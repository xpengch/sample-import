# tests/test_log_parser.py
import pytest
from skills.log_parser.skill import LogParserSkill
from core.context import Context

def test_log_parser_skill_name():
    skill = LogParserSkill()
    assert skill.name == "log_parser"
    assert skill.use_llm is False

def test_log_parser_can_handle():
    skill = LogParserSkill()
    ctx = Context(raw_log="some log")
    assert skill.can_handle(ctx) is True

def test_log_parser_execute():
    skill = LogParserSkill()
    ctx = Context(raw_log="2026-03-03 [ERROR] Clock signal abnormal")

    result = skill.execute(ctx)

    assert result.success is True
    assert ctx.parsed_data is not None
    assert "errors" in ctx.parsed_data
    assert len(ctx.parsed_data["errors"]) > 0
