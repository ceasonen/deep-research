"""DuckDuckGo free search adapter."""

from __future__ import annotations

from backend.search.base import BaseSearchEngine
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class DuckDuckGoSearchEngine(BaseSearchEngine):
    name = "duckduckgo"

    async def search(self, query: str, max_results: int = 8) -> list[dict]:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            logger.warning("duckduckgo-search dependency missing")
            return []

        try:
            with DDGS() as ddgs:
                rows = list(ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": row.get("title") or "Untitled",
                    "url": row.get("href") or "",
                    "snippet": row.get("body") or "",
                    "source_engine": self.name,
                }
                for row in rows
                if row.get("href")
            ]
        except Exception as exc:  # pragma: no cover
            logger.warning("DuckDuckGo search failed: %s", exc)
            return []
