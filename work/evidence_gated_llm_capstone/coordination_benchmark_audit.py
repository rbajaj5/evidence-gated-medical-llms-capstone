"""Synthetic coordination-benchmark audit for medical LLM assurance.

This experiment is inspired by Gessler et al.'s OvercookedV2 argument: a
benchmark can appear to test zero-shot coordination while mostly measuring state
coverage. For clinical LLM settings, the analogous failure is treating broad
chart/context coverage as proof of usable clinician-AI coordination.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SOURCE = "https://arxiv.org/abs/2503.17821"


@dataclass(frozen=True)
class CoordinationCase:
    case_id: str
    label: str
    state_coverage: float
    asymmetric_information: bool
    stochasticity: bool
    grounded_channel: bool
    test_time_protocol: bool
    implicit_action_demo: bool
    clinical_analogy: str


CASES = [
    CoordinationCase(
        case_id="C01",
        label="Fully observable kitchen-style benchmark after state augmentation",
        state_coverage=0.98,
        asymmetric_information=False,
        stochasticity=False,
        grounded_channel=False,
        test_time_protocol=False,
        implicit_action_demo=False,
        clinical_analogy="A prompt suite with broad chart states but no handoff asymmetry.",
    ),
    CoordinationCase(
        case_id="C02",
        label="Grounded communication under partial observability",
        state_coverage=0.97,
        asymmetric_information=True,
        stochasticity=True,
        grounded_channel=True,
        test_time_protocol=False,
        implicit_action_demo=False,
        clinical_analogy="A monitor where one role sees a lab trend and another role acts.",
    ),
    CoordinationCase(
        case_id="C03",
        label="Test-time protocol formation with feedback",
        state_coverage=0.97,
        asymmetric_information=True,
        stochasticity=True,
        grounded_channel=False,
        test_time_protocol=True,
        implicit_action_demo=False,
        clinical_analogy="A family-consent or shift-handoff protocol that must be formed online.",
    ),
    CoordinationCase(
        case_id="C04",
        label="Implicit demonstration through action",
        state_coverage=0.97,
        asymmetric_information=True,
        stochasticity=True,
        grounded_channel=False,
        test_time_protocol=True,
        implicit_action_demo=True,
        clinical_analogy="A clinician action, gesture, or note timing carries meaning not in text.",
    ),
    CoordinationCase(
        case_id="C05",
        label="Low coverage benchmark with no structural coordination challenge",
        state_coverage=0.62,
        asymmetric_information=False,
        stochasticity=False,
        grounded_channel=False,
        test_time_protocol=False,
        implicit_action_demo=False,
        clinical_analogy="A brittle prompt test that fails because common states are missing.",
    ),
]


def structural_coordination_score(case: CoordinationCase) -> int:
    return sum(
        [
            case.asymmetric_information,
            case.stochasticity,
            case.test_time_protocol,
            case.implicit_action_demo,
            case.asymmetric_information and not case.grounded_channel,
        ]
    )


def audit_case(case: CoordinationCase) -> dict[str, object]:
    coverage_gap = round(1.0 - case.state_coverage, 3)
    structural_score = structural_coordination_score(case)

    if case.state_coverage < 0.9 and structural_score == 0:
        action = "STRESS_TEST_STATE_COVERAGE"
        reason = "Failure can plausibly be explained by missing state coverage."
    elif case.state_coverage >= 0.9 and structural_score == 0:
        action = "DO_NOT_TREAT_AS_COORDINATION_BENCHMARK"
        reason = "High coverage with no asymmetry or stochasticity is too weak for coordination claims."
    elif case.state_coverage >= 0.9 and structural_score > 0:
        action = "REQUIRE_PROTOCOL_ASSURANCE"
        reason = "Coverage alone is insufficient once hidden information, stochasticity, or online protocols matter."
    else:
        action = "REQUIRE_COVERAGE_AND_PROTOCOL_ASSURANCE"
        reason = "Both missing state coverage and structural coordination difficulty are present."

    return {
        **asdict(case),
        "coverage_gap": coverage_gap,
        "structural_coordination_score": structural_score,
        "action": action,
        "reason": reason,
    }


def run() -> dict[str, object]:
    rows = [audit_case(case) for case in CASES]
    action_counts: dict[str, int] = {}
    for row in rows:
        action_counts[row["action"]] = action_counts.get(row["action"], 0) + 1

    summary = {
        "source": SOURCE,
        "case_count": len(rows),
        "action_counts": action_counts,
        "rows": rows,
        "capstone_interpretation": (
            "A medical LLM benchmark should distinguish ordinary state coverage "
            "from genuine clinician-AI coordination under asymmetric information, "
            "stochastic workflow, implicit communication, and test-time protocol formation."
        ),
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "coordination_benchmark_audit_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
