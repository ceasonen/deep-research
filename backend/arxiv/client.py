"""ArXiv API client with conservative rate limiting and ranking."""

from __future__ import annotations

import asyncio
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import aiohttp

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._request_lock = asyncio.Lock()
        self._last_request_ts = 0.0

    async def search(
        self,
        query: str,
        max_results: int = 12,
        categories: list[str] | None = None,
    ) -> list[dict]:
        allowed_categories = categories or self.settings.arxiv_categories
        request_count = max(1, min(max_results, self.settings.arxiv_max_results))
        search_query = self._build_query(query, allowed_categories)
        encoded_query = urllib.parse.quote_plus(search_query)
        url = (
            f"{self.settings.arxiv_base_url}?search_query={encoded_query}"
            f"&start=0&max_results={request_count}&sortBy=submittedDate&sortOrder=descending"
        )

        xml_text = await self._fetch(url)
        return self._parse_feed(xml_text)

    def rank_papers(self, papers: list[dict], query: str) -> list[dict]:
        query_tokens = self._tokenize(query)

        scored: list[dict] = []
        for item in papers:
            score = self._score(item, query_tokens)
            enriched = dict(item)
            enriched["relevance_score"] = round(score, 4)
            scored.append(enriched)

        scored.sort(key=lambda paper: paper.get("relevance_score", 0.0), reverse=True)
        return scored

    def _build_query(self, query: str, categories: list[str]) -> str:
        category_expr = " OR ".join(f"cat:{item}" for item in categories if item)
        if not category_expr:
            category_expr = "cat:cs.AI"

        stripped_query = query.strip()
        if stripped_query:
            return f"(all:{stripped_query}) AND ({category_expr})"
        return f"({category_expr})"

    async def _fetch(self, url: str) -> str:
        timeout = aiohttp.ClientTimeout(total=20)
        connector = aiohttp.TCPConnector(limit=1, ssl=False)

        async with self._request_lock:
            elapsed = time.monotonic() - self._last_request_ts
            wait_seconds = self.settings.arxiv_min_interval_seconds - elapsed
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(url, headers={"User-Agent": "AutoSearch-AI/0.1"}) as response:
                    response.raise_for_status()
                    text = await response.text()
                    self._last_request_ts = time.monotonic()
                    return text

    def _parse_feed(self, xml_text: str) -> list[dict]:
        root = ET.fromstring(xml_text)
        entries: list[dict] = []

        for entry in root.findall("atom:entry", ATOM_NS):
            id_url = (entry.findtext("atom:id", default="", namespaces=ATOM_NS) or "").strip()
            arxiv_id = id_url.rsplit("/", 1)[-1] if id_url else ""
            title = self._normalize_whitespace(
                entry.findtext("atom:title", default="", namespaces=ATOM_NS) or ""
            )
            summary = self._normalize_whitespace(
                entry.findtext("atom:summary", default="", namespaces=ATOM_NS) or ""
            )
            published = (entry.findtext("atom:published", default="", namespaces=ATOM_NS) or "").strip()
            updated = (entry.findtext("atom:updated", default="", namespaces=ATOM_NS) or "").strip()
            comment = self._normalize_whitespace(
                entry.findtext("arxiv:comment", default="", namespaces=ATOM_NS) or ""
            )
            comment = comment or None

            authors = []
            for author in entry.findall("atom:author", ATOM_NS):
                name = (author.findtext("atom:name", default="", namespaces=ATOM_NS) or "").strip()
                if name:
                    authors.append(name)

            categories = []
            for category in entry.findall("atom:category", ATOM_NS):
                term = category.attrib.get("term", "").strip()
                if term:
                    categories.append(term)

            primary_category = ""
            primary_tag = entry.find("arxiv:primary_category", ATOM_NS)
            if primary_tag is not None:
                primary_category = primary_tag.attrib.get("term", "").strip()

            pdf_url = ""
            for link in entry.findall("atom:link", ATOM_NS):
                href = link.attrib.get("href", "").strip()
                link_type = link.attrib.get("type", "").strip()
                link_title = link.attrib.get("title", "").strip().lower()
                if not href:
                    continue
                if link_type == "application/pdf" or link_title == "pdf":
                    pdf_url = href
                    break

            if not pdf_url and arxiv_id:
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            entries.append(
                {
                    "arxiv_id": arxiv_id,
                    "title": title or "Untitled",
                    "url": id_url or f"https://arxiv.org/abs/{arxiv_id}",
                    "pdf_url": pdf_url,
                    "summary": summary,
                    "published_date": published,
                    "updated_date": updated,
                    "authors": authors,
                    "categories": categories,
                    "primary_category": primary_category,
                    "comment": comment,
                }
            )

        return entries

    def _score(self, paper: dict, query_tokens: set[str]) -> float:
        title = paper.get("title", "").lower()
        summary = paper.get("summary", "").lower()
        categories = " ".join(paper.get("categories", [])).lower()
        score = 0.0

        for token in query_tokens:
            if token in title:
                score += 2.0
            if token in summary:
                score += 1.0
            if token in categories:
                score += 0.5

        published = paper.get("published_date", "")
        score += self._recency_score(published)
        return score

    def _recency_score(self, published_date: str) -> float:
        if not published_date:
            return 0.0
        try:
            published = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
        except ValueError:
            return 0.0

        now = datetime.now(timezone.utc)
        age_days = max(0.0, (now - published).total_seconds() / 86400)
        # New papers get a small boost without overwhelming relevance score.
        return max(0.0, 2.0 - (age_days / 30.0))

    def _tokenize(self, text: str) -> set[str]:
        tokens = re.findall(r"[a-zA-Z0-9]{3,}", text.lower())
        return set(tokens)

    def _normalize_whitespace(self, text: str) -> str:
        return " ".join(text.split())
