"""Brave Search API adapter."""

from __future__ import annotations

import aiohttp

from backend.config import get_settings
from backend.search.base import BaseSearchEngine
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class BraveSearchEngine(BaseSearchEngine):
    name = "brave"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def search(self, query: str, max_results: int = 8) -> list[dict]:
        if not self.settings.brave_api_key:
            return []

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.settings.brave_api_key,
        }
        params = {"q": query, "count": max_results}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params=params,
                    timeout=12,
                ) as response:
                    if response.status != 200:
                        return []
                    data = await response.json()
        except Exception as exc:  # pragma: no cover
            logger.warning("Brave search failed: %s", exc)
            return []

        rows = data.get("web", {}).get("results", [])
        return [
            {
                "title": row.get("title", "Untitled"),
                "url": row.get("url", ""),
                "snippet": row.get("description", ""),
                "source_engine": self.name,
            }
            for row in rows
            if row.get("url")
        ]
