"""Unified OpenAI-compatible async client with graceful fallback behavior."""

from __future__ import annotations

import json
import re
import time
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._cooldown_until = 0.0
        self._last_error_message = ""

    @property
    def last_error_message(self) -> str:
        return self._last_error_message

    def resolved_model(self, runtime_config: dict[str, Any] | None = None) -> str:
        runtime = self._resolve_runtime(runtime_config)
        return runtime["model"]

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

        if not api_key:
            file_key = self._read_local_key_file()
            if file_key:
                api_key = file_key
                if not base_url:
                    base_url = self.settings.llm_auto_base_url
                if (
                    not runtime.get("model")
                    and not self.settings.llm_base_url
                    and self.settings.llm_model == "gpt-4o-mini"
                ):
                    model = self.settings.llm_auto_model

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

    def _read_local_key_file(self) -> str | None:
        key_file = (self.settings.llm_api_key_file or "").strip()
        if not key_file:
            return None
        try:
            content = Path(key_file).read_text(encoding="utf-8").strip()
            return content or None
        except Exception:
            return None

    def _build_openai_client(self, runtime: dict[str, Any]):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            return None

        if not runtime["api_key"] and not runtime["base_url"]:
            return None

        kwargs: dict[str, Any] = {"max_retries": 0}
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

    def _clear_last_error(self) -> None:
        self._last_error_message = ""

    def _set_last_error(self, message: str) -> None:
        self._last_error_message = message.strip()

    def _is_cooling_down(self) -> bool:
        return time.monotonic() < self._cooldown_until

    def _cooldown_remaining(self) -> float:
        return max(0.0, self._cooldown_until - time.monotonic())

    def _extract_retry_seconds(self, exc: Exception) -> float:
        default_retry = float(self.settings.llm_cooldown_default_seconds)
        candidates: list[float] = []

        payload = getattr(exc, "body", None)
        candidates.extend(self._collect_retry_values(payload))
        candidates.extend(self._collect_retry_values(str(exc)))

        if not candidates:
            return default_retry
        return max(default_retry, max(candidates))

    def _collect_retry_values(self, payload: Any) -> list[float]:
        values: list[float] = []
        if payload is None:
            return values

        if isinstance(payload, str):
            for pattern in (
                r"retry in\s+([0-9]+(?:\.[0-9]+)?)s",
                r"retrydelay['\"]?\s*[:=]\s*['\"]?([0-9]+(?:\.[0-9]+)?)s",
                r"retrydelay['\"]?\s*[:=]\s*['\"]?([0-9]+(?:\.[0-9]+)?)",
            ):
                for match in re.finditer(pattern, payload.lower()):
                    try:
                        values.append(float(match.group(1)))
                    except ValueError:
                        continue
            return values

        if isinstance(payload, bytes):
            try:
                decoded = payload.decode("utf-8", errors="ignore")
            except Exception:
                return values
            return self._collect_retry_values(decoded)

        if isinstance(payload, (int, float)):
            return values

        if isinstance(payload, dict):
            for key, value in payload.items():
                lowered = str(key).lower()
                if lowered == "retrydelay" and isinstance(value, str):
                    values.extend(self._collect_retry_values(f"retryDelay:{value}"))
                else:
                    values.extend(self._collect_retry_values(value))
            return values

        if isinstance(payload, list):
            for item in payload:
                values.extend(self._collect_retry_values(item))
            return values

        # Last-resort path for provider-specific objects.
        try:
            text = json.dumps(payload)
            values.extend(self._collect_retry_values(text))
        except Exception:
            values.extend(self._collect_retry_values(str(payload)))
        return values

    def _is_rate_limit_error(self, exc: Exception) -> bool:
        status_code = getattr(exc, "status_code", None)
        if status_code == 429:
            return True
        text = str(exc).lower()
        return any(token in text for token in ("429", "rate limit", "resource_exhausted", "quota"))

    def _handle_rate_limit(self, exc: Exception) -> None:
        retry_seconds = self._extract_retry_seconds(exc)
        self._cooldown_until = max(self._cooldown_until, time.monotonic() + retry_seconds)
        self._set_last_error(f"LLM quota exceeded. Retry in about {retry_seconds:.1f}s.")

    @property
    def is_available(self) -> bool:
        return self.is_available_for(None)

    def is_available_for(self, runtime_config: dict[str, Any] | None = None) -> bool:
        runtime = self._resolve_runtime(runtime_config)
        return bool(runtime["api_key"] or runtime["base_url"])

    async def complete(
        self, system_prompt: str, user_prompt: str, runtime_config: dict[str, Any] | None = None
    ) -> str:
        self._clear_last_error()
        runtime = self._resolve_runtime(runtime_config)
        client = self._build_openai_client(runtime)
        if client is None:
            self._set_last_error("LLM provider is not configured.")
            return ""

        if self._is_cooling_down():
            self._set_last_error(
                f"LLM quota cooldown active. Retry in about {self._cooldown_remaining():.1f}s."
            )
            return ""

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
            if self._is_rate_limit_error(exc):
                self._handle_rate_limit(exc)
            else:
                self._set_last_error("Model request failed. Please retry.")
            logger.warning("LLM completion failed: %s", exc)
            return ""

    async def stream(
        self, system_prompt: str, user_prompt: str, runtime_config: dict[str, Any] | None = None
    ) -> AsyncGenerator[str, None]:
        self._clear_last_error()
        runtime = self._resolve_runtime(runtime_config)
        client = self._build_openai_client(runtime)

        if client is None:
            self._set_last_error("LLM provider is not configured.")
            return

        if self._is_cooling_down():
            self._set_last_error(
                f"LLM quota cooldown active. Retry in about {self._cooldown_remaining():.1f}s."
            )
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
            if self._is_rate_limit_error(exc):
                self._handle_rate_limit(exc)
            else:
                self._set_last_error("Model stream failed. Please retry.")
            logger.warning("LLM streaming failed: %s", exc)
