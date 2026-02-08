"""Lightweight AI analysis layer for ArXiv papers."""

from __future__ import annotations

import json
import re

from backend.llm.client import LLMClient
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ArxivPaperAnalyzer:
    def __init__(self) -> None:
        self.client = LLMClient()

    async def analyze_many(self, papers: list[dict], query: str) -> list[dict]:
        enriched: list[dict] = []
        for paper in papers:
            analysis = await self.analyze_paper(query=query, paper=paper)
            item = dict(paper)
            item.update(analysis)
            enriched.append(item)
        return enriched

    async def analyze_paper(self, query: str, paper: dict) -> dict:
        fallback = self._fallback_analysis(paper)
        if not self.client.is_available:
            return fallback

        system_prompt = (
            "You are an ML paper analyst. Return strict JSON with keys: "
            "summary_3_lines, method_highlights, limitations, reproduction_difficulty, code_repo_url. "
            "Use concise plain text. reproduction_difficulty must be one of: low, medium, high."
        )
        user_prompt = (
            f"User intent: {query}\n"
            f"Title: {paper.get('title', '')}\n"
            f"Summary: {paper.get('summary', '')}\n"
            f"Authors: {', '.join(paper.get('authors', []))}\n"
            f"Categories: {', '.join(paper.get('categories', []))}\n"
            "If code repository is unknown, use empty string."
        )

        try:
            raw = await self.client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
            parsed = self._parse_json(raw)
            if not parsed:
                return fallback
            return {
                "ai_summary_3lines": parsed.get("summary_3_lines") or fallback["ai_summary_3lines"],
                "method_highlights": parsed.get("method_highlights") or fallback["method_highlights"],
                "limitations": parsed.get("limitations") or fallback["limitations"],
                "reproduction_difficulty": self._normalize_difficulty(
                    parsed.get("reproduction_difficulty", fallback["reproduction_difficulty"])
                ),
                "code_repo_url": parsed.get("code_repo_url") or fallback["code_repo_url"],
            }
        except Exception as exc:  # pragma: no cover - external provider failures vary by env
            logger.warning("ArXiv paper analysis failed: %s", exc)
            return fallback

    def _fallback_analysis(self, paper: dict) -> dict:
        summary = paper.get("summary", "")
        lines = self._three_line_summary(summary)
        code_url = self._extract_github_url(summary)
        return {
            "ai_summary_3lines": lines,
            "method_highlights": self._method_highlights(summary),
            "limitations": self._limitations(summary),
            "reproduction_difficulty": self._estimate_repro_difficulty(summary),
            "code_repo_url": code_url,
        }

    def _parse_json(self, raw: str) -> dict:
        text = raw.strip()
        if not text:
            return {}
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        try:
            payload = json.loads(text)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            return {}
        return {}

    def _three_line_summary(self, summary: str) -> str:
        clean = " ".join(summary.split())
        if not clean:
            return "No abstract available.\nNo abstract available.\nNo abstract available."

        chunks = re.split(r"(?<=[.!?])\s+", clean)
        selected = [chunk.strip() for chunk in chunks if chunk.strip()][:3]
        while len(selected) < 3:
            selected.append(selected[-1] if selected else "No abstract available.")
        return "\n".join(selected)

    def _method_highlights(self, summary: str) -> str:
        lowered = summary.lower()
        keywords = ["transformer", "diffusion", "contrastive", "rlhf", "retrieval", "benchmark"]
        found = [key for key in keywords if key in lowered]
        if found:
            return "Core methods: " + ", ".join(found[:3]) + "."
        return "Core method is not explicit from abstract-only evidence."

    def _limitations(self, summary: str) -> str:
        lowered = summary.lower()
        cues = ["however", "but", "limitation", "future work", "challenging"]
        if any(cue in lowered for cue in cues):
            return "Authors indicate constraints or open problems in the abstract."
        return "No explicit limitation sentence detected in abstract."

    def _estimate_repro_difficulty(self, summary: str) -> str:
        lowered = summary.lower()
        high = ["large-scale", "billion", "cluster", "proprietary", "human preference"]
        low = ["simple baseline", "small-scale", "toy dataset", "lightweight"]
        if any(token in lowered for token in high):
            return "high"
        if any(token in lowered for token in low):
            return "low"
        return "medium"

    def _extract_github_url(self, text: str) -> str:
        match = re.search(r"https?://github\.com/[^\s)]+", text)
        return match.group(0).rstrip(".,)") if match else ""

    def _normalize_difficulty(self, value: str) -> str:
        lowered = (value or "").strip().lower()
        if lowered in {"low", "medium", "high"}:
            return lowered
        return "medium"
