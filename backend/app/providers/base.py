from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Vendor-agnostic completion interface. Analog: WebDriver vs ChromeDriver."""

    @property
    @abstractmethod
    def model_id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_structured(self, prompt: str, json_schema: dict) -> str:
        """Return a JSON string that should match json_schema."""
        raise NotImplementedError
