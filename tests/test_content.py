from backend.content.extractor import ContentExtractor


def test_extractor_returns_clean_text():
    extractor = ContentExtractor()
    html = """
    <html><head><title>t</title><script>ignore()</script></head>
    <body><nav>menu</nav><main><h1>Hello</h1><p>World</p></main></body></html>
    """

    text = extractor.extract(html)
    assert "Hello" in text
    assert "World" in text
    assert "ignore" not in text
