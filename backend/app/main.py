from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.ai_service import AIService, LLMOutputError
from app.config import Settings, get_settings
from app.providers import build_provider
from app.schemas import (
    CaseGenerateRequest,
    CaseGenerateResponse,
    GenerateRequest,
    GenerateResponse,
    ScenarioGenerateRequest,
    ScenarioGenerateResponse,
)

app = FastAPI(
    title="AI_QA",
    description="AI-powered QA engineering workbench. Generated artifacts require human review.",
    version="0.2.0",
)


def configure_cors(application: FastAPI, settings: Settings) -> None:
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


configure_cors(app, get_settings())


def get_ai_service(settings: Settings = Depends(get_settings)) -> AIService:
    return AIService(build_provider(settings))


def _run(action):
    try:
        return action()
    except LLMOutputError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream model request failed: {exc}",
        ) from exc


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "phase": 2, "product": "AI_QA"}


@app.post("/api/v1/generate", response_model=GenerateResponse)
def generate(
    request: GenerateRequest,
    service: AIService = Depends(get_ai_service),
) -> GenerateResponse:
    return _run(lambda: service.generate_test_pack(request))


@app.post("/api/v1/generate/scenarios", response_model=ScenarioGenerateResponse)
def generate_scenarios(
    request: ScenarioGenerateRequest,
    service: AIService = Depends(get_ai_service),
) -> ScenarioGenerateResponse:
    return _run(lambda: service.generate_scenarios(request))


@app.post("/api/v1/generate/cases", response_model=CaseGenerateResponse)
def generate_cases(
    request: CaseGenerateRequest,
    service: AIService = Depends(get_ai_service),
) -> CaseGenerateResponse:
    return _run(lambda: service.generate_cases(request))
