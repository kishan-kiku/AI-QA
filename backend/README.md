# backend

FastAPI application: HTTP API, request validation, prompt loading, AI service, Gemini provider adapter.

## Run

From the repo root, with `.venv` activated and `.env` populated:

```text
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

OpenAPI docs: http://localhost:8000/docs

## Test

```text
pytest backend
```

Tests inject `FakeProvider`. They do not call Gemini.
