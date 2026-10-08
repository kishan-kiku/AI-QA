# AI_QA

An AI-powered QA engineering workbench — not a ChatGPT clone.

AI_QA helps a QA engineer turn requirements, stories, and domain knowledge into **reviewable QA artifacts**: test scenarios, test cases, edge cases, and (later) coverage, test data, and API tests.

The long-term differentiator is **domain-aware insurance QA**, especially Guidewire-shaped workflows. That domain knowledge is not hardcoded in Phase 0. It will be supplied later through documents, prompts, and retrieval.

This repository is also a **learning product**. The application is built in phases so the architecture stays understandable while it grows.

## Who it is for

- **Now:** Kishan — insurance / Guidewire QA engineer learning how AI applications are actually built.
- **Later:** other QA engineers who want structured QA output, not chat transcripts.

## Current phase

**Phase 0 — Discovery and Architecture (complete).**

There is no running application yet. This phase exists so the map is written down *before* the first Gemini call.

**Next:** [Phase 1 — Simple AI QA Copilot](ROADMAP.md).

## What we are building first (Phase 1)

A QA engineer types something like:

> Create test cases for a policy cancellation feature.

The UI sends that request to the backend. The backend loads a prompt, calls Gemini through a provider adapter, and returns **structured** scenarios and test cases — the way a junior test designer would hand you a pack for review, not a chat bubble.

## What we are not building yet

RAG, vector databases, multi-agent orchestration, Guidewire-specific hardcoded rules, authentication, PostgreSQL, Docker/Kubernetes, full product navigation, or persisting projects.

Those appear on the [roadmap](ROADMAP.md) when they solve a real problem.

## Architecture at a glance

```
QA Engineer
    ↓
React (Vite) frontend     ← workbench UI; never holds API keys
    ↓  HTTP JSON
FastAPI backend           ← validation, prompts, AI service
    ↓
AI Service                ← "generate test scenarios", not "call Gemini"
    ↓
LLM Provider Adapter      ← Gemini today; swap later
    ↓
Google Gemini
```

Details: [ARCHITECTURE.md](ARCHITECTURE.md).

## Tech stack (locked)

| Layer | Choice | Why |
|---|---|---|
| Backend | Python + FastAPI | Dominant AI engineering stack; Pydantic validates structured LLM output the way you validate an API schema |
| Frontend | React + Vite + TypeScript | Fast local UI; typed contracts with the API |
| LLM | Google Gemini (cloud) | Cloud API; no local GPU/Ollama. Model id is configuration, not hardcoded |
| Data | None in Phase 0/1 | Generate-and-display first; persist when we have entities worth storing |

Cursor is the **development environment**. It is not the application's model API. See [DECISIONS.md](DECISIONS.md).

## Repository layout

```
AI_QA/
  README.md              You are here
  ARCHITECTURE.md        How the pieces connect
  ROADMAP.md             Phases 0–10
  LEARNING.md            What each phase taught
  DECISIONS.md           Why we chose X over Y
  .env.example           Secret and model placeholders
  backend/               API + AI service (Phase 1)
  frontend/              QA workbench UI (Phase 1)
  prompts/qa/            Prompt templates (Phase 1)
```

## Documentation map

| File | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Frontend, backend, AI, prompts, data, request flow |
| [ROADMAP.md](ROADMAP.md) | What exists, what is next, what is later |
| [LEARNING.md](LEARNING.md) | Concepts taught while building |
| [DECISIONS.md](DECISIONS.md) | Architectural choices and rejected alternatives |

## Secrets

Copy `.env.example` to `.env` when Phase 1 starts. Never commit `.env`. Never put `GEMINI_API_KEY` in the frontend.

Think of `.env` as environment config for a test run (PolicyCenter URL, credentials) — it belongs to the machine, not the repository.

## How to run

Not applicable in Phase 0. Phase 1 will add backend and frontend start commands here.
