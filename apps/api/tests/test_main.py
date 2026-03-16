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


def test_similar_tickets_endpoint_uses_provider() -> None:
    response = client.post("/api/similar-tickets", json={"query": "login"})

    assert response.status_code == 200
    body = response.json()
    assert "tickets" in body
    assert len(body["tickets"]) >= 1


def test_search_tickets_endpoint() -> None:
    response = client.post("/api/tickets/search", json={"query": "otp"})

    assert response.status_code == 200
    body = response.json()
    assert "tickets" in body
    assert all("ticketId" in ticket for ticket in body["tickets"])


def test_get_ticket_details_endpoint() -> None:
    response = client.get("/api/tickets/TCK-4387")

    assert response.status_code == 200
    body = response.json()
    assert body["ticket"]["ticketId"] == "TCK-4387"


def test_get_ticket_details_not_found_returns_structured_error() -> None:
    response = client.get("/api/tickets/UNKNOWN")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["code"] == "TICKET_NOT_FOUND"
    assert body["detail"]["details"]["ticketId"] == "UNKNOWN"
