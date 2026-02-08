"""Prompt templates used by the answer synthesizer."""

from __future__ import annotations


def build_system_prompt(language: str) -> str:
    return (
        "You are AutoSearch AI, a factual assistant that must ground every claim in provided sources. "
        f"Respond in {language}. Use concise markdown and include citation markers like [1], [2]. "
        "If evidence is weak, clearly say uncertainty."
    )


def build_user_prompt(query: str, sources: list[dict]) -> str:
    source_chunks: list[str] = []
    for index, source in enumerate(sources, start=1):
        title = source.get("title", "Untitled")
        url = source.get("url", "")
        snippet = source.get("snippet", "")
        content = source.get("content", "")
        source_chunks.append(
            f"[{index}] {title}\nURL: {url}\nSnippet: {snippet}\nContent: {content[:900]}\n"
        )

    joined = "\n".join(source_chunks)
    return (
        f"Question: {query}\n\n"
        "Use only the evidence below. Build a structured answer with key points and citations.\n\n"
        f"Sources:\n{joined}\n"
    )
