from app.ai_service import LLMOutputError, parse_llm_json
from app.prompt_loader import load_prompt


def test_prompt_files_are_loadable() -> None:
    pack = load_prompt("qa/generate_test_pack.md")
    scenarios = load_prompt("qa/generate_scenarios.md")
    cases = load_prompt("qa/generate_cases.md")
    assert "reviewable test pack" in pack
    assert "test scenarios only" in scenarios
    assert "listed scenarios" in cases
    assert "Guidewire" in pack


def test_parse_strips_markdown_fences() -> None:
    raw = """```json
{"summary": "ok"}
```"""
    assert parse_llm_json(raw) == {"summary": "ok"}


def test_parse_rejects_prose() -> None:
    try:
        parse_llm_json("Not JSON at all")
    except LLMOutputError as exc:
        assert "JSON" in str(exc)
    else:
        raise AssertionError("expected LLMOutputError")
