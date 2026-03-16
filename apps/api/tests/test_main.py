from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_answer_endpoint_returns_sources() -> None:
    response = client.post("/api/answer", json={"question": "How do I reset MFA?"})
    body = response.json()

    assert response.status_code == 200
    assert "answer" in body
    assert len(body["sources"]) >= 1
