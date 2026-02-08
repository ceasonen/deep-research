import pytest

from backend.models.schemas import SearchRequest
from backend.pipeline.search_pipeline import SearchPipeline


@pytest.mark.asyncio
async def test_search_sync_returns_shape(monkeypatch):
    pipeline = SearchPipeline()

    async def fake_retrieve(_request):
        return [
            {
                "title": "Example",
                "url": "https://example.com",
                "snippet": "Example snippet",
                "content": "Example content",
                "source_engine": "duckduckgo",
            }
        ]

    async def fake_generate(**_kwargs):
        return "Example answer [1]"

    monkeypatch.setattr(pipeline, "_retrieve", fake_retrieve)
    monkeypatch.setattr(pipeline.synthesizer, "generate", fake_generate)

    request = SearchRequest(query="What is FastAPI?", stream=False)
    result = await pipeline.search_sync(request)

    assert result["query"] == "What is FastAPI?"
    assert "answer" in result
    assert len(result["sources"]) == 1
    assert result["search_time"] >= 0


@pytest.mark.asyncio
async def test_search_stream_emits_events(monkeypatch):
    pipeline = SearchPipeline()

    async def fake_retrieve(_request):
        return [{"title": "A", "url": "https://a.com", "snippet": "x"}]

    async def fake_stream(**_kwargs):
        yield "Part1"
        yield "Part2"

    monkeypatch.setattr(pipeline, "_retrieve", fake_retrieve)
    monkeypatch.setattr(pipeline.synthesizer, "stream", fake_stream)

    request = SearchRequest(query="hello", stream=True)
    events = [event async for event in pipeline.search_stream(request)]

    assert any("event: sources" in event for event in events)
    assert any("event: answer_chunk" in event for event in events)
    assert any("event: answer_end" in event for event in events)


def test_sanitize_sources_normalizes_nan_score():
    pipeline = SearchPipeline()
    cleaned = pipeline._sanitize_sources(
        [
            {"title": "A", "url": "https://a.com", "snippet": "x", "relevance_score": float("nan")},
            {"title": "B", "url": "https://b.com", "snippet": "y", "relevance_score": float("inf")},
        ]
    )

    assert cleaned[0]["relevance_score"] == 0.0
    assert cleaned[1]["relevance_score"] == 0.0
