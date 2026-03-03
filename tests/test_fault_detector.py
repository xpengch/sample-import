# tests/test_fault_detector.py
import pytest
from unittest.mock import Mock
from skills.fault_detector.skill import FaultDetectorSkill
from core.context import Context

@pytest.fixture
def mock_llm():
    mock = Mock()
    mock.chat.return_value = """{
  "faults": [
    {
      "type": "clock_signal",
      "severity": "high",
      "confidence": 0.85,
      "evidence": ["Clock signal abnormal at 10:00:05"]
    }
  ],
  "summary": "检测到时钟信号异常"
}"""
    return mock

def test_fault_detector_name():
    skill = FaultDetectorSkill(llm_client=Mock())
    assert skill.name == "fault_detector"
    assert skill.use_llm is True

def test_fault_detector_can_handle():
    skill = FaultDetectorSkill(llm_client=Mock())
    ctx = Context(raw_log="test")
    ctx.parsed_data = {"errors": [{"message": "Clock abnormal"}]}
    assert skill.can_handle(ctx) is True

def test_fault_detector_execute(mock_llm):
    skill = FaultDetectorSkill(llm_client=mock_llm)
    ctx = Context(raw_log="test")
    ctx.parsed_data = {"errors": [{"message": "Clock abnormal"}]}

    result = skill.execute(ctx)

    assert result.success is True
    assert len(ctx.detected_faults) > 0
    mock_llm.chat.assert_called_once()

def test_fault_detector_uncertain():
    mock_llm = Mock()
    mock_llm.chat.return_value = """{
  "uncertain": true,
  "reason": "多个故障信号概率接近",
  "faults": [
    {"type": "clock", "confidence": 0.48},
    {"type": "power", "confidence": 0.47}
  ],
  "options": ["优先检查时钟", "优先检查电源"]
}"""

    skill = FaultDetectorSkill(llm_client=mock_llm)
    ctx = Context(raw_log="test")
    ctx.parsed_data = {"errors": [{"message": "Multiple issues"}]}

    result = skill.execute(ctx)

    assert result.uncertain is True
    assert "概率接近" in result.uncertainty_reason
    assert len(result.options) > 0
