# Decisions

Record major choices so we do not rediscover them in six months. Format: context, options, choice, why, consequences.

Small implementation details do not belong here.

---

## D001 — Separate FastAPI backend and React frontend

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 0

**Context:** Empty repo. Need a stack that teaches AI application architecture and can grow into a real product.

**Options:**

1. **Python FastAPI + React/Vite** — two processes, clear HTTP boundary.
2. **Next.js (TypeScript only)** — one language, UI and API in one framework.
3. **Python UI kits (Streamlit/Gradio)** — fastest demo, weakest product shape.

**Choice:** Option 1. Confirmed with Kishan.

**Why:** LLM SDKs, structured output (Pydantic), and later RAG/eval work are Python-first. A separate UI and API makes the request path obvious — the same reason you separate UI tests from API tests instead of asserting everything in one script.

**Consequences:** Two runtimes to start in Phase 1 (`uvicorn` + `vite`). Worth it for learning and evolution. CORS will need an explicit allow-list for the Vite origin.

**Rejected:** Next.js would ship UI faster but hide the backend boundary. Streamlit would train the wrong instinct (prototype, not workbench).

---

## D002 — Google Gemini as the first cloud LLM

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 0

**Context:** Need a cloud LLM. Local hosting (Ollama, CUDA) is out of scope. Cursor subscription is not an application API key.

**Options:** OpenAI, Anthropic Claude, Google Gemini, Cursor SDK as the app brain.

**Choice:** Gemini. Confirmed with Kishan. Default to a Flash-class model; exact id in `GEMINI_MODEL`.

**Why:** Cloud, no local GPU, reasonable cost/speed for iterative QA generation. Flash is enough for Phase 1 structured lists. Provider is behind an adapter so this is not a life sentence.

**Consequences:** Backend depends on `GEMINI_API_KEY`. If the key is missing, the API must fail clearly. We will not hardcode a model id in multiple files — vendors rename models.

**Rejected:** Cursor SDK — that runs **coding agents** against a repo (tools, files, long loops). Using it to generate a test pack would be like launching a full Guidewire regression controller to print a notepad list of scenarios. Wrong abstraction, extra cost, extra risk.

---

## D003 — Provider adapter; do not call the vendor SDK from the UI or from every route

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 0

**Context:** Model vendors change. We will want OpenAI or local models later without rewriting the workbench.

**Choice:** `AI Service` → `LLM Provider` interface → `GeminiProvider`.

**Why:** Same idea as WebDriver vs ChromeDriver. Application code says "complete this QA generation." Only the adapter knows Gemini's SDK.

**Consequences:** A little extra code in Phase 1. Pays off the first time we switch providers or mock the LLM in tests.

---

## D004 — No database in Phase 0 or Phase 1

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 0

**Context:** Need somewhere to store… nothing yet. First value is a round-trip to Gemini.

**Options:** SQLite now, PostgreSQL now, no database until we persist artifacts.

**Choice:** No database until we have entities we must query (likely Phase 3 — requirements and generated cases). Then SQLite first.

**Why:** A results warehouse before the first test run is ceremony. SQLite later is enough for a local learning product; PostgreSQL when we have multi-user or serious volume.

**Consequences:** Refreshing the UI loses generated output in Phase 1. Acceptable. We will say so in the Phase 1 UI.

---

## D005 — Prompts live in files, not buried in UI code

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 0

**Choice:** `prompts/qa/` (and later domain folders) as text/markdown templates loaded by the backend.

**Why:** Prompts are closer to test assets than to page objects. They should be reviewable in git without opening React. The UI sends **user input**; the backend combines it with the **system/prompt template**.

**Consequences:** Phase 1 must include a small prompt loader. Do not invent a prompt CMS.

---

## D006 — No LangChain / LlamaIndex in Phase 0/1

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 0

**Choice:** Official Gemini SDK + our thin adapter.

**Why:** Orchestration frameworks hide the actual HTTP/SDK call. The learning goal is to *see* the path: request → prompt → provider → model → parse → validate. Add a framework when we have orchestration pain (many tools, many steps), not on day one.

**Consequences:** We write a small amount of glue ourselves. That glue *is* the lesson.

---

## D007 — No local LLM hosting

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 0

**Choice:** Cloud Gemini only. Ollama, local GPU, Hugging Face inference servers are a later study phase if needed.

**Why:** Local inference is an infrastructure project. It would delay the first useful QA loop.

---

## D008 — AI output is never treated as truth

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 0

**Choice:** Validate shape in the backend; human reviews domain correctness. Later: evaluation tests, coverage checks, user feedback.

**Why:** LLMs hallucinate. A well-formatted cancellation test that assumes a coverage that does not exist is still a failed actual vs expected — the "actual" just looks professional.

**Consequences:** Phase 1 UI should read as a **review pack**, not as "the system created your tests, you're done."

---

## D009 — Git: milestone commits, no force-push, no remote until we have one

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 0

**Choice:** Commit at logical milestones (Phase 0 complete, then Phase 1, …). Do not push unless asked.

**Why:** History should match learning milestones so the repo stays teachable.

**Update:** Remote is `https://github.com/kishan-kiku/AI-QA.git`.

---

## D010 — Fake provider beside Gemini

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 1

**Context:** Need to run UI and tests without a Gemini key, and to prove the adapter is real.

**Choice:** `AI_QA_PROVIDER=gemini|fake`. Fake returns a canned policy-cancellation pack.

**Why:** Same reason you stub an unavailable PolicyCenter in a CI pipeline. The rest of the app must not care.

**Consequences:** A local `.env` can use `fake` for demos. Production-shaped runs must use `gemini` and a real key. Tests always inject `FakeProvider` and ignore this env var.

---

## D011 — JSON Schema to Gemini, Pydantic after the fact

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 1

**Choice:** Pass a hand-written JSON Schema via `response_json_schema`. Parse text (including markdown fences). Validate with `LLMQAPayload`. Reject orphan `scenario_id` values.

**Why:** Asking the model nicely is not a quality gate. Validating the actual result is. We avoid Pydantic `$defs` graphs because Gemini supports a JSON Schema subset.

---

## D012 — Temperature 0.3 for QA generation

**Date:** 2026-10-08  
**Status:** Accepted  
**Phase:** 1

**Choice:** Gemini `temperature=0.3`.

**Why:** QA packs should be conservative. We can raise temperature later if we want more diverse negative ideas.

---

## D013 — Two-step generation: scenarios, then cases

**Date:** 2026-10-11  
**Status:** Accepted  
**Phase:** 2

**Options:** (A) type checkboxes on the Phase 1 one-shot call; (B) generate scenarios, human selects, then generate cases.

**Choice:** B for the workbench. Keep `POST /api/v1/generate` as a one-shot API.

**Why:** A test lead reviews the scenario list before anyone writes cases. A filter on a one-shot call still skips that gate.

**Consequences:** Two prompts, two schemas, two endpoints. No session store — the UI sends selected scenarios back on the second call.

---

## D014 — Missing requested types are warnings; extra types are errors

**Date:** 2026-10-11  
**Status:** Accepted  
**Phase:** 2

**Choice:** If the model returns a `type` you did not ask for → 502. If it skips a type you asked for → `warnings[]`.

**Why:** Extra types are a contract violation (like an API adding undeclared fields you must not persist). Missing types are a coverage gap you may accept, like a planned negative that was not written this sprint.
