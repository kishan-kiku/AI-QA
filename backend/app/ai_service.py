import json
import re

from pydantic import ValidationError

from app.prompt_loader import load_prompt
from app.providers.base import LLMProvider
from app.schemas import (
    CaseGenerateRequest,
    CaseGenerateResponse,
    GenerateRequest,
    GenerateResponse,
    LLM_CASE_SCHEMA,
    LLM_JSON_SCHEMA,
    LLM_SCENARIO_SCHEMA,
    LLMCasePayload,
    LLMQAPayload,
    LLMScenarioPayload,
    ScenarioGenerateResponse,
    ScenarioType,
    TestScenario,
)

DISCLAIMER = (
    "Suggested engineering output requiring human validation. "
    "AI_QA does not execute these tests and does not treat them as production truth."
)

GENERATE_PROMPT_PATH = "qa/generate_test_pack.md"
SCENARIO_PROMPT_PATH = "qa/generate_scenarios.md"
CASE_PROMPT_PATH = "qa/generate_cases.md"


class LLMOutputError(Exception):
    """Model returned text that is not a valid QA pack. Analog: response schema mismatch."""


def parse_llm_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMOutputError(
            "The model did not return JSON. This is a common LLM failure "
            "(markdown fences or prose instead of a JSON object)."
        ) from exc
    if not isinstance(data, dict):
        raise LLMOutputError("The model returned JSON that is not an object.")
    return data


def format_types(types: list[ScenarioType]) -> str:
    return ", ".join(item.value for item in types)


def missing_type_warnings(
    scenarios: list[TestScenario], requested: list[ScenarioType]
) -> list[str]:
    present = {item.type for item in scenarios}
    return [
        f"No {item.value} scenarios were generated. Review whether that type is needed."
        for item in requested
        if item not in present
    ]


def assert_types_allowed(
    scenarios: list[TestScenario], requested: list[ScenarioType]
) -> None:
    allowed = set(requested)
    unexpected = sorted(
        {item.type.value for item in scenarios if item.type not in allowed}
    )
    if unexpected:
        raise LLMOutputError(
            "The model returned scenario types that were not requested: "
            + ", ".join(unexpected)
        )


def assert_cases_match_scenarios(
    cases: list, scenarios: list[TestScenario]
) -> None:
    scenario_ids = {item.id for item in scenarios}
    dangling = [case.id for case in cases if case.scenario_id not in scenario_ids]
    if dangling:
        raise LLMOutputError(
            "The model returned test cases whose scenario_id does not match any scenario: "
            + ", ".join(dangling)
        )
    uncovered = [
        item.id
        for item in scenarios
        if not any(case.scenario_id == item.id for case in cases)
    ]
    if uncovered:
        raise LLMOutputError(
            "The model did not return a test case for every selected scenario: "
            + ", ".join(uncovered)
        )


class AIService:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider
        self._pack_prompt = load_prompt(GENERATE_PROMPT_PATH)
        self._scenario_prompt = load_prompt(SCENARIO_PROMPT_PATH)
        self._case_prompt = load_prompt(CASE_PROMPT_PATH)

    def generate_test_pack(self, request: GenerateRequest) -> GenerateResponse:
        types = format_types(request.scenario_types)
        prompt = (
            f"{self._pack_prompt}\n\n"
            f"## Requested scenario types: {types}\n\n"
            "## Feature / requirement to design tests for\n\n"
            f"{request.feature_description}\n"
        )
        raw = self._provider.generate_structured(prompt, LLM_JSON_SCHEMA)
        payload = self._validate_pack(raw, request.scenario_types)
        return GenerateResponse(
            **payload.model_dump(),
            model=self._provider.model_id,
            disclaimer=DISCLAIMER,
            warnings=missing_type_warnings(payload.scenarios, request.scenario_types),
        )

    def generate_scenarios(self, request: GenerateRequest) -> ScenarioGenerateResponse:
        types = format_types(request.scenario_types)
        prompt = (
            f"{self._scenario_prompt}\n\n"
            f"## Requested scenario types: {types}\n\n"
            "## Feature / requirement to design tests for\n\n"
            f"{request.feature_description}\n"
        )
        raw = self._provider.generate_structured(prompt, LLM_SCENARIO_SCHEMA)
        payload = self._validate_scenarios(raw, request.scenario_types)
        return ScenarioGenerateResponse(
            **payload.model_dump(),
            model=self._provider.model_id,
            disclaimer=DISCLAIMER,
            warnings=missing_type_warnings(payload.scenarios, request.scenario_types),
        )

    def generate_cases(self, request: CaseGenerateRequest) -> CaseGenerateResponse:
        scenario_block = "\n".join(
            f"- {item.id} [{item.type.value}] {item.title}: {item.description}"
            for item in request.scenarios
        )
        prompt = (
            f"{self._case_prompt}\n\n"
            "## Feature / requirement (context only)\n\n"
            f"{request.feature_description}\n\n"
            "## Scenarios to expand into test cases\n\n"
            f"{scenario_block}\n"
        )
        raw = self._provider.generate_structured(prompt, LLM_CASE_SCHEMA)
        payload = self._validate_cases(raw, request.scenarios)
        return CaseGenerateResponse(
            **payload.model_dump(),
            model=self._provider.model_id,
            disclaimer=DISCLAIMER,
            warnings=[],
        )

    @staticmethod
    def _validate_pack(raw: str, requested: list[ScenarioType]) -> LLMQAPayload:
        data = parse_llm_json(raw)
        try:
            payload = LLMQAPayload.model_validate(data)
        except ValidationError as exc:
            raise LLMOutputError(
                "The model returned JSON that does not match the QA pack schema "
                "(missing fields, wrong types, or empty lists)."
            ) from exc
        assert_types_allowed(payload.scenarios, requested)
        assert_cases_match_scenarios(payload.test_cases, payload.scenarios)
        return payload

    @staticmethod
    def _validate_scenarios(
        raw: str, requested: list[ScenarioType]
    ) -> LLMScenarioPayload:
        data = parse_llm_json(raw)
        try:
            payload = LLMScenarioPayload.model_validate(data)
        except ValidationError as exc:
            raise LLMOutputError(
                "The model returned JSON that does not match the scenario schema "
                "(missing fields, wrong types, or an empty scenario list)."
            ) from exc
        assert_types_allowed(payload.scenarios, requested)
        return payload

    @staticmethod
    def _validate_cases(
        raw: str, scenarios: list[TestScenario]
    ) -> LLMCasePayload:
        data = parse_llm_json(raw)
        try:
            payload = LLMCasePayload.model_validate(data)
        except ValidationError as exc:
            raise LLMOutputError(
                "The model returned JSON that does not match the test-case schema "
                "(missing fields, wrong types, or an empty case list)."
            ) from exc
        assert_cases_match_scenarios(payload.test_cases, scenarios)
        return payload
