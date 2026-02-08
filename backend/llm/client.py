"""Unified OpenAI-compatible async client with fallback generation."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    def _build_openai_client(self):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            return None

        kwargs = {}
        if self.settings.llm_api_key:
            kwargs["api_key"] = self.settings.llm_api_key
        if self.settings.llm_base_url:
            kwargs["base_url"] = self.settings.llm_base_url

        return AsyncOpenAI(**kwargs)

    @property
    def is_available(self) -> bool:
        return bool(self.settings.llm_api_key) or self.settings.llm_provider == "ollama"

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        if self._client is None:
            self._client = self._build_openai_client()

        if self._client is None:
            return "I could not reach an LLM provider, so here is a source-grounded summary from collected web snippets."

        try:
            response = await self._client.chat.completions.create(
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # pragma: no cover
            logger.warning("LLM completion failed: %s", exc)
            return "The model request failed. Falling back to concise summary from retrieved sources."

    async def stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        if self._client is None:
            self._client = self._build_openai_client()

        if self._client is None:
            yield "LLM unavailable. Returning source-based summary only."
            return

        try:
            stream = await self._client.chat.completions.create(
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
                stream=True,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as exc:  # pragma: no cover
            logger.warning("LLM streaming failed: %s", exc)
            yield "The model stream failed. Please retry."
