# core/workflow.py
from typing import List, Optional
from core.context import Context
from core.llm_client import LLMClient
from core.skill import Skill

class WorkflowEngine:
    """工作流引擎"""

    def __init__(self, llm_client: LLMClient, skills: List[Skill]):
        self.llm = llm_client
        self.skills = skills
        self.user_pause_requested = False

    def select_next_skill(self, context: Context) -> Optional[Skill]:
        """选择下一个可执行的技能"""
        for skill in self.skills:
            if skill.can_handle(context):
                return skill
        return None

    def run(self, log_file: str):
        """执行工作流"""
        # 读取日志文件
        with open(log_file, 'r', encoding='utf-8') as f:
            raw_log = f.read()

        # 初始化上下文
        context = Context(raw_log=raw_log)

        # 主循环
        iteration = 0
        max_iterations = 10

        while iteration < max_iterations:
            iteration += 1

            # 选择技能
            skill = self.select_next_skill(context)
            if not skill:
                print(f"[系统] 没有可执行的技能，分析结束")
                break

            print(f"[系统] 执行技能: {skill.name}")

            # 执行技能
            result = skill.execute(context)

            if result.uncertain:
                print(f"[系统] 需要人工判断: {result.uncertainty_reason}")
                # MVP 版本：暂时打印选项
                for i, opt in enumerate(result.options, 1):
                    print(f"  {i}. {opt}")
                break

            if not result.success:
                print(f"[系统] 技能执行失败")
                break

            print(f"[系统] 技能执行成功")

            # 简单完成条件
            if skill.name == "fault_detector" and result.success:
                print(f"[系统] 故障检测完成")
                break

        print(f"[系统] 工作流结束，迭代次数: {iteration}")
