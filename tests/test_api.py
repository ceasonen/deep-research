from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "version" in payload


def test_search_empty_query_validation():
    response = client.post(
        "/api/search",
        json={"query": "", "mode": "quick", "max_sources": 3, "language": "en", "stream": False},
    )
    assert response.status_code == 422
