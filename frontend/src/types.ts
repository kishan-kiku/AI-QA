export type ScenarioType =
  | "positive"
  | "negative"
  | "edge"
  | "boundary"
  | "regression";

export const SCENARIO_TYPES: ScenarioType[] = [
  "positive",
  "negative",
  "edge",
  "boundary",
  "regression",
];

export interface TestScenario {
  id: string;
  title: string;
  description: string;
  type: ScenarioType;
}

export interface TestCase {
  id: string;
  scenario_id: string;
  title: string;
  preconditions: string[];
  steps: string[];
  expected_result: string;
}

export interface GenerateResponse {
  summary: string;
  assumptions: string[];
  scenarios: TestScenario[];
  test_cases: TestCase[];
  model: string;
  disclaimer: string;
  warnings: string[];
}

export interface ScenarioGenerateResponse {
  summary: string;
  assumptions: string[];
  scenarios: TestScenario[];
  model: string;
  disclaimer: string;
  warnings: string[];
}

export interface CaseGenerateResponse {
  test_cases: TestCase[];
  model: string;
  disclaimer: string;
  warnings: string[];
}
