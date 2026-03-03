# skills/fault_detector/skill.py
import json
from typing import Dict, Any
from core.skill import Skill, SkillResult
from core.context import Context
from core.llm_client import LLMClient
from skills.fault_detector.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

class FaultDetectorSkill(Skill):
    """故障检测技能 - 使用 LLM 分析"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.system_prompt = SYSTEM_PROMPT

    @property
    def name(self) -> str:
        return "fault_detector"

    @property
    def use_llm(self) -> bool:
        return True

    def can_handle(self, context: Context) -> bool:
        return context.parsed_data is not None and \
               len(context.parsed_data.get("errors", [])) > 0

    def execute(self, context: Context) -> SkillResult:
        """执行故障检测"""
        # 准备输入
        errors = context.parsed_data.get("errors", [])
        warnings = context.parsed_data.get("warnings", [])

        # 构建 prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            errors=json.dumps(errors, ensure_ascii=False, indent=2),
            warnings=json.dumps(warnings, ensure_ascii=False, indent=2)
        )

        # 调用 LLM
        messages = [{"role": "user", "content": user_prompt}]

        # 添加用户输入作为上下文
        for user_input in context.user_inputs:
            self.llm.add_context(user_input)

        response = self.llm.chat(messages, system_prompt=self.system_prompt)

        # 解析响应
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取 JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                result = json.loads(response[start:end])
            else:
                return SkillResult(
                    success=False,
                    uncertain=True,
                    uncertainty_reason="LLM 返回格式错误",
                    options=["重试", "手动分析"]
                )

        # 处理不确定情况
        if result.get("uncertain", False):
            context.detected_faults = result.get("faults", [])
            return SkillResult(
                success=False,
                uncertain=True,
                uncertainty_reason=result.get("reason", "无法确定"),
                options=result.get("options", [])
            )

        # 正常情况
        context.detected_faults = result.get("faults", [])

        return SkillResult(
            success=True,
            data={
                "faults": context.detected_faults,
                "summary": result.get("summary", "")
            }
        )
