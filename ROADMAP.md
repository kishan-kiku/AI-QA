# Roadmap

Build in phases. Each phase has a clear objective, something working, something to learn, and a foundation for the next phase.

Do not treat later phases as a backlog to implement early.

## Status legend

- **Done** — in the repo
- **Next** — the following implementation milestone
- **Later** — planned, not started
- **Not yet** — explicitly out of scope until a prior phase is real

## Phase 0 — Discovery and Architecture

**Status: Done**

Objective: inspect the empty repo, lock stack and LLM provider, write the map.

Delivered:

- This documentation set (`README`, `ARCHITECTURE`, `ROADMAP`, `LEARNING`, `DECISIONS`)
- `.gitignore` and `.env.example`
- Folder placeholders: `backend/`, `frontend/`, `prompts/qa/`

Not delivered (by design): running app, Gemini calls, UI, database.

## Phase 1 — Simple AI QA Copilot

**Status: Done**

Objective: smallest useful loop — input a feature, get structured QA output.

Delivered:

- FastAPI `GET /health` and `POST /api/v1/generate`
- Gemini provider adapter (model id from env) plus a `fake` provider for tests/UI without a key
- Prompt file `prompts/qa/generate_test_pack.md`
- React/Vite workbench (review pack, not a chat clone)
- Structured scenarios and test cases
- Policy-cancellation sample that does not invent Guidewire screens
- pytest coverage for validation, happy path (fake), markdown-instead-of-JSON, orphan scenario ids

## Phase 2 — Structured QA Generation

**Status: Done**

Objective: stop generating the whole pack in one blob.

Delivered:

- Scenario-type filter (positive, negative, edge, boundary, regression)
- `POST /api/v1/generate/scenarios` and `POST /api/v1/generate/cases`
- Separate prompts and JSON schemas for each step
- Validation gates: unrequested types rejected; every selected scenario must get a case
- Missing requested types become warnings, not a hard failure
- Workbench: generate scenarios → select → generate cases
- Phase 1 full-pack endpoint kept

## Phase 3 — Requirement → Test Case

**Status: Next**

Paste/upload a requirement. Analyze → acceptance criteria → scenarios → cases → coverage mapping.

Learn: document processing, chunking, prompt construction, traceability (requirement id ↔ test id).

First likely persistence (SQLite): requirements and generated artifacts.

## Phase 4 — QA Knowledge Base / RAG

**Status: Later**

Introduce retrieval **when generation without project documents starts to fail** (wrong process, missing house rules, invented Guidewire steps).

Flow: documents → chunk → embed → vector store → retrieve → inject context → LLM.

Learn: embeddings, similarity, hallucination reduction **and** RAG limits.

## Phase 5 — Domain-aware Insurance QA

**Status: Later**

Policy, rating, billing, claims, underwriting, endorsement, renewal, cancellation — as **supplied knowledge**, not thousands of hardcoded rules.

## Phase 6 — Guidewire QA Copilot

**Status: Later**

PolicyCenter / ClaimCenter / BillingCenter shaped workflows, product model and rating **from project documents**. Do not invent proprietary Guidewire behavior.

## Phase 7 — API QA

**Status: Later**

OpenAPI/Swagger in → positive, negative, authz, schema, error-handling tests. Execution only when it is justified.

## Phase 8 — Test Data Generation

**Status: Later**

Customers, policies, coverages, claims — valid, invalid, boundary, risk-focused. Validate; do not trust generated data blindly.

## Phase 9 — QA Agents

**Status: Later**

Agents only after the single-call path is stable. Possible roles: requirement analyst, test designer, reviewer, coverage, domain, orchestrator.

Learn: agents vs a normal LLM call, tools, loops, guardrails.

## Phase 10 — QA Autonomy

**Status: Later**

End-to-end assisted workflow: analyze → risks → scenarios → cases → review → coverage → data → report. Still human-gated.

## Explicitly not now

Kubernetes, microservices, event buses, enterprise SSO, local LLM hosting (Ollama/CUDA), LangChain as a default, Cursor SDK as the app's LLM.
