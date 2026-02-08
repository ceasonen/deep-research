import pytest

from backend.models.schemas import SearchMode, SearchRequest
from backend.pipeline.search_pipeline import SearchPipeline


@pytest.mark.asyncio
async def test_arxiv_mode_uses_arxiv_path(monkeypatch):
    pipeline = SearchPipeline()

    async def fake_retrieve_arxiv(_request):
        return [
            {
                "title": "Paper A",
                "url": "https://arxiv.org/abs/1234.5678",
                "snippet": "Abstract",
                "source_engine": "arxiv",
                "pdf_url": "https://arxiv.org/pdf/1234.5678.pdf",
                "relevance_score": 2.5,
            }
        ]

    async def fake_build_answer(*, request, sources):
        _ = request, sources
        return "ArXiv answer [1]"

    monkeypatch.setattr(pipeline, "_retrieve_arxiv", fake_retrieve_arxiv)
    monkeypatch.setattr(pipeline, "_build_answer", fake_build_answer)

    request = SearchRequest(query="test", mode=SearchMode.ARXIV, stream=False)
    result = await pipeline.search_sync(request)

    assert result["answer"] == "ArXiv answer [1]"
    assert result["sources"][0]["source_engine"] == "arxiv"
    assert any("cs.LG" in item for item in result["related_queries"])


def test_paper_to_source_mapping_contains_arxiv_fields():
    pipeline = SearchPipeline()
    source = pipeline._paper_to_source(
        {
            "title": "Paper B",
            "url": "https://arxiv.org/abs/9876.5432",
            "summary": "hello",
            "arxiv_id": "9876.5432",
            "pdf_url": "https://arxiv.org/pdf/9876.5432.pdf",
            "authors": ["A", "B"],
            "categories": ["cs.LG"],
            "ai_summary_3lines": "line1\nline2\nline3",
            "method_highlights": "transformer",
            "limitations": "data limited",
            "reproduction_difficulty": "medium",
            "code_repo_url": "https://github.com/example/repo",
        }
    )

    assert source["arxiv_id"] == "9876.5432"
    assert source["pdf_url"].endswith(".pdf")
    assert source["authors"] == ["A", "B"]
