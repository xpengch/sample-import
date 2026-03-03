# cli/main.py
import sys
import yaml
import os
from pathlib import Path
from core.workflow import WorkflowEngine
from core.llm_client import LLMClient

def load_config(config_path: str = "config.yaml") -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 环境变量替换
    if "llm" in config:
        for key in ["api_key", "base_url"]:
            if key in config["llm"]:
                value = config["llm"][key]
                if isinstance(value, str) and value.startswith("${"):
                    env_var = value[2:-1]
                    config["llm"][key] = os.environ.get(env_var, value)

    return config

def load_skills(config: dict, llm_client: LLMClient) -> list:
    """加载技能"""
    skills = []

    if config.get("skills", {}).get("log_parser", {}).get("enabled", True):
        from skills.log_parser import LogParserSkill
        skills.append(LogParserSkill())

    if config.get("skills", {}).get("fault_detector", {}).get("enabled", True):
        from skills.fault_detector import FaultDetectorSkill
        skills.append(FaultDetectorSkill(llm_client=llm_client))

    return skills

def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Usage: python -m cli.main analyze <log_file>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: python -m cli.main analyze <log_file>")
            sys.exit(1)

        log_file = sys.argv[2]

        # 检查文件存在
        if not Path(log_file).exists():
            print(f"错误: 日志文件不存在: {log_file}")
            sys.exit(1)

        # 加载配置
        config = load_config()

        # 初始化 LLM 客户端
        llm_config = config.get("llm", {})
        llm_client = LLMClient(
            api_key=llm_config.get("api_key", ""),
            base_url=llm_config.get("base_url", ""),
            model=llm_config.get("model", "claude-3-5-sonnet-20241022")
        )

        # 加载技能
        skills = load_skills(config, llm_client)

        # 运行工作流
        engine = WorkflowEngine(llm_client=llm_client, skills=skills)
        engine.run(log_file)

    else:
        print(f"未知命令: {command}")
        print("可用命令: analyze")
        sys.exit(1)

if __name__ == "__main__":
    main()
