# Architecture

Phase 0 defined **where things live**. Phase 1 implements the request flow below.

If you already design test architecture, treat this document like a test-system design: layers, responsibilities, interfaces, and what is deliberately out of scope.

## What AI_QA is

A **QA workbench** that produces structured engineering artifacts.

It is not:

- a generic chatbot with a QA system prompt
- an autonomous agent (yet)
- a Guidewire product that "knows" PolicyCenter internals we have not provided

The model is a **junior analyst**. The application is the **process** around that analyst: input validation, prompt, structured output, and (later) review, persistence, and retrieval.

## High-level request flow (Phase 2)

```
QA Engineer
    ↓  types a feature + selects scenario types
React Vite frontend
    ↓  POST /api/v1/generate/scenarios
Backend → prompt (scenarios) → provider → validate types
    ↓  reviewable scenario list
QA Engineer selects scenarios to keep
    ↓  POST /api/v1/generate/cases
Backend → prompt (cases) → provider → validate coverage
    ↓  cases attached to selected scenarios
```

Phase 1 one-shot `POST /api/v1/generate` is still available. The workbench uses the two-step path because a test lead reviews the scenario list before anyone writes cases.

Every generated artifact is a **suggestion**. The human QA engineer is the gate, the same way an automation suite does not become production truth until someone reviews failures.

## Responsibilities

### Frontend (`frontend/`)

- Collect user input (feature description, later: requirements, options).
- Display structured output (scenarios, cases) in a QA-focused layout — not a chat transcript.
- Talk only to **our** backend.

The frontend must never:

- hold `GEMINI_API_KEY`
- call Gemini (or any LLM) directly

Same rule as UI tests: do not embed PolicyCenter credentials in a browser script that anyone can inspect.

### Backend (`backend/`)

The application brain:

- HTTP API (FastAPI)
- request/response schemas (Pydantic)
- load prompts
- call the AI service
- validate model output before it reaches the UI
- (later) persistence, retrieval, evaluation

FastAPI also exposes OpenAPI docs automatically. That is useful as a QA engineer: the product API is inspectable the same way you inspect a Guidewire integration API.

### AI Service

An internal module the rest of the app calls with **QA intent**:

- generate test scenarios
- (later) generate cases, analyze requirements, map coverage

It does **not** expose Gemini method names to the UI or to every route. Analog: Selenium WebDriver — tests say `click()`, they do not speak Chrome DevTools Protocol.

### LLM Provider Adapter

One interface, one implementation in Phase 1: `GeminiProvider`.

The rest of the application should not care whether the underlying model is Gemini, OpenAI, Anthropic, or a future local model. Model **id** is configuration (`GEMINI_MODEL` in `.env`), not scattered string literals.

### Prompts (`prompts/`)

Prompt text is not buried in React components or random Python strings.

| Kind of text | Lives in | Analog |
|---|---|---|
| Source code | `backend/`, `frontend/` | Test framework / page objects |
| Configuration | `.env`, later settings | Environment URLs, timeouts |
| Prompt | `prompts/` | Reusable test library / keyword layer |
| Documentation | `*.md` at repo root | Living test strategy |
| System instruction | part of the prompt sent to the model | Setup: "you are a QA designer…" |
| User input | HTTP request body | Test data for this run |
| Model output | HTTP response (after validation) | Actual result — must be checked |

Markdown prompt files are useful because they are reviewable, diffable in git, and editable without redeploying UI code. They are still **not source of truth for business rules** — they are instructions to a model that can ignore or hallucinate them.

### Data

**Phase 0/1: no database.**

A request comes in, a response goes out. We do not persist projects, requirements, or generated cases until those entities exist and we need history.

Introducing SQLite (or anything else) before the first successful Gemini round-trip is standing up a results warehouse before the first test executes.

Likely later entities (not created now): Project, Requirement, TestScenario, TestCase, Prompt, AIRequest/AIResponse, CoverageMapping, KnowledgeChunk.

## Where AI fits

AI is a **dependency behind an interface**, not the application.

```
Application (FastAPI + React)
    ↓
AI Service
    ↓
Model Provider Adapter
    ↓
Cloud LLM (Gemini)
```

If Gemini is down, the UI should get an application error, not a raw SDK stack trace. If we change providers, the UI contract stays the same.

## Where models fit

- **Provider:** Google Gemini (cloud).
- **Default class of model:** Flash — fast and cheap enough to iterate on QA generation while learning.
- **Exact model id:** environment variable, because vendors rename models.
- **Not used as the app LLM:** Cursor Agent / Cursor SDK. Cursor runs coding agents against a repo. AI_QA needs a completion/chat call behind an HTTP API.

## Where secrets fit

| Item | Location |
|---|---|
| `GEMINI_API_KEY` | `.env` on the machine that runs the backend |
| `GEMINI_MODEL` | `.env` (not secret, but environment-specific) |
| `.env` | gitignored |
| `.env.example` | committed, empty placeholders |

Never log full prompts that contain production policyholder data. Phase 1 will use synthetic insurance examples.

## Phase 1 files

| Path | Role |
|---|---|
| `backend/app/main.py` | `GET /health`, `POST /api/v1/generate`, `/generate/scenarios`, `/generate/cases` |
| `backend/app/schemas.py` | Separate contracts + JSON Schemas for pack, scenarios, cases |
| `backend/app/ai_service.py` | Two prompts, two schemas, type/coverage validation |
| `backend/app/providers/` | `LLMProvider` + `GeminiProvider` + `FakeProvider` |
| `prompts/qa/` | `generate_test_pack.md`, `generate_scenarios.md`, `generate_cases.md` |
| `frontend/src/App.tsx` | Type filter → scenarios → select → cases |

**Still not added:**

- RAG / embeddings / vector store
- Agents / tool calling
- Database
- Auth
- Full navigation (Requirements, Coverage, Agents, …)
- Hardcoded Guidewire product model

## Quality rule

AI output is **suggested engineering output requiring validation**.

The architecture must assume:

- the model may return markdown instead of JSON
- the model may invent coverages, statuses, or Guidewire screens
- duplicate or missing scenarios are normal
- traditional pass/fail tests are insufficient for "is this a good test pack?" — we will add evaluation later

Phase 1 starts that habit with schema validation. Domain correctness remains a human review — your job, not the model's.
