# Learning log

This file is the study notes for the product. After each phase: what was learned, what was built, what broke, and questions to answer before the next phase.

Audience: experienced QA professional learning **AI application engineering** — not beginner programming, not beginner testing.

---

## Phase 0 — Discovery and Architecture

### What I learned

An AI product is not "a screen that talks to ChatGPT." It is an application with the same kinds of layers you already use in test architecture:

- a UI that collects input and shows results
- an API that enforces a contract
- a service layer that expresses **intent**
- an adapter to an external system
- configuration and secrets that must not leak into the UI
- artifacts that are **suggestions** until a human validates them

The empty repo was the right time to write that map. Starting with RAG or agents would be like designing a full Guidewire regression factory before the first smoke test passes.

### New AI concepts

**LLM (Large Language Model).** A model that predicts the next tokens of text. It does not "look up" PolicyCenter. It generates plausible language. That is why it can write a useful cancellation scenario **and** invent a coverage that does not exist.

**Cloud API vs Cursor.** Cursor (this IDE) uses models to help *write the product*. AI_QA's backend will call **Gemini** to *be* the product's intelligence. Two different consumers, two different keys. Analog: your automation framework license vs the PolicyCenter environment URL.

**Prompt.** Instructions + user input sent to the model. Treat prompts like reusable test libraries: version them, review them, do not copy-paste them into every screen.

**Model vs provider vs adapter.** Provider = Google. Model = a specific Gemini id (Flash vs Pro). Adapter = our code that speaks that provider's SDK so the rest of the app does not have to.

**Hallucination (preview).** Confident, fluent, wrong. In QA terms: an actual result that looks well-formed but does not match the requirement. Architecture must assume this, not be surprised by it.

Tokens, context windows, temperature, embeddings, RAG, and agents are **not** required to understand Phase 0. They will be taught when the code needs them.

### New software concepts

**Frontend vs backend.** Browser vs server. The browser is untrusted (users can see everything we ship to it). The server holds the Gemini key. Same split as: a public UI vs an integration layer that talks to a billing API with credentials.

**Adapter / provider pattern.** One interface, swap implementations. Analog: WebDriver — your tests target an API; Chrome or Firefox is plugged in underneath.

**Environment variables (`.env`).** Runtime config and secrets. Committed file is `.env.example` (shape only). Real `.env` is gitignored. Analog: keeping environment-specific test configs out of the shared suite.

**No database yet.** Persistence is a product decision, not a default. We persist when we have entities and a reason to query them.

**Pydantic / schema validation (preview for Phase 1).** Typed contracts for JSON in and out. For LLMs, this is the first quality gate: "did we even get a TestScenario list, or did we get a poem?"

### What we implemented

Documentation and a thin folder skeleton only:

- `README.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `LEARNING.md`, `DECISIONS.md`
- `.gitignore`, `.env.example`
- `backend/`, `frontend/`, `prompts/qa/` purpose files

No FastAPI app, no React app, no Gemini call.

### Why we implemented it this way

So the first code in Phase 1 has a place to live and a set of decisions that are written down, not implied. This is the equivalent of a one-page test strategy before the first automation script.

### Problems encountered

None in code — there was no application. The only real risk in Phase 0 is **overbuilding the map**. We kept docs short and refused LangChain, databases, and agents.

### How we solved them

Not applicable.

### Questions I should understand before Phase 1

1. Why must the React app call FastAPI instead of Gemini?
2. What is the difference between Cursor (dev tool) and Gemini (app dependency)?
3. Where should a prompt live, and why not inside a button click handler?
4. What does "structured output" mean compared to a chat reply?
5. If Gemini returns markdown instead of JSON, whose job is it to catch that — UI, API, or AI service?
6. What is the first workflow we will implement, and what will we refuse to add in the same step?

---

## Phase 1 — Simple AI QA Copilot

### What I learned

The first useful AI feature is a **request/response loop with a schema**, not a chatbot.

Flow: UI → FastAPI → prompt file → AI service → provider → (Gemini or fake) → JSON parse → Pydantic validation → UI review pack.

The UI never sees the API key. Tests never need Gemini. That is the same split as UI tests vs a stubbed billing adapter.

### New AI concepts

**Structured output.** We ask the model for JSON that matches a schema, not a paragraph. Analog: asserting an API response against a Swagger/OpenAPI schema instead of grepping log text.

**JSON schema vs Pydantic.** Gemini is given a JSON Schema (`response_json_schema`). After the text comes back, **we** validate with Pydantic. Two gates: “please shape it this way” (model) and “reject it if you didn’t” (our app).

**Temperature (0.3).** Controls how adventurous token choices are. Lower ≈ more repeatable, like fixed test data. Higher ≈ more variety, like random test data — useful for ideas, worse for a stable pack. We start low because QA output should be conservative.

**Tokens / context (preview).** The prompt file + user feature description are the “payload size” of this call. We are nowhere near a context-window limit in Phase 1. When we paste 80-page requirements (Phase 3), this starts to matter.

**Hallucination, now visible.** Even a valid JSON pack can invent a PolicyCenter screen. The disclaimer is not decoration. Schema validation does **not** prove the tests are right — only that they are well-formed.

**Markdown instead of JSON.** A classic LLM defect. We strip ``` fences if present, then still 502 if it is prose. Analog: a SOAP response that arrived as an HTML error page.

