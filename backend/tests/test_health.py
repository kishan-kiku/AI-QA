from fastapi.testclient import TestClient

from app.main import app


def test_health_does_not_need_a_model() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["phase"] == 2
