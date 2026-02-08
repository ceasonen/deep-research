"""Pydantic schemas for request and response payloads."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SearchMode(str, Enum):
    QUICK = "quick"
    DEEP = "deep"
    ACADEMIC = "academic"


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    mode: SearchMode = SearchMode.QUICK
    max_sources: int = Field(default=6, ge=1, le=20)
    language: str = "en"
    stream: bool = True


class SearchSource(BaseModel):
    title: str
    url: str
    snippet: str
    content: str | None = None
    relevance_score: float | None = None
    source_engine: str = "unknown"
    favicon_url: str | None = None
    published_date: str | None = None


class SearchResponse(BaseModel):
    query: str
    answer: str
    sources: list[SearchSource]
    related_queries: list[str] = Field(default_factory=list)
    search_time: float
    model_used: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StreamEvent(BaseModel):
    event: str
    data: Any


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    llm_connected: bool
    reranker_loaded: bool
    search_engines: list[str]
