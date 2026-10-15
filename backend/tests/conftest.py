import pytest
from fastapi.testclient import TestClient

from app.ai_service import AIService
from app.main import app, get_ai_service
from app.providers.fake import FakeProvider


@pytest.fixture
def fake_service() -> AIService:
    return AIService(FakeProvider())


@pytest.fixture
def client(fake_service: AIService) -> TestClient:
    app.dependency_overrides[get_ai_service] = lambda: fake_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
