"""Core search pipeline: search -> fetch -> extract -> rerank -> synthesize."""

from __future__ import annotations

import json
import time
from collections.abc import AsyncGenerator

from backend.config import get_settings
from backend.content.extractor import ContentExtractor
from backend.content.fetcher import ContentFetcher
from backend.llm.synthesizer import AnswerSynthesizer
from backend.models.reranker import Reranker
from backend.models.schemas import SearchRequest
from backend.search.aggregator import SearchAggregator
from backend.utils.cache import TTLCache


def to_sse(event: str, data: dict | str) -> str:
    payload = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data
    return f"event: {event}\ndata: {payload}\n\n"


class SearchPipeline:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.aggregator = SearchAggregator()
        self.fetcher = ContentFetcher()
        self.extractor = ContentExtractor()
        self.reranker = Reranker()
        self.synthesizer = AnswerSynthesizer()
        self.cache = TTLCache(
            ttl_seconds=self.settings.cache_ttl,
            max_size=self.settings.cache_max_size,
        )

    async def _retrieve(self, request: SearchRequest) -> list[dict]:
        raw = await self.aggregator.search(request.query, max_results=request.max_sources * 2)

        urls = [item.get("url", "") for item in raw if item.get("url")]
        html_map = await self.fetcher.fetch_many(urls, limit=request.max_sources)

        enriched: list[dict] = []
        for item in raw:
            url = item.get("url", "")
            html = html_map.get(url)
            if html:
                item["content"] = self.extractor.extract(html)
            enriched.append(item)

        if self.settings.reranker_enabled:
            reranked = self.reranker.rerank(request.query, enriched, top_k=request.max_sources)
            if reranked:
                return reranked

        return enriched[: request.max_sources]

    def _related_queries(self, query: str) -> list[str]:
        return [
            f"latest updates about {query}",
            f"expert analysis on {query}",
            f"pros and cons of {query}",
        ]

    async def search_sync(self, request: SearchRequest) -> dict:
        cache_key = f"{request.query}:{request.mode}:{request.max_sources}:{request.language}"
        if self.settings.cache_enabled:
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        start = time.perf_counter()
        sources = await self._retrieve(request)
        answer = await self.synthesizer.generate(
            query=request.query,
            sources=sources,
            language=request.language,
        )
        elapsed = time.perf_counter() - start

        response = {
            "query": request.query,
            "answer": answer,
            "sources": sources,
            "related_queries": self._related_queries(request.query),
            "search_time": round(elapsed, 3),
            "model_used": self.settings.llm_model,
        }

        if self.settings.cache_enabled:
            self.cache.set(cache_key, response)
        return response

    async def search_stream(self, request: SearchRequest) -> AsyncGenerator[str, None]:
        start = time.perf_counter()
        try:
            sources = await self._retrieve(request)
            yield to_sse("sources", {"items": sources})
            yield to_sse("answer_start", {"status": "streaming"})

            answer_parts: list[str] = []
            async for chunk in self.synthesizer.stream(
                query=request.query,
                sources=sources,
                language=request.language,
            ):
                answer_parts.append(chunk)
                yield to_sse("answer_chunk", {"chunk": chunk})

            elapsed = time.perf_counter() - start
            payload = {
                "query": request.query,
                "answer": "".join(answer_parts),
                "sources": sources,
                "related_queries": self._related_queries(request.query),
                "search_time": round(elapsed, 3),
                "model_used": self.settings.llm_model,
            }
            yield to_sse("answer_end", payload)
        except Exception as exc:
            yield to_sse("error", {"message": str(exc)})
