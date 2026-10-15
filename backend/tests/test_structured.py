import json

from fastapi.testclient import TestClient

from app.ai_service import AIService
from app.main import app, get_ai_service
from app.providers.fake import FakeProvider

FEATURE = "Create test cases for a policy cancellation feature."

POSITIVE_SCENARIO = {
    "id": "SC-01",
    "title": "Cancel active policy",
    "description": "Happy path mid-term cancel",
    "type": "positive",
}


def test_scenarios_returns_only_requested_types(client: TestClient) -> None:
    response = client.post(
        "/api/v1/generate/scenarios",
        json={
            "feature_description": FEATURE,
            "scenario_types": ["negative", "boundary"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    types = {item["type"] for item in body["scenarios"]}
    assert types <= {"negative", "boundary"}
    assert "test_cases" not in body


def test_scenarios_rejects_empty_types(client: TestClient) -> None:
    response = client.post(
        "/api/v1/generate/scenarios",
        json={"feature_description": FEATURE, "scenario_types": []},
    )
    assert response.status_code == 422


def test_scenarios_returns_502_for_unrequested_type() -> None:
    leaked = {
        "summary": "Leaked type",
        "assumptions": [],
        "scenarios": [
            {
                "id": "SC-01",
                "title": "Cancel active policy",
                "description": "Should not appear when only negative was asked",
                "type": "positive",
            }
        ],
    }
    service = AIService(FakeProvider(raw_json=json.dumps(leaked)))
    app.dependency_overrides[get_ai_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/generate/scenarios",
                json={
                    "feature_description": FEATURE,
                    "scenario_types": ["negative"],
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert "not requested" in response.json()["detail"]


def test_cases_expand_selected_scenarios(client: TestClient) -> None:
    response = client.post(
        "/api/v1/generate/cases",
        json={"feature_description": FEATURE, "scenarios": [POSITIVE_SCENARIO]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["test_cases"]
    assert all(case["scenario_id"] == "SC-01" for case in body["test_cases"])


def test_cases_return_502_when_a_selected_scenario_is_missing() -> None:
    incomplete = {
        "test_cases": [
            {
                "id": "TC-01",
                "scenario_id": "SC-01",
                "title": "Only one of two",
                "preconditions": ["Policy exists"],
                "steps": ["Cancel"],
                "expected_result": "Cancelled",
            }
        ]
    }
    service = AIService(FakeProvider(raw_json=json.dumps(incomplete)))
    app.dependency_overrides[get_ai_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/generate/cases",
                json={
                    "feature_description": FEATURE,
                    "scenarios": [
                        POSITIVE_SCENARIO,
                        {
                            "id": "SC-02",
                            "title": "Expired policy",
                            "description": "Reject cancel",
                            "type": "negative",
                        },
                    ],
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert "every selected scenario" in response.json()["detail"]


def test_full_pack_respects_type_filter(client: TestClient) -> None:
    response = client.post(
        "/api/v1/generate",
        json={"feature_description": FEATURE, "scenario_types": ["positive"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert {item["type"] for item in body["scenarios"]} == {"positive"}
    scenario_ids = {item["id"] for item in body["scenarios"]}
    assert all(case["scenario_id"] in scenario_ids for case in body["test_cases"])
