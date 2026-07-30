"""Model selection for evidence-gated medical LLM claim forms.

The monitor chooses among candidate claim models. It selects the least unsafe
claim form that fits the evidence, using an information-criterion style loss:
missing evidence, forbidden crossings, model complexity, nested-chain burden,
and authority risk are all penalized.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from run_evidence_gate_stress_test import SCENARIOS, Scenario
from zdd_sparse_claim_family import scenario_features


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


@dataclass(frozen=True)
class ClaimModel:
    name: str
    action: str
    required: frozenset[str]
    forbidden: frozenset[str]
    complexity: int
    nested_burden: int
    authority_risk: int
    description: str


BLOCKERS = frozenset(
    {
        "citation_unverifiable",
        "context_missing",
        "context_material_missing",
        "population_mismatch",
        "population_temporal_shift",
        "opportunity_unaddressed_high",
        "clinician_filtering_possible",
        "clinician_handoff_missing",
        "public_health_boundary_needed",
        "chain_deferred",
        "chain_no_terminal",
    }
)


CLAIM_MODELS = [
    ClaimModel(
        name="deny_unverifiable_citation",
        action="DENY_CITATION",
        required=frozenset({"citation_unverifiable"}),
        forbidden=frozenset(),
        complexity=1,
        nested_burden=0,
        authority_risk=0,
        description="Deny claims based on unverifiable citation.",
    ),
    ClaimModel(
        name="abstain_deferred_chain",
        action="ABSTAIN_EVIDENCE_CHAIN",
        required=frozenset({"chain_deferred"}),
        forbidden=frozenset(),
        complexity=1,
        nested_burden=2,
        authority_risk=0,
        description="Abstain when the evidence chain never terminates in the requested outcome.",
    ),
    ClaimModel(
        name="abstain_context_missing",
        action="ABSTAIN_CONTEXT",
        required=frozenset({"context_material_missing"}),
        forbidden=frozenset(),
        complexity=1,
        nested_burden=1,
        authority_risk=1,
        description="Abstain when material or handoff context is missing.",
    ),
    ClaimModel(
        name="abstain_provenance_gap",
        action="ABSTAIN_PROVENANCE",
        required=frozenset({"chain_no_terminal", "endpoint_none"}),
        forbidden=frozenset({"citation_unverifiable"}),
        complexity=1,
        nested_burden=0,
        authority_risk=0,
        description="Use audit-only mode when a source artifact has no terminal clinical evidence.",
    ),
    ClaimModel(
        name="abstain_transport_gap",
        action="ABSTAIN_TRANSPORT",
        required=frozenset({"population_mismatch"}),
        forbidden=frozenset({"citation_unverifiable"}),
        complexity=2,
        nested_burden=1,
        authority_risk=1,
        description="Abstain from transporting evidence across unmatched populations.",
    ),
    ClaimModel(
        name="stress_test_temporal_shift",
        action="STRESS_TEST_GENERALIZATION",
        required=frozenset({"population_temporal_shift"}),
        forbidden=frozenset({"citation_unverifiable"}),
        complexity=2,
        nested_burden=1,
        authority_risk=1,
        description="Route temporal shift to stress testing rather than prediction.",
    ),
    ClaimModel(
        name="abstain_opportunity_cost",
        action="ABSTAIN_OPPORTUNITY_COST",
        required=frozenset({"opportunity_unaddressed_high"}),
        forbidden=frozenset({"citation_unverifiable", "context_simulation_available"}),
        complexity=2,
        nested_burden=1,
        authority_risk=1,
        description="Abstain when opportunity cost is high and unaddressed.",
    ),
    ClaimModel(
        name="workflow_diagnosis",
        action="ESCALATE_WORKFLOW_DIAGNOSIS",
        required=frozenset({"clinician_filtering_possible"}),
        forbidden=frozenset({"citation_unverifiable"}),
        complexity=2,
        nested_burden=1,
        authority_risk=1,
        description="Treat low acceptance as possible clinician filtering.",
    ),
    ClaimModel(
        name="bounded_second_reader",
        action="ALLOW_BOUNDED_SECOND_READER",
        required=frozenset(
            {
                "endpoint_local_case",
                "design_case",
                "population_match",
                "context_available",
                "opportunity_low",
                "clinician_authority_retained",
                "chain_terminal_local",
            }
        ),
        forbidden=frozenset({"citation_unverifiable"}),
        complexity=2,
        nested_burden=0,
        authority_risk=1,
        description="Allow local second-reader assistance without population-level outcome claim.",
    ),
    ClaimModel(
        name="narrow_surrogate_claim",
        action="NARROW_TO_SURROGATE",
        required=frozenset({"citation_verified", "endpoint_surrogate", "chain_terminal_surrogate"}),
        forbidden=BLOCKERS.union({"design_observational"}),
        complexity=3,
        nested_burden=1,
        authority_risk=1,
        description="Permit only a surrogate/process-limited claim.",
    ),
    ClaimModel(
        name="local_audio_surrogate_claim",
        action="NARROW_TO_SURROGATE",
        required=frozenset(
            {
                "citation_course_or_local",
                "endpoint_surrogate",
                "design_validation",
                "population_plausible",
                "context_partial",
                "opportunity_unknown",
                "clinician_authority_retained",
                "chain_terminal_surrogate",
            }
        ),
        forbidden=BLOCKERS,
        complexity=3,
        nested_burden=1,
        authority_risk=1,
        description="Permit technical audio/captioning benchmark claims only as surrogate evidence.",
    ),
    ClaimModel(
        name="observational_mechanism_surrogate_claim",
        action="NARROW_TO_SURROGATE",
        required=frozenset(
            {
                "citation_verified",
                "endpoint_surrogate",
                "design_observational",
                "population_plausible",
                "context_partial",
                "opportunity_unknown",
                "clinician_authority_retained",
                "chain_terminal_surrogate",
            }
        ),
        forbidden=BLOCKERS,
        complexity=3,
        nested_burden=1,
        authority_risk=1,
        description="Permit observational mechanism, association, or wearable physiology language only as surrogate evidence.",
    ),
    ClaimModel(
        name="hospital_genetics_triage_support",
        action="NARROW_TO_SURROGATE",
        required=frozenset(
            {
                "citation_verified",
                "endpoint_process",
                "design_validation",
                "population_plausible",
                "context_partial",
                "opportunity_addressed",
                "clinician_authority_retained",
                "chain_terminal_process",
            }
        ),
        forbidden=BLOCKERS,
        complexity=3,
        nested_burden=1,
        authority_risk=1,
        description="Permit recurring hospital genetics support only as triage, routing, documentation, or audit evidence.",
    ),
    ClaimModel(
        name="bounded_telemedicine_training_simulation",
        action="ALLOW_BOUNDED_TRAINING_SIMULATION",
        required=frozenset(
            {
                "citation_course_or_local",
                "endpoint_process",
                "design_case",
                "population_match",
                "context_simulation_available",
                "opportunity_low",
                "clinician_authority_retained",
                "chain_terminal_process",
            }
        ),
        forbidden=BLOCKERS,
        complexity=3,
        nested_burden=0,
        authority_risk=1,
        description="Allow synthetic telemedicine practice without clinical outcome or treatment claims.",
    ),
    ClaimModel(
        name="runtime_budget_ordering_stress_test",
        action="STRESS_TEST_ORDERING",
        required=frozenset(
            {
                "citation_course_or_local",
                "endpoint_process",
                "design_case",
                "population_match",
                "context_simulation_available",
                "opportunity_unaddressed_high",
                "clinician_authority_retained",
                "chain_terminal_process",
            }
        ),
        forbidden=frozenset({"citation_unverifiable"}),
        complexity=3,
        nested_burden=2,
        authority_risk=1,
        description="Stress-test runtime action ordering when scarce budgets are depleted sequentially.",
    ),
    ClaimModel(
        name="orthogonal_projection_confounding_stress_test",
        action="STRESS_TEST_CONFOUNDING",
        required=frozenset(
            {
                "citation_course_or_local",
                "endpoint_process",
                "design_case",
                "population_match",
                "context_simulation_available",
                "opportunity_unknown",
                "clinician_authority_retained",
                "chain_terminal_process",
            }
        ),
        forbidden=frozenset({"citation_unverifiable"}),
        complexity=3,
        nested_burden=2,
        authority_risk=1,
        description="Stress-test whether latent/residual signal is orthogonal to known design covariates.",
    ),
    ClaimModel(
        name="family_consent_boundary_audit",
        action="PRESERVE_CONSENT_BOUNDARY",
        required=frozenset(
            {
                "citation_course_or_local",
                "endpoint_process",
                "design_case",
                "population_unknown",
                "context_simulation_available",
                "opportunity_unknown",
                "clinician_authority_retained",
                "chain_terminal_process",
            }
        ),
        forbidden=frozenset({"citation_unverifiable"}),
        complexity=3,
        nested_burden=2,
        authority_risk=1,
        description="Preserve individual genomic-consent boundaries when ranked family preferences do not aggregate safely.",
    ),
    ClaimModel(
        name="validated_surrogate_with_confirmation",
        action="NARROW_WITH_CONFIRMATION",
        required=frozenset(
            {
                "citation_verified",
                "endpoint_validated_surrogate",
                "design_rct",
                "population_match",
                "context_available",
                "opportunity_addressed",
                "clinician_authority_retained",
                "chain_terminal_surrogate",
            }
        ),
        forbidden=frozenset({"citation_unverifiable"}),
        complexity=4,
        nested_burden=1,
        authority_risk=1,
        description="Allow validated-surrogate claim with confirmatory outcome obligation.",
    ),
    ClaimModel(
        name="hard_outcome_pragmatic_rct",
        action="ALLOW_CAUTIOUS_CLINICIAN_SUMMARY",
        required=frozenset(
            {
                "citation_verified",
                "endpoint_hard_outcome",
                "design_pragmatic_rct",
                "population_match",
                "context_available",
                "opportunity_addressed",
                "clinician_authority_retained",
                "chain_terminal_outcome",
            }
        ),
        forbidden=BLOCKERS,
        complexity=5,
        nested_burden=1,
        authority_risk=2,
        description="Permit cautious patient-outcome summary.",
    ),
]


def model_loss(model: ClaimModel, features: frozenset[str]) -> dict[str, object]:
    missing = model.required.difference(features)
    forbidden_present = model.forbidden.intersection(features)
    # Large penalties keep disallowed crossings from winning merely because the
    # candidate model is otherwise simple.
    loss = (
        100 * len(missing)
        + 250 * len(forbidden_present)
        + 2 * model.complexity
        + 5 * model.nested_burden
        + 8 * model.authority_risk
    )
    return {
        "model": model.name,
        "action": model.action,
        "loss": loss,
        "missing": sorted(missing),
        "forbidden_present": sorted(forbidden_present),
        "complexity": model.complexity,
        "nested_burden": model.nested_burden,
        "authority_risk": model.authority_risk,
    }


def select_claim_model(scenario: Scenario) -> dict[str, object]:
    features = scenario_features(scenario)
    losses = [model_loss(model, features) for model in CLAIM_MODELS]
    winner = min(losses, key=lambda item: (item["loss"], item["complexity"], item["model"]))
    return {
        "scenario_id": scenario.scenario_id,
        "label": scenario.label,
        "expected_action": scenario.expected_action,
        "selected_action": winner["action"],
        "selected_model": winner["model"],
        "selected_loss": winner["loss"],
        "matches_expected": winner["action"] == scenario.expected_action,
        "features": sorted(features),
        "top_losses": sorted(losses, key=lambda item: (item["loss"], item["complexity"], item["model"]))[:4],
    }


def run() -> dict[str, object]:
    rows = [select_claim_model(scenario) for scenario in SCENARIOS]
    summary = {
        "scenario_count": len(rows),
        "matched_expected_count": sum(1 for row in rows if row["matches_expected"]),
        "all_matched_expected": all(row["matches_expected"] for row in rows),
        "candidate_model_count": len(CLAIM_MODELS),
        "model_selection_rule": (
            "Select the claim model with minimum information-criterion style loss, "
            "penalizing missing evidence, forbidden boundary crossings, complexity, "
            "nested dependency burden, and authority risk."
        ),
        "fifo_lifo_policy": (
            "FIFO preserves audit replay; LIFO/backtracking is acceptable for search or "
            "diagram construction; runtime safety decisions are priority-ordered by "
            "boundary-crossing risk."
        ),
        "scenario_rows": rows,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "model_selection_claim_policy_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
