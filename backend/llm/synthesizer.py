"""Answer synthesis using retrieved source evidence."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from backend.llm.client import LLMClient
from backend.llm.prompts import build_system_prompt, build_user_prompt


class AnswerSynthesizer:
    def __init__(self) -> None:
        self.client = LLMClient()

    async def generate(self, query: str, sources: list[dict], language: str = "en") -> str:
        if not sources:
            return "No reliable sources were retrieved for this query."

        system_prompt = build_system_prompt(language)
        user_prompt = build_user_prompt(query, sources)

        answer = await self.client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        if not answer.strip():
            return self._fallback_answer(sources)
        return answer

    async def stream(self, query: str, sources: list[dict], language: str = "en") -> AsyncGenerator[str, None]:
        if not sources:
            yield "No reliable sources were retrieved for this query."
            return

        system_prompt = build_system_prompt(language)
        user_prompt = build_user_prompt(query, sources)

        had_output = False
        async for chunk in self.client.stream(system_prompt=system_prompt, user_prompt=user_prompt):
            had_output = True
            yield chunk

        if not had_output:
            yield self._fallback_answer(sources)

    def _fallback_answer(self, sources: list[dict]) -> str:
        bullet_lines = []
        for index, source in enumerate(sources[:5], start=1):
            bullet_lines.append(f"- {source.get('title', 'Untitled')} [{index}]")
        return "I could not produce a full LLM answer. Key retrieved sources:\n" + "\n".join(bullet_lines)
