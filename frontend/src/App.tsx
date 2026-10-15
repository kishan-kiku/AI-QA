import { FormEvent, useMemo, useState } from "react";
import { generateCases, generateScenarios } from "./api";
import { POLICY_CANCELLATION_SAMPLE } from "./sample";
import {
  SCENARIO_TYPES,
  type ScenarioType,
  type TestCase,
  type TestScenario,
} from "./types";

function casesForScenario(cases: TestCase[], scenarioId: string): TestCase[] {
  return cases.filter((item) => item.scenario_id === scenarioId);
}

function ScenarioCard({
  scenario,
  cases,
  selected,
  onToggle,
}: {
  scenario: TestScenario;
  cases: TestCase[];
  selected: boolean;
  onToggle: () => void;
}) {
  return (
    <article className="scenario">
      <header className="scenario-head">
        <label className="select-scenario">
          <input type="checkbox" checked={selected} onChange={onToggle} />
          <span className="sr-only">Select {scenario.id}</span>
        </label>
        <span className={`badge badge-${scenario.type}`}>{scenario.type}</span>
        <span className="muted">{scenario.id}</span>
        <h3>{scenario.title}</h3>
      </header>
      <p>{scenario.description}</p>
      {cases.length === 0 && (
        <p className="muted">No cases yet — select this scenario and generate cases.</p>
      )}
      {cases.map((testCase) => (
        <section key={testCase.id} className="testcase">
          <h4>
            {testCase.id} — {testCase.title}
          </h4>
          <p className="label">Preconditions</p>
          <ul>
            {testCase.preconditions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <p className="label">Steps</p>
          <ol>
            {testCase.steps.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
          <p className="label">Expected result</p>
          <p className="expected">{testCase.expected_result}</p>
        </section>
      ))}
    </article>
  );
}

export default function App() {
  const [description, setDescription] = useState(POLICY_CANCELLATION_SAMPLE);
  const [types, setTypes] = useState<ScenarioType[]>([...SCENARIO_TYPES]);
  const [summary, setSummary] = useState("");
  const [assumptions, setAssumptions] = useState<string[]>([]);
  const [scenarios, setScenarios] = useState<TestScenario[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [cases, setCases] = useState<TestCase[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [disclaimer, setDisclaimer] = useState("");
  const [model, setModel] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<"idle" | "scenarios" | "cases">("idle");

  const selectedScenarios = useMemo(
    () => scenarios.filter((item) => selectedIds.includes(item.id)),
    [scenarios, selectedIds],
  );

  const grouped = useMemo(
    () =>
      scenarios.map((scenario) => ({
        scenario,
        cases: casesForScenario(cases, scenario.id),
      })),
    [scenarios, cases],
  );

  function toggleType(type: ScenarioType) {
    setTypes((current) =>
      current.includes(type)
        ? current.filter((item) => item !== type)
        : [...current, type],
    );
  }

  function toggleScenario(id: string) {
    setSelectedIds((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id],
    );
  }

  async function onGenerateScenarios(event: FormEvent) {
    event.preventDefault();
    setLoading("scenarios");
    setError(null);
    try {
      const result = await generateScenarios(description, types);
      setSummary(result.summary);
      setAssumptions(result.assumptions);
      setScenarios(result.scenarios);
      setSelectedIds(result.scenarios.map((item) => item.id));
      setCases([]);
      setWarnings(result.warnings);
      setDisclaimer(result.disclaimer);
      setModel(result.model);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scenario generation failed");
    } finally {
      setLoading("idle");
    }
  }

  async function onGenerateCases() {
    setLoading("cases");
    setError(null);
    try {
      const result = await generateCases(description, selectedScenarios);
      setCases(result.test_cases);
      setWarnings(result.warnings);
      setDisclaimer(result.disclaimer);
      setModel(result.model);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Case generation failed");
    } finally {
      setLoading("idle");
    }
  }

  const busy = loading !== "idle";
  const hasPack = scenarios.length > 0;

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI_QA</p>
          <h1>QA Copilot</h1>
        </div>
        <p className="phase">Phase 2 — scenarios, then cases</p>
      </header>

      <main className="layout">
        <section className="panel input-panel">
          <h2>Feature or requirement</h2>
          <p className="lede">
            Step 1: choose scenario types and generate a review list. Step 2: keep
            the scenarios you want and expand them into cases. The UI never talks
            to Gemini.
          </p>
          <form onSubmit={onGenerateScenarios}>
            <label htmlFor="feature">Description</label>
            <textarea
              id="feature"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={12}
              required
              minLength={10}
            />
            <fieldset className="type-picker">
              <legend>Scenario types</legend>
              {SCENARIO_TYPES.map((type) => (
                <label key={type} className="type-option">
                  <input
                    type="checkbox"
                    checked={types.includes(type)}
                    onChange={() => toggleType(type)}
                  />
                  {type}
                </label>
              ))}
            </fieldset>
            <div className="actions">
              <button type="submit" disabled={busy || types.length === 0}>
                {loading === "scenarios" ? "Designing scenarios…" : "Generate scenarios"}
              </button>
              <button
                type="button"
                className="secondary"
                onClick={() => setDescription(POLICY_CANCELLATION_SAMPLE)}
              >
                Load cancellation sample
              </button>
            </div>
          </form>
        </section>

        <section className="panel output-panel">
          {!hasPack && !error && loading === "idle" && (
            <div className="empty">
              <h2>Review pack</h2>
              <p>
                Scenarios appear first. Nothing is saved — refresh clears the pack.
              </p>
            </div>
          )}

          {loading === "scenarios" && (
            <p className="status">Generating scenarios (structured JSON, not a chat reply).</p>
          )}
          {loading === "cases" && (
            <p className="status">Expanding selected scenarios into test cases.</p>
          )}

          {error && (
            <div className="error" role="alert">
              <h2>Generation failed</h2>
              <p>{error}</p>
            </div>
          )}

          {hasPack && (
            <>
              {disclaimer && <p className="disclaimer">{disclaimer}</p>}
              <p className="meta">
                Model <code>{model}</code> · {scenarios.length} scenarios ·{" "}
                {cases.length} cases · {selectedIds.length} selected
              </p>
              {warnings.length > 0 && (
                <div className="warnings">
                  <h2>Validation notes</h2>
                  <ul>
                    {warnings.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
              <h2>Summary</h2>
              <p>{summary}</p>
              {assumptions.length > 0 && (
                <>
                  <h2>Assumptions</h2>
                  <ul>
                    {assumptions.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </>
              )}
              <div className="select-row">
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setSelectedIds(scenarios.map((item) => item.id))}
                >
                  Select all
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setSelectedIds([])}
                >
                  Select none
                </button>
                <button
                  type="button"
                  disabled={busy || selectedScenarios.length === 0}
                  onClick={onGenerateCases}
                >
                  {loading === "cases"
                    ? "Writing cases…"
                    : `Generate cases (${selectedScenarios.length})`}
                </button>
              </div>
              <h2>Scenarios and cases</h2>
              {grouped.map(({ scenario, cases: scenarioCases }) => (
                <ScenarioCard
                  key={scenario.id}
                  scenario={scenario}
                  cases={scenarioCases}
                  selected={selectedIds.includes(scenario.id)}
                  onToggle={() => toggleScenario(scenario.id)}
                />
              ))}
            </>
          )}
        </section>
      </main>
    </div>
  );
}
