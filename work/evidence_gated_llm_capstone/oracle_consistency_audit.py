"""Oracle-consistency audit for strong-performance medical LLM claims.

Inspired by Kong, Ram, and Yu (2026), this synthetic experiment separates
"strong play" from "perfect play." In the capstone setting, the analogous
distinction is high benchmark score versus stepwise evidence consistency: a
clinician-facing LLM can be useful while still failing the exact claim trajectory
needed for safe medical reasoning.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SOURCE = "https://arxiv.org/abs/2607.08984"


@dataclass(frozen=True)
class OracleRun:
    run_id: str
    domain: str
    model: str
    full_trace_perfect: float
    full_trace_match: float
    sampled_state_match: float
    auxiliary_oracle_supervision: bool
    representation_only_change: bool
    clinical_analogy: str


RUNS = [
    OracleRun(
        run_id="O01",
        domain="Chomp 9x10",
        model="Vanilla AlphaZero",
        full_trace_perfect=0.000,
        full_trace_match=0.609,
        sampled_state_match=0.500,
        auxiliary_oracle_supervision=False,
        representation_only_change=False,
        clinical_analogy="A medical LLM with decent aggregate answers but unstable evidence-chain steps.",
    ),
    OracleRun(
        run_id="O02",
        domain="Chomp 9x10",
        model="Multi-frame AlphaZero",
        full_trace_perfect=0.000,
        full_trace_match=0.483,
        sampled_state_match=0.176,
        auxiliary_oracle_supervision=False,
        representation_only_change=True,
        clinical_analogy="Adding more context frames without changing supervision can still miss the invariant.",
    ),
    OracleRun(
        run_id="O03",
        domain="Chomp 9x10",
        model="AZAL",
        full_trace_perfect=0.567,
        full_trace_match=0.948,
        sampled_state_match=1.000,
        auxiliary_oracle_supervision=True,
        representation_only_change=False,
        clinical_analogy="Auxiliary evidence labels can greatly improve but not fully certify trajectory safety.",
    ),
    OracleRun(
        run_id="O04",
        domain="Chomp 10x11",
        model="AZAL",
        full_trace_perfect=1.000,
        full_trace_match=1.000,
        sampled_state_match=0.829,
        auxiliary_oracle_supervision=True,
        representation_only_change=False,
        clinical_analogy="Perfect traced cases still need random-start or out-of-trajectory auditing.",
    ),
    OracleRun(
        run_id="O05",
        domain="Connect Four",
        model="Vanilla AlphaZero",
        full_trace_perfect=0.000,
        full_trace_match=0.785,
        sampled_state_match=0.589,
        auxiliary_oracle_supervision=False,
        representation_only_change=False,
        clinical_analogy="High practical success can coexist with immediate non-oracle reasoning steps.",
    ),
    OracleRun(
        run_id="O06",
        domain="Connect Four",
        model="AZAL",
        full_trace_perfect=0.000,
        full_trace_match=0.849,
        sampled_state_match=0.768,
        auxiliary_oracle_supervision=True,
        representation_only_change=False,
        clinical_analogy="Auxiliary supervision improves oracle match but does not eliminate runtime monitoring.",
    ),
]


def audit_run(run: OracleRun) -> dict[str, object]:
    if run.representation_only_change and run.full_trace_match < 0.5:
        action = "DO_NOT_TREAT_MORE_CONTEXT_AS_SUPERVISION"
    elif run.full_trace_perfect == 1.0 and run.sampled_state_match < 1.0:
        action = "REQUIRE_RANDOM_START_ORACLE_AUDIT"
    elif run.auxiliary_oracle_supervision and run.full_trace_perfect < 1.0:
        action = "ALLOW_WITH_RUNTIME_ORACLE_MONITOR"
    elif run.full_trace_perfect == 0.0 and run.full_trace_match >= 0.75:
        action = "DO_NOT_EQUATE_STRONG_WITH_ORACLE_SAFE"
    else:
        action = "REQUIRE_AUXILIARY_SUPERVISION"

    oracle_gap = round(1.0 - run.full_trace_perfect, 3)
    aggregate_gap = round(1.0 - run.full_trace_match, 3)
    sampled_gap = round(1.0 - run.sampled_state_match, 3)

    return {
        **asdict(run),
        "oracle_gap": oracle_gap,
        "aggregate_gap": aggregate_gap,
        "sampled_gap": sampled_gap,
        "action": action,
    }


def run() -> dict[str, object]:
    rows = [audit_run(item) for item in RUNS]
    action_counts: dict[str, int] = {}
    for row in rows:
        action_counts[row["action"]] = action_counts.get(row["action"], 0) + 1

    azal_rows = [row for row in rows if row["auxiliary_oracle_supervision"]]
    vanilla_rows = [
        row
        for row in rows
        if row["model"] == "Vanilla AlphaZero" and row["domain"] in {"Chomp 9x10", "Connect Four"}
    ]

    summary = {
        "source": SOURCE,
        "case_count": len(rows),
        "action_counts": action_counts,
        "mean_vanilla_full_trace_match": round(
            sum(row["full_trace_match"] for row in vanilla_rows) / len(vanilla_rows), 3
        ),
        "mean_azal_full_trace_match": round(
            sum(row["full_trace_match"] for row in azal_rows) / len(azal_rows), 3
        ),
        "rows": rows,
        "capstone_interpretation": (
            "Aggregate strength, extra context, and fluent planning are insufficient "
            "unless the claim trajectory remains oracle-consistent under runtime audit."
        ),
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "oracle_consistency_audit_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
