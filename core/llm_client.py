# core/llm_client.py
import os
from typing import Optional
import anthropic

class LLMClient:
    """Claude API 客户端"""

    def __init__(self, api_key: str, base_url: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.conversation_history = []
        self._client = anthropic.Anthropic(
            api_key=api_key,
            base_url=base_url
        )

    def chat(self, messages: list, system_prompt: Optional[str] = None) -> str:
        """调用 LLM"""
        # 构建完整消息列表（包含历史上下文）
        all_messages = self.conversation_history + messages

        kwargs = {
            "model": self.model,
            "messages": all_messages,
            "max_tokens": 4096
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)
        return response.content[0].text

    def add_context(self, info: str):
        """添加上下文供后续调用使用"""
        self.conversation_history.append({
            "role": "user",
            "content": f"[上下文信息] {info}"
        })

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
