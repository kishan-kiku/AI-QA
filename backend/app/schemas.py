from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ScenarioType(str, Enum):
    positive = "positive"
    negative = "negative"
    edge = "edge"
    boundary = "boundary"
    regression = "regression"


ALL_SCENARIO_TYPES = list(ScenarioType)


def _unique_types(values: list[ScenarioType]) -> list[ScenarioType]:
    seen: list[ScenarioType] = []
    for item in values:
        if item not in seen:
            seen.append(item)
    if not seen:
        raise ValueError("Select at least one scenario type")
    return seen


def _strip_description(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) < 10:
        raise ValueError("feature_description must contain at least 10 characters")
    return cleaned


class TestScenario(BaseModel):
    id: str
    title: str
    description: str
    type: ScenarioType


class TestCase(BaseModel):
    id: str
    scenario_id: str
    title: str
    preconditions: list[str] = Field(min_length=1)
    steps: list[str] = Field(min_length=1)
    expected_result: str = Field(min_length=1)


class LLMScenarioPayload(BaseModel):
    summary: str = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    scenarios: list[TestScenario] = Field(min_length=1)


class LLMCasePayload(BaseModel):
    test_cases: list[TestCase] = Field(min_length=1)


class LLMQAPayload(LLMScenarioPayload):
    """Full pack JSON from one model call (Phase 1 endpoint)."""

    test_cases: list[TestCase] = Field(min_length=1)


class GenerateRequest(BaseModel):
    feature_description: str = Field(min_length=10, max_length=8000)
    scenario_types: list[ScenarioType] = Field(default_factory=lambda: list(ScenarioType))

    @field_validator("feature_description")
    @classmethod
    def strip_description(cls, value: str) -> str:
        return _strip_description(value)

    @field_validator("scenario_types")
    @classmethod
    def unique_scenario_types(cls, value: list[ScenarioType]) -> list[ScenarioType]:
        return _unique_types(value)


class ScenarioGenerateRequest(GenerateRequest):
    pass


class CaseGenerateRequest(BaseModel):
    feature_description: str = Field(min_length=10, max_length=8000)
    scenarios: list[TestScenario] = Field(min_length=1)

    @field_validator("feature_description")
    @classmethod
    def strip_description(cls, value: str) -> str:
        return _strip_description(value)

    @field_validator("scenarios")
    @classmethod
    def unique_scenario_ids(cls, value: list[TestScenario]) -> list[TestScenario]:
        ids = [item.id for item in value]
        if len(ids) != len(set(ids)):
            raise ValueError("scenarios must have unique ids")
        return value


class GenerateResponse(LLMQAPayload):
    model: str
    disclaimer: str
    warnings: list[str] = Field(default_factory=list)


class ScenarioGenerateResponse(LLMScenarioPayload):
    model: str
    disclaimer: str
    warnings: list[str] = Field(default_factory=list)


class CaseGenerateResponse(LLMCasePayload):
    model: str
    disclaimer: str
    warnings: list[str] = Field(default_factory=list)


SCENARIO_ITEM_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "type": {
            "type": "string",
            "enum": ["positive", "negative", "edge", "boundary", "regression"],
        },
    },
    "required": ["id", "title", "description", "type"],
}

CASE_ITEM_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "scenario_id": {"type": "string"},
        "title": {"type": "string"},
        "preconditions": {"type": "array", "items": {"type": "string"}},
        "steps": {"type": "array", "items": {"type": "string"}},
        "expected_result": {"type": "string"},
    },
    "required": [
        "id",
        "scenario_id",
        "title",
        "preconditions",
        "steps",
        "expected_result",
    ],
}

LLM_JSON_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "scenarios": {"type": "array", "items": SCENARIO_ITEM_SCHEMA},
        "test_cases": {"type": "array", "items": CASE_ITEM_SCHEMA},
    },
    "required": ["summary", "assumptions", "scenarios", "test_cases"],
}

LLM_SCENARIO_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "scenarios": {"type": "array", "items": SCENARIO_ITEM_SCHEMA},
    },
    "required": ["summary", "assumptions", "scenarios"],
}

LLM_CASE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "test_cases": {"type": "array", "items": CASE_ITEM_SCHEMA},
    },
    "required": ["test_cases"],
}
