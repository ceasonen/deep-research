"""Bing Web Search API adapter."""

from __future__ import annotations

import aiohttp

from backend.config import get_settings
from backend.search.base import BaseSearchEngine
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class BingSearchEngine(BaseSearchEngine):
    name = "bing"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def search(self, query: str, max_results: int = 8) -> list[dict]:
        if not self.settings.bing_api_key:
            return []

        headers = {"Ocp-Apim-Subscription-Key": self.settings.bing_api_key}
        params = {"q": query, "count": max_results, "mkt": "en-US"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.bing.microsoft.com/v7.0/search",
                    headers=headers,
                    params=params,
                    timeout=12,
                ) as response:
                    if response.status != 200:
                        return []
                    data = await response.json()
        except Exception as exc:  # pragma: no cover
            logger.warning("Bing search failed: %s", exc)
            return []

        rows = data.get("webPages", {}).get("value", [])
        return [
            {
                "title": row.get("name", "Untitled"),
                "url": row.get("url", ""),
                "snippet": row.get("snippet", ""),
                "source_engine": self.name,
            }
            for row in rows
            if row.get("url")
        ]
