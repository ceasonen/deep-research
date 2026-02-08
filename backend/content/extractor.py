"""Robust content extraction: trafilatura first, then BeautifulSoup fallback."""

from __future__ import annotations

from bs4 import BeautifulSoup

from backend.config import get_settings


class ContentExtractor:
    def __init__(self) -> None:
        self.settings = get_settings()

    def extract(self, html: str) -> str:
        if not html:
            return ""

        text = ""
        try:
            import trafilatura

            text = trafilatura.extract(html, include_comments=False, include_tables=False) or ""
        except Exception:
            text = ""

        if not text:
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
                tag.decompose()
            text = " ".join(soup.get_text(separator=" ").split())

        return text[: self.settings.content_max_length]
