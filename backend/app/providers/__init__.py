from app.config import Settings
from app.providers.base import LLMProvider
from app.providers.fake import FakeProvider
from app.providers.gemini import GeminiProvider


def build_provider(settings: Settings) -> LLMProvider:
    name = settings.ai_qa_provider.strip().lower()
    if name == "fake":
        return FakeProvider()
    if name == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)
    raise RuntimeError(f"Unknown AI_QA_PROVIDER '{settings.ai_qa_provider}'. Use gemini or fake.")
