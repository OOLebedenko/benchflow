from fastapi.testclient import TestClient

from benchflow.main import app

client = TestClient(app)


def test_health() -> None:
    """Return successful health status."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
