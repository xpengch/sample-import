# tests/test_main.py
import pytest
from unittest.mock import patch, Mock, MagicMock
from cli.main import main

@patch('cli.main.Path')
@patch('cli.main.WorkflowEngine')
@patch('cli.main.load_skills')
@patch('cli.main.load_config')
@patch('cli.main.LLMClient')
@patch('sys.argv', ['main.py', 'analyze', 'test.log'])
def test_main_analyze_command(mock_llm_client, mock_config, mock_skills, mock_engine, Path_mock):
    Path_mock.return_value.exists.return_value = True
    mock_config.return_value = {"llm": {"model": "test", "api_key": "test", "base_url": "https://test.com"}}
    mock_skills.return_value = [Mock()]
    mock_engine_instance = Mock()
    mock_engine.return_value = mock_engine_instance

    main()

    mock_engine_instance.run.assert_called_once_with('test.log')
