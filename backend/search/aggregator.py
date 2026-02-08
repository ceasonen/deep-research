"""Concurrent multi-engine search aggregation."""

from __future__ import annotations

import asyncio
from collections import defaultdict

from backend.config import get_settings
from backend.search.base import BaseSearchEngine
from backend.search.bing import BingSearchEngine
from backend.search.brave import BraveSearchEngine
from backend.search.duckduckgo import DuckDuckGoSearchEngine
from backend.search.google import GoogleSearchEngine
from backend.utils.logger import get_logger

logger = get_logger(__name__)


ENGINE_REGISTRY: dict[str, type[BaseSearchEngine]] = {
    "duckduckgo": DuckDuckGoSearchEngine,
    "google": GoogleSearchEngine,
    "bing": BingSearchEngine,
    "brave": BraveSearchEngine,
}


class SearchAggregator:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.engines: list[BaseSearchEngine] = []

        names = self.settings.search_engines or ["duckduckgo"]
        for name in names:
            cls = ENGINE_REGISTRY.get(name)
            if cls is None:
                continue
            self.engines.append(cls())

        if not self.engines:
            self.engines = [DuckDuckGoSearchEngine()]

    async def search(self, query: str, max_results: int = 8) -> list[dict]:
        tasks = [engine.search(query, max_results=max_results) for engine in self.engines]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        merged: list[dict] = []
        for response in responses:
            if isinstance(response, Exception):
                logger.warning("One engine failed: %s", response)
                continue
            merged.extend(response)

        deduped = self._dedupe_and_score(merged)
        return deduped[:max_results]

    def _dedupe_and_score(self, items: list[dict]) -> list[dict]:
        by_url: dict[str, dict] = {}
        support_count: defaultdict[str, int] = defaultdict(int)

        for item in items:
            url = item.get("url", "").strip()
            if not url:
                continue
            support_count[url] += 1

            if url not in by_url:
                by_url[url] = dict(item)
            elif len(item.get("snippet", "")) > len(by_url[url].get("snippet", "")):
                by_url[url]["snippet"] = item.get("snippet", "")

        results = []
        for url, item in by_url.items():
            score = float(support_count[url])
            item["relevance_score"] = score
            results.append(item)

        results.sort(key=lambda entry: entry.get("relevance_score", 0), reverse=True)
        return results
