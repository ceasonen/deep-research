"""Unified OpenAI-compatible async client with fallback generation."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _resolve_runtime(self, runtime_config: dict[str, Any] | None = None) -> dict[str, Any]:
        runtime = runtime_config or {}
        base_url = (runtime.get("base_url") or self.settings.llm_base_url or "").strip() or None
        api_key = (runtime.get("api_key") or self.settings.llm_api_key or "").strip() or None
        model = (runtime.get("model") or self.settings.llm_model or "").strip() or self.settings.llm_model
        temperature = runtime.get("temperature")
        if temperature is None:
            temperature = self.settings.llm_temperature
        max_tokens = runtime.get("max_tokens")
        if max_tokens is None:
            max_tokens = self.settings.llm_max_tokens

        if self.settings.llm_provider == "ollama" and not base_url:
            base_url = "http://localhost:11434/v1"
            api_key = api_key or "ollama-local"

        return {
            "base_url": base_url,
            "api_key": api_key,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def _build_openai_client(self, runtime_config: dict[str, Any] | None = None):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            return None

        runtime = self._resolve_runtime(runtime_config)
        if not runtime["api_key"] and not runtime["base_url"]:
            return None

        kwargs = {}
        if runtime["base_url"]:
            kwargs["base_url"] = runtime["base_url"]

        if runtime["api_key"]:
            kwargs["api_key"] = runtime["api_key"]
        elif runtime["base_url"]:
            kwargs["api_key"] = "local-no-key"
        else:
            return None

        try:
            return AsyncOpenAI(**kwargs)
        except Exception as exc:  # pragma: no cover
            logger.warning("OpenAI client init failed: %s", exc)
            return None

    @property
    def is_available(self) -> bool:
        return self.is_available_for(None)

    def is_available_for(self, runtime_config: dict[str, Any] | None = None) -> bool:
        runtime = self._resolve_runtime(runtime_config)
        return bool(runtime["api_key"] or runtime["base_url"])

    async def complete(
        self, system_prompt: str, user_prompt: str, runtime_config: dict[str, Any] | None = None
    ) -> str:
        runtime = self._resolve_runtime(runtime_config)
        client = self._build_openai_client(runtime)
        if client is None:
            return "I could not reach an LLM provider, so here is a source-grounded summary from collected web snippets."

        try:
            response = await client.chat.completions.create(
                model=runtime["model"],
                temperature=runtime["temperature"],
                max_tokens=runtime["max_tokens"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # pragma: no cover
            logger.warning("LLM completion failed: %s", exc)
            return "The model request failed. Falling back to concise summary from retrieved sources."

    async def stream(
        self, system_prompt: str, user_prompt: str, runtime_config: dict[str, Any] | None = None
    ) -> AsyncGenerator[str, None]:
        runtime = self._resolve_runtime(runtime_config)
        client = self._build_openai_client(runtime)

        if client is None:
            yield "LLM unavailable. Returning source-based summary only."
            return

        try:
            stream = await client.chat.completions.create(
                model=runtime["model"],
                temperature=runtime["temperature"],
                max_tokens=runtime["max_tokens"],
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
