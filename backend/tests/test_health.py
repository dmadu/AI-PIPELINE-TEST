"""Tests for the ``/api/v1/health`` endpoint and its success envelope."""

HEALTH_URL = "/api/v1/health"


def test_health_endpoint_returns_http_200_json(client):
    response = client.get(HEALTH_URL)

    assert response.status_code == 200
    assert response.content_type.startswith("application/json")


def test_health_endpoint_returns_success_envelope(client):
    response = client.get(HEALTH_URL)
    payload = response.get_json()

    assert isinstance(payload, dict)
    assert list(payload.keys()) == ["data"]

    data = payload["data"]
    assert isinstance(data, dict)
    assert data, "health payload should not be empty"
    assert "status" in data
    assert isinstance(data["status"], str)
    assert data["status"]
