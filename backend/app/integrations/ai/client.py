"""AI 服务统一客户端。

支持 Anthropic Claude 和 OpenAI 兼容接口（含 DeepSeek）。
按 settings.DEFAULT_AI_PROVIDER 路由。
"""
from typing import List, Literal, Optional

from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class AIClient:
    """AI 统一封装。"""

    async def chat(
        self,
        system: str,
        user: str,
        provider: Optional[Literal["anthropic", "openai"]] = None,
    ) -> str:
        """单轮对话，返回文本。"""
        p = provider or settings.DEFAULT_AI_PROVIDER
        if p == "anthropic":
            return await self._chat_anthropic(system, user)
        return await self._chat_openai(system, user)

    async def _chat_anthropic(self, system: str, user: str) -> str:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("未配置 ANTHROPIC_API_KEY")

        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        resp = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return resp.content[0].text

    async def _chat_openai(self, system: str, user: str) -> str:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("未配置 OPENAI_API_KEY")

        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        resp = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=4096,
        )
        return resp.choices[0].message.content or ""


ai = AIClient()
