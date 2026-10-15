import json
import re

from app.providers.base import LLMProvider

# Canned pack so the UI and tests can run without a cloud call.
# Analog: a stub PolicyCenter adapter that returns a known quote.
CANNED_PACK = {
    "summary": (
        "Cancellation of an in-force personal auto policy: effective date, "
        "prorated premium, outstanding balances, and related claims."
    ),
    "assumptions": [
        "Personal auto policy; cancellation is requested by the policyholder.",
        "A future, current, or past effective date may be supplied.",
        "Billing and claims systems are in scope only at the interface (balance, open claim).",
        "No Guidewire screen names or APIs were provided, so none are asserted.",
    ],
    "scenarios": [
        {
            "id": "SC-01",
            "title": "Cancel an active policy mid-term",
            "description": "Insured requests cancellation of an in-force policy with a valid future or current date.",
            "type": "positive",
        },
        {
            "id": "SC-02",
            "title": "Cancel an already expired policy",
            "description": "Cancellation is requested for a policy that is already expired or non-renewed.",
            "type": "negative",
        },
        {
            "id": "SC-03",
            "title": "Cancel a future-dated (not yet effective) policy",
            "description": "Policy is bound but the term has not started.",
            "type": "edge",
        },
        {
            "id": "SC-04",
            "title": "Cancellation with outstanding premium",
            "description": "Open billed amount or unearned vs earned premium creates a balance.",
            "type": "edge",
        },
        {
            "id": "SC-05",
            "title": "Cancellation while a claim is open",
            "description": "An open claim exists on the policy being cancelled.",
            "type": "edge",
        },
        {
            "id": "SC-06",
            "title": "Invalid cancellation effective date",
            "description": "Date is malformed, before inception, or otherwise not allowed by the stated rules.",
            "type": "boundary",
        },
        {
            "id": "SC-07",
            "title": "Regression after a mid-term endorsement",
            "description": "Policy was endorsed earlier in the term; cancellation must still apply to the current term state.",
            "type": "regression",
        },
    ],
    "test_cases": [
        {
            "id": "TC-01",
            "scenario_id": "SC-01",
            "title": "Mid-term cancel with valid date — policy moves to cancelled",
            "preconditions": [
                "Policy is in force",
                "No blocking outstanding legal hold is described",
            ],
            "steps": [
                "Submit a cancellation request with an effective date inside the current term",
                "Confirm the request",
            ],
            "expected_result": "Policy status is cancelled as of the requested date; a confirmation is produced.",
        },
        {
            "id": "TC-02",
            "scenario_id": "SC-02",
            "title": "Reject cancellation of an expired policy",
            "preconditions": ["Policy term has already ended"],
            "steps": ["Submit a cancellation request for the expired policy"],
            "expected_result": "Request is rejected with a clear reason; policy status is unchanged.",
        },
        {
            "id": "TC-03",
            "scenario_id": "SC-03",
            "title": "Cancel before the term starts",
            "preconditions": ["Policy is bound with a future inception date"],
            "steps": ["Request cancellation effective on or before inception"],
            "expected_result": "System either flat-cancels per stated rules or rejects with a reason — not a silent no-op.",
        },
        {
            "id": "TC-04",
            "scenario_id": "SC-04",
            "title": "Outstanding balance is visible on cancel",
            "preconditions": ["Policy has an unpaid billed amount"],
            "steps": ["Request cancellation and review the resulting balance"],
            "expected_result": "Any amount due or refund is calculated and shown; cancellation is not hidden because of money.",
        },
        {
            "id": "TC-05",
            "scenario_id": "SC-05",
            "title": "Open claim does not disappear on cancel",
            "preconditions": ["An open claim exists on the policy"],
            "steps": ["Request cancellation and inspect claim status"],
            "expected_result": "Claim remains visible and is not auto-closed solely because the policy cancelled.",
        },
        {
            "id": "TC-06",
            "scenario_id": "SC-06",
            "title": "Reject a blank or impossible cancellation date",
            "preconditions": ["Policy is in force"],
            "steps": ["Submit cancellation with a blank date, then with a date before policy inception"],
            "expected_result": "Each invalid date is rejected with field-level validation; policy stays in force.",
        },
        {
            "id": "TC-07",
            "scenario_id": "SC-07",
            "title": "Cancel after endorsement still uses current term state",
            "preconditions": ["Policy is in force", "A mid-term endorsement has already been issued"],
            "steps": ["Request cancellation of the endorsed policy with a valid date"],
            "expected_result": "Cancellation applies to the current endorsed term; prior endorsement is not silently dropped.",
        },
    ],
}

_TYPE_LINE = re.compile(r"Requested scenario types:\s*(.+)", re.IGNORECASE)
_SCENARIO_ID = re.compile(r"\bSC-\d+\b")


def _requested_types(prompt: str) -> list[str] | None:
    match = _TYPE_LINE.search(prompt)
    if not match:
        return None
    types = [part.strip().lower() for part in match.group(1).split(",") if part.strip()]
    return types or None


def _filter_scenarios(prompt: str) -> list[dict]:
    types = _requested_types(prompt)
    scenarios = list(CANNED_PACK["scenarios"])
    if types:
        filtered = [item for item in scenarios if item["type"] in types]
        if filtered:
            return filtered
    return scenarios


class FakeProvider(LLMProvider):
    def __init__(self, raw_json: str | None = None) -> None:
        self._raw_json = raw_json

    @property
    def model_id(self) -> str:
        return "fake-model"

    def generate_structured(self, prompt: str, json_schema: dict) -> str:
        if self._raw_json is not None:
            return self._raw_json

        required = set(json_schema.get("required") or [])
        scenarios = _filter_scenarios(prompt)
        scenario_ids = {item["id"] for item in scenarios}

        if "test_cases" in required and "scenarios" not in required:
            mentioned = set(_SCENARIO_ID.findall(prompt))
            wanted = mentioned or scenario_ids
            cases = [
                case
                for case in CANNED_PACK["test_cases"]
                if case["scenario_id"] in wanted
            ]
            return json.dumps({"test_cases": cases})

        if "scenarios" in required and "test_cases" not in required:
            return json.dumps(
                {
                    "summary": CANNED_PACK["summary"],
                    "assumptions": CANNED_PACK["assumptions"],
                    "scenarios": scenarios,
                }
            )

        cases = [
            case
            for case in CANNED_PACK["test_cases"]
            if case["scenario_id"] in scenario_ids
        ]
        return json.dumps(
            {
                "summary": CANNED_PACK["summary"],
                "assumptions": CANNED_PACK["assumptions"],
                "scenarios": scenarios,
                "test_cases": cases,
            }
        )
