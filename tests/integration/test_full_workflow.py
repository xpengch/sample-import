# tests/integration/test_full_workflow.py
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_full_workflow_with_sample_log():
    """测试完整工作流"""
    from cli.main import load_config, load_skills
    from core.workflow import WorkflowEngine
    from core.llm_client import LLMClient

    # 加载配置
    config = load_config()

    # 初始化 LLM 客户端（使用 mock）
    llm_client = LLMClient(
        api_key=os.environ.get("ANTHROPIC_AUTH_TOKEN", "test"),
        base_url=os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        model=config["llm"]["model"]
    )

    # 加载技能
    skills = load_skills(config, llm_client)

    # 创建工作流引擎
    engine = WorkflowEngine(llm_client=llm_client, skills=skills)

    # 执行
    log_file = "logs/sample.log"
    if Path(log_file).exists():
        engine.run(log_file)
    else:
        pytest.skip(f"Sample log file not found: {log_file}")
