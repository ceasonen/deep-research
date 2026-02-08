"""Optional lightweight reranker based on sentence-transformers cross-encoder."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScoredText:
    score: float
    payload: dict


class Reranker:
    """Lazy-loading reranker with graceful fallback when dependency is missing."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = None
        self.is_loaded = False

    def load(self) -> bool:
        if not self.settings.reranker_enabled:
            logger.info("Reranker disabled by configuration")
            return False

        if self.is_loaded:
            return True

        try:
            from sentence_transformers import CrossEncoder
        except ImportError:
            logger.warning("sentence-transformers not installed; reranking disabled")
            return False

        try:
            self.model = CrossEncoder(self.settings.reranker_model, max_length=512, device="cpu")
            self.is_loaded = True
            logger.info("Reranker loaded: %s", self.settings.reranker_model)
            return True
        except Exception as exc:  # pragma: no cover - model download failures are environment-specific
            logger.warning("Failed to load reranker model: %s", exc)
            return False

    def rerank(self, query: str, items: Iterable[dict], top_k: int | None = None) -> list[dict]:
        candidates = list(items)
        if not candidates:
            return []

        limit = top_k or self.settings.reranker_top_k
        if not self.load() or self.model is None:
            return candidates[:limit]

        pairs = [(query, f"{item.get('title', '')}\n{item.get('content') or item.get('snippet', '')}") for item in candidates]
        scores = self.model.predict(pairs)

        ranked: list[ScoredText] = []
        for payload, score in zip(candidates, scores):
            normalized_score = float(score)
            if not math.isfinite(normalized_score):
                normalized_score = 0.0
            ranked.append(ScoredText(score=normalized_score, payload=payload))
        ranked.sort(key=lambda item: item.score, reverse=True)

        output: list[dict] = []
        for item in ranked[:limit]:
            payload = dict(item.payload)
            payload["relevance_score"] = item.score
            output.append(payload)
        return output
