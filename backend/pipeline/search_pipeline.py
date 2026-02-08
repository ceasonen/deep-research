"""Core search pipeline: search -> fetch -> extract -> rerank -> synthesize."""

from __future__ import annotations

import json
import math
import time
from collections.abc import AsyncGenerator

from backend.arxiv import ArxivClient, ArxivPaperAnalyzer
from backend.config import get_settings
from backend.content.extractor import ContentExtractor
from backend.content.fetcher import ContentFetcher
from backend.llm.synthesizer import AnswerSynthesizer
from backend.models.reranker import Reranker
from backend.models.schemas import SearchMode, SearchRequest
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
        self.arxiv_client = ArxivClient()
        self.paper_analyzer = ArxivPaperAnalyzer()
        self.cache = TTLCache(
            ttl_seconds=self.settings.cache_ttl,
            max_size=self.settings.cache_max_size,
        )

    async def _retrieve(self, request: SearchRequest) -> list[dict]:
        if request.mode == SearchMode.ARXIV:
            return await self._retrieve_arxiv(request)

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

    async def _retrieve_arxiv(self, request: SearchRequest) -> list[dict]:
        target_size = min(
            self.settings.arxiv_max_results,
            max(request.max_sources * 2, request.max_sources),
        )
        papers = await self.arxiv_client.search(
            query=request.query,
            max_results=target_size,
            categories=self.settings.arxiv_categories,
        )
        ranked = self.arxiv_client.rank_papers(papers, query=request.query)
        analyzed = await self.paper_analyzer.analyze_many(
            papers=ranked[: request.max_sources],
            query=request.query,
        )
        return [self._paper_to_source(paper) for paper in analyzed]

    def _paper_to_source(self, paper: dict) -> dict:
        return {
            "title": paper.get("title", "Untitled"),
            "url": paper.get("url", ""),
            "snippet": paper.get("summary", ""),
            "content": paper.get("summary", ""),
            "source_engine": "arxiv",
            "published_date": paper.get("published_date"),
            "relevance_score": paper.get("relevance_score", 0.0),
            "arxiv_id": paper.get("arxiv_id"),
            "pdf_url": paper.get("pdf_url"),
            "authors": paper.get("authors", []),
            "categories": paper.get("categories", []),
            "ai_summary_3lines": paper.get("ai_summary_3lines"),
            "method_highlights": paper.get("method_highlights"),
            "limitations": paper.get("limitations"),
            "reproduction_difficulty": paper.get("reproduction_difficulty"),
            "code_repo_url": paper.get("code_repo_url"),
        }

    def _related_queries(self, query: str, mode: SearchMode) -> list[str]:
        if mode == SearchMode.ARXIV:
            return [
                f"{query} in cs.LG",
                f"{query} in cs.CL",
                f"{query} in stat.ML",
            ]
        return [
            f"latest updates about {query}",
            f"expert analysis on {query}",
            f"pros and cons of {query}",
        ]

    async def _build_answer(self, request: SearchRequest, sources: list[dict]) -> str:
        if request.mode != SearchMode.ARXIV:
            return await self.synthesizer.generate(
                query=request.query,
                sources=sources,
                language=request.language,
            )

        if self.synthesizer.client.is_available:
            return await self.synthesizer.generate(
                query=f"Summarize latest arXiv papers about: {request.query}",
                sources=sources,
                language=request.language,
            )
        return self._arxiv_fallback_answer(sources)

    async def _stream_answer(
        self, request: SearchRequest, sources: list[dict]
    ) -> AsyncGenerator[str, None]:
        if request.mode != SearchMode.ARXIV or self.synthesizer.client.is_available:
            async for chunk in self.synthesizer.stream(
                query=request.query,
                sources=sources,
                language=request.language,
            ):
                yield chunk
            return

        yield self._arxiv_fallback_answer(sources)

    def _arxiv_fallback_answer(self, sources: list[dict]) -> str:
        if not sources:
            return "No recent arXiv papers were found for this topic."

        lines = ["## ArXiv Radar", ""]
        for index, source in enumerate(sources[:5], start=1):
            method = source.get("method_highlights") or "Method highlights unavailable."
            limits = source.get("limitations") or "Limitations not stated."
            lines.append(f"{index}. **{source.get('title', 'Untitled')}** [{index}]")
            lines.append(f"- Method: {method}")
            lines.append(f"- Limits: {limits}")
        return "\n".join(lines)

    async def search_sync(self, request: SearchRequest) -> dict:
        cache_key = f"{request.query}:{request.mode}:{request.max_sources}:{request.language}"
        if self.settings.cache_enabled:
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        start = time.perf_counter()
        sources = await self._retrieve(request)
        answer = await self._build_answer(request=request, sources=sources)
        elapsed = time.perf_counter() - start

        response = {
            "query": request.query,
            "answer": answer,
            "sources": self._sanitize_sources(sources),
            "related_queries": self._related_queries(request.query, request.mode),
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
            safe_sources = self._sanitize_sources(sources)
            yield to_sse("sources", {"items": safe_sources})
            yield to_sse("answer_start", {"status": "streaming"})

            answer_parts: list[str] = []
            async for chunk in self._stream_answer(request=request, sources=sources):
                answer_parts.append(chunk)
                yield to_sse("answer_chunk", {"chunk": chunk})

            elapsed = time.perf_counter() - start
            payload = {
                "query": request.query,
                "answer": "".join(answer_parts),
                "sources": safe_sources,
                "related_queries": self._related_queries(request.query, request.mode),
                "search_time": round(elapsed, 3),
                "model_used": self.settings.llm_model,
            }
            yield to_sse("answer_end", payload)
        except Exception as exc:
            yield to_sse("error", {"message": str(exc)})

    def _sanitize_sources(self, sources: list[dict]) -> list[dict]:
        cleaned: list[dict] = []
        for source in sources:
            item = dict(source)
            score = item.get("relevance_score")
            if isinstance(score, float) and not math.isfinite(score):
                item["relevance_score"] = 0.0
            cleaned.append(item)
        return cleaned
