"""Async webpage fetcher with timeout and user-agent defaults."""

from __future__ import annotations

import asyncio

import aiohttp

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ContentFetcher:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.timeout = aiohttp.ClientTimeout(total=self.settings.content_timeout)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }

    async def fetch(self, url: str) -> str | None:
        try:
            async with aiohttp.ClientSession(timeout=self.timeout, headers=self.headers) as session:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status >= 400:
                        return None
                    return await response.text(errors="ignore")
        except Exception as exc:  # pragma: no cover
            logger.debug("Fetch failed for %s: %s", url, exc)
            return None

    async def fetch_many(self, urls: list[str], limit: int | None = None) -> dict[str, str]:
        max_urls = limit or self.settings.content_max_pages
        selected = urls[:max_urls]

        semaphore = asyncio.Semaphore(6)

        async def bounded_fetch(target_url: str) -> tuple[str, str | None]:
            async with semaphore:
                html = await self.fetch(target_url)
                return target_url, html

        pairs = await asyncio.gather(*(bounded_fetch(url) for url in selected), return_exceptions=False)
        return {url: html for url, html in pairs if html}