### New software concepts

**CORS.** The browser blocks `localhost:5173` from calling `localhost:8000` unless the API allows that origin. Analog: a firewall rule between the UI test box and the API.

**Dependency injection in FastAPI.** Tests replace `get_ai_service` with a service that uses `FakeProvider`. Analog: injecting a stub PolicyCenter client.

**502 vs 422 vs 503.** 422 = our request schema (user input too short). 502 = upstream model output unusable. 503 = we are not configured (missing key). These are different failures; do not collapse them into “AI didn’t work.”

### What we implemented

- Backend generate + health endpoints
- Gemini adapter + fake adapter
- Prompt `prompts/qa/generate_test_pack.md`
- Workbench UI
- pytest for happy path, validation, bad JSON, orphan `scenario_id`

### Why we implemented it this way

A fake provider is not a toy. It is the adapter pattern paying off on day one: the UI and tests can run when Gemini is down, unpaid, or not configured.

### Problems encountered

- There is no `GEMINI_API_KEY` on this machine yet, so the running demo uses `AI_QA_PROVIDER=fake`. The Gemini adapter is implemented; it is not exercised live until a key is added.
- FastAPI TestClient emitted a Starlette/httpx deprecation warning. Tests still passed; we did not chase a framework upgrade in this phase.

### Questions I should understand before Phase 2

1. Where is the JSON schema enforced — Gemini, Pydantic, or both?
2. Why can a 200 response still be a bad test pack?
3. What does temperature change, in QA terms?
4. Why do tests use `FakeProvider` instead of calling Gemini?
5. What would we add in Phase 2 that Phase 1 still generates in one blob?

Answer: a **review gate**. Generate scenarios first. A human selects which ones to keep. Then generate cases only for those. Separate prompts and schemas, plus type filters.

---

## Phase 2 — Structured QA Generation

### What I learned

One LLM call that writes scenarios *and* cases is like asking a junior to deliver a full suite without a test-lead review of the scenario list. Phase 2 inserts that review.

Two prompts + two JSON schemas is not ceremony. A cases prompt that cannot invent new scenario ids is a **smaller, safer contract**. Analog: a test that asserts a cancel API cannot also silently create a new policy.

### New AI concepts

**Prompt design as scope control.** The scenario prompt says “do not write steps.” The case prompt says “do not invent scenarios.” Same model, different job. Analog: a smoke suite vs an end-to-end suite — different charters.

**Validation as a quality gate, not a style preference.**

- Unrequested `type` (you asked for negative, model returned positive) → **502**. That is a contract break.
- Requested type missing (you asked for regression, model skipped it) → **warning**. That is a coverage finding, like a planned test that was not written.

Those are different defects. Do not treat them as one “AI error.”

**Smaller schema, fewer hallucinations of shape.** Asking only for `{ test_cases }` makes it harder for the model to wander into a chatty summary.

### New software concepts

**Two-step API.** `/generate/scenarios` then `/generate/cases`. The second request sends the selected scenario objects back. The server does not remember the first call (no database). Analog: a stateless API test — you pass the quote id you care about; the server does not keep your last UI click.

**Client state is the workbench.** Selected checkboxes live in React. Refresh loses them. That is still acceptable in Phase 2.

### What we implemented

- Type filter
- Scenario endpoint + case endpoint
- Two new prompts
- Type and coverage validators
- Workbench selection step
- Tests for filter, leaked types, missing selected scenarios

### Why we implemented it this way

A checkbox-only filter on the old one-shot call would still write cases for scenarios you never reviewed. The product differentiator is **human-gated structured generation**, not more text.

### Problems encountered

- Fake-provider type filter failed tests because the prompt heading was `Requested scenario types` and the stub looked for a colon. The model does not need the colon; the stub did. Lesson: test doubles parse our prompt text — keep that text mechanical.

### Questions I should understand before Phase 3

1. Why are unrequested types a 502, but missing types a warning?
2. Why does the cases request include the full scenario objects, not just ids?
3. Why is there still no database?
4. What breaks when the requirement is a 20-page story instead of a textarea?
