from backend.search.aggregator import SearchAggregator


def test_dedupe_and_score_merges_same_url():
    aggregator = SearchAggregator()
    items = [
        {"title": "A", "url": "https://example.com/a", "snippet": "short", "source_engine": "duckduckgo"},
        {
            "title": "A2",
            "url": "https://example.com/a",
            "snippet": "this is a longer snippet",
            "source_engine": "google",
        },
        {"title": "B", "url": "https://example.com/b", "snippet": "another", "source_engine": "duckduckgo"},
    ]

    merged = aggregator._dedupe_and_score(items)
    assert len(merged) == 2
    assert merged[0]["url"] == "https://example.com/a"
    assert merged[0]["snippet"] == "this is a longer snippet"
