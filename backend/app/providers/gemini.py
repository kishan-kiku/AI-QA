from google import genai
from google.genai import types

from app.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, temperature: float = 0.3) -> None:
        if not api_key.strip():
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        self._model = model
        self._temperature = temperature
        self._client = genai.Client(api_key=api_key)

    @property
    def model_id(self) -> str:
        return self._model

    def generate_structured(self, prompt: str, json_schema: dict) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self._temperature,
                response_mime_type="application/json",
                response_json_schema=json_schema,
            ),
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return text
