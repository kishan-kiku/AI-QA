import type {
  CaseGenerateResponse,
  GenerateResponse,
  ScenarioGenerateResponse,
  ScenarioType,
  TestScenario,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function formatDetail(detail: unknown): string {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg: string }).msg);
        }
        return JSON.stringify(item);
      })
      .join("; ");
  }
  return "Request failed";
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? (payload as { detail: unknown }).detail
        : null;
    throw new Error(formatDetail(detail) || `HTTP ${response.status}`);
  }

  return payload as T;
}

export async function generateTestPack(
  featureDescription: string,
  scenarioTypes: ScenarioType[],
): Promise<GenerateResponse> {
  return postJson("/api/v1/generate", {
    feature_description: featureDescription,
    scenario_types: scenarioTypes,
  });
}

export async function generateScenarios(
  featureDescription: string,
  scenarioTypes: ScenarioType[],
): Promise<ScenarioGenerateResponse> {
  return postJson("/api/v1/generate/scenarios", {
    feature_description: featureDescription,
    scenario_types: scenarioTypes,
  });
}

export async function generateCases(
  featureDescription: string,
  scenarios: TestScenario[],
): Promise<CaseGenerateResponse> {
  return postJson("/api/v1/generate/cases", {
    feature_description: featureDescription,
    scenarios,
  });
}
