# tests/test_workflow.py
import pytest
from unittest.mock import Mock, patch
from core.workflow import WorkflowEngine
from core.context import Context
from core.llm_client import LLMClient

@pytest.fixture
def mock_skills():
    return [Mock(), Mock()]

@pytest.fixture
def mock_llm():
    return Mock(spec=LLMClient)

def test_workflow_initialization(mock_llm, mock_skills):
    engine = WorkflowEngine(llm_client=mock_llm, skills=mock_skills)
    assert engine.llm == mock_llm
    assert len(engine.skills) == 2

def test_workflow_select_next_skill(mock_llm, mock_skills):
    mock_skills[0].can_handle.return_value = False
    mock_skills[1].can_handle.return_value = True

    engine = WorkflowEngine(llm_client=mock_llm, skills=mock_skills)
    ctx = Context(raw_log="test")

    skill = engine.select_next_skill(ctx)
    assert skill == mock_skills[1]

@patch('core.workflow.WorkflowEngine.run')
def test_workflow_run(mock_run, mock_llm, mock_skills):
    """测试工作流可以被调用"""
    engine = WorkflowEngine(llm_client=mock_llm, skills=mock_skills)
    engine.run("test.log")
    mock_run.assert_called_once_with("test.log")
