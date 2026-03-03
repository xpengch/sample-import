# tests/test_llm_client.py
import pytest
from unittest.mock import Mock, patch
from core.llm_client import LLMClient

def test_llm_client_initialization():
    client = LLMClient(
        api_key="test_key",
        base_url="https://api.test.com",
        model="claude-3-5-sonnet-20241022"
    )
    assert client.api_key == "test_key"
    assert client.model == "claude-3-5-sonnet-20241022"
    assert len(client.conversation_history) == 0

def test_add_context():
    client = LLMClient(api_key="test", base_url="https://test.com", model="test")
    client.add_context("芯片批次有已知问题")
    assert len(client.conversation_history) == 1
    assert "芯片批次" in client.conversation_history[0]["content"]

@patch('core.llm_client.anthropic.Anthropic')
def test_chat_call(mock_anthropic):
    mock_response = Mock()
    mock_response.content = [Mock(text="测试响应")]
    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    client = LLMClient(api_key="test", base_url="https://test.com", model="test")
    result = client.chat([{"role": "user", "content": "测试"}])

    assert result == "测试响应"
    mock_client.messages.create.assert_called_once()
