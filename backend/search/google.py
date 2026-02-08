"""Google Custom Search API adapter."""

from __future__ import annotations

import aiohttp

from backend.config import get_settings
from backend.search.base import BaseSearchEngine
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleSearchEngine(BaseSearchEngine):
    name = "google"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def search(self, query: str, max_results: int = 8) -> list[dict]:
        if not self.settings.google_api_key or not self.settings.google_cx_id:
            return []

        params = {
            "key": self.settings.google_api_key,
            "cx": self.settings.google_cx_id,
            "q": query,
            "num": min(max_results, 10),
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://www.googleapis.com/customsearch/v1", params=params, timeout=12
                ) as response:
                    if response.status != 200:
                        return []
                    data = await response.json()
        except Exception as exc:  # pragma: no cover
            logger.warning("Google search failed: %s", exc)
            return []

        results: list[dict] = []
        for item in data.get("items", []):
            link = item.get("link")
            if not link:
                continue
            results.append(
                {
                    "title": item.get("title", "Untitled"),
                    "url": link,
                    "snippet": item.get("snippet", ""),
                    "source_engine": self.name,
                }
            )
        return results
