# prompts/qa

Prompt templates for QA generation. Loaded by the backend, never by the UI.

- `generate_test_pack.md` — one-shot full pack (API `POST /api/v1/generate`)
- `generate_scenarios.md` — scenarios only (`POST /api/v1/generate/scenarios`)
- `generate_cases.md` — cases for selected scenarios (`POST /api/v1/generate/cases`)
