"""DuckDuckGo free search adapter via HTML endpoint.

This avoids low-level crashes observed with `duckduckgo_search`/`ddgs`
in some macOS environments.
"""

from __future__ import annotations

from urllib.parse import parse_qs, unquote, urlparse

import aiohttp
from bs4 import BeautifulSoup

from backend.search.base import BaseSearchEngine
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class DuckDuckGoSearchEngine(BaseSearchEngine):
    name = "duckduckgo"

    async def search(self, query: str, max_results: int = 8) -> list[dict]:
        try:
            async with aiohttp.ClientSession(
                headers={"User-Agent": "Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(total=12)
            ) as session:
                async with session.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                ) as response:
                    if response.status != 200:
                        return []
                    html = await response.text(errors="ignore")
        except Exception as exc:  # pragma: no cover
            logger.warning("DuckDuckGo request failed: %s", exc)
            return []

        soup = BeautifulSoup(html, "lxml")
        items: list[dict] = []
        for anchor in soup.select("a.result__a"):
            href = self._normalize_url(anchor.get("href", ""))
            if not href:
                continue

            title = anchor.get_text(" ", strip=True) or "Untitled"
            snippet = ""
            container = anchor.find_parent(class_="result")
            if container:
                snippet_tag = container.select_one(".result__snippet")
                if snippet_tag:
                    snippet = snippet_tag.get_text(" ", strip=True)

            items.append(
                {
                    "title": title,
                    "url": href,
                    "snippet": snippet,
                    "source_engine": self.name,
                }
            )

            if len(items) >= max_results:
                break

        return items

    def _normalize_url(self, href: str) -> str:
        if not href:
            return ""

        parsed = urlparse(href)
        if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
            target = parse_qs(parsed.query).get("uddg", [""])[0]
            return unquote(target)

        if href.startswith("//"):
            return f"https:{href}"

        return href
