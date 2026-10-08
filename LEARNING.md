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

## Later phases

Phase 1+ entries will be appended here after each milestone.
