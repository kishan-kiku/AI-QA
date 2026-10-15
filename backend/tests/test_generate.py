import json

from fastapi.testclient import TestClient

from app.ai_service import AIService
from app.main import app, get_ai_service
from app.providers.fake import FakeProvider


def test_generate_rejects_short_description(client: TestClient) -> None:
    response = client.post("/api/v1/generate", json={"feature_description": "cancel"})
    assert response.status_code == 422


def test_generate_returns_structured_pack(client: TestClient) -> None:
    response = client.post(
        "/api/v1/generate",
        json={
            "feature_description": "Create test cases for a policy cancellation feature."
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["model"] == "fake-model"
    assert "human validation" in body["disclaimer"]
    assert len(body["scenarios"]) >= 1
    assert len(body["test_cases"]) >= 1
    scenario_ids = {item["id"] for item in body["scenarios"]}
    for case in body["test_cases"]:
        assert case["scenario_id"] in scenario_ids


def test_generate_returns_502_when_model_returns_markdown() -> None:
    service = AIService(FakeProvider(raw_json="Here are some tests:\n1. Cancel policy"))
    app.dependency_overrides[get_ai_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/generate",
                json={"feature_description": "Create test cases for policy cancellation."},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert "JSON" in response.json()["detail"]


def test_generate_returns_502_when_scenario_ids_do_not_match() -> None:
    broken = {
        "summary": "Broken pack",
        "assumptions": [],
        "scenarios": [
            {
                "id": "SC-01",
                "title": "Cancel active policy",
                "description": "Happy path",
                "type": "positive",
            }
        ],
        "test_cases": [
            {
                "id": "TC-01",
                "scenario_id": "SC-99",
                "title": "Orphan case",
                "preconditions": ["Policy exists"],
                "steps": ["Cancel"],
                "expected_result": "Cancelled",
            }
        ],
    }
    service = AIService(FakeProvider(raw_json=json.dumps(broken)))
    app.dependency_overrides[get_ai_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/generate",
                json={"feature_description": "Create test cases for policy cancellation."},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert "scenario_id" in response.json()["detail"]
