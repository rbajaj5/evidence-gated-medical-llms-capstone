"""ZDD-style sparse family audit for evidence-gated LLM claim forms.

This is a compact implementation sketch, not a production ZDD package. It
builds a reduced zero-suppressed decision diagram over sparse evidence-feature
sets and checks whether observed claim states belong to pre-specified families.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from run_evidence_gate_stress_test import SCENARIOS, Scenario


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

FEATURE_ORDER = (
    "citation_verified",
    "citation_course_or_local",
    "citation_unverifiable",
    "endpoint_hard_outcome",
    "endpoint_validated_surrogate",
    "endpoint_surrogate",
    "endpoint_process",
    "endpoint_local_case",
    "endpoint_none",
    "design_pragmatic_rct",
    "design_rct",
    "design_validation",
    "design_observational",
    "design_case",
    "design_unverifiable",
    "population_match",
    "population_plausible",
    "population_mismatch",
    "population_temporal_shift",
    "population_unknown",
    "context_available",
    "context_partial",
    "context_missing",
    "context_material_missing",
    "context_simulation_available",
    "opportunity_addressed",
    "opportunity_low",
    "opportunity_unaddressed_high",
    "opportunity_unknown",
    "clinician_authority_retained",
    "clinician_filtering_possible",
    "clinician_handoff_missing",
    "public_health_boundary_needed",
    "chain_terminal_outcome",
    "chain_terminal_surrogate",
    "chain_terminal_process",
    "chain_terminal_local",
    "chain_deferred",
    "chain_no_terminal",
)


@dataclass(frozen=True)
class Node:
    var_index: int
    lo: int
    hi: int


class MiniZDD:
    ZERO = 0
    ONE = 1

    def __init__(self, feature_order: tuple[str, ...]):
        self.feature_order = feature_order
        self.feature_index = {feature: index for index, feature in enumerate(feature_order)}
        self.nodes: dict[int, Node] = {}
        self.unique: dict[Node, int] = {}
        self.next_id = 2

    def make_node(self, var_index: int, lo: int, hi: int) -> int:
        # Zero suppression: if including this feature cannot reach a valid set,
        # the node is equivalent to the branch where the feature is absent.
        if hi == self.ZERO:
            return lo
        node = Node(var_index, lo, hi)
        if node in self.unique:
            return self.unique[node]
        node_id = self.next_id
        self.next_id += 1
        self.nodes[node_id] = node
        self.unique[node] = node_id
        return node_id

    def build(self, family: set[frozenset[str]]) -> int:
        normalized = frozenset(frozenset(s) for s in family)

        @lru_cache(maxsize=None)
        def rec(index: int, subfamily: frozenset[frozenset[str]]) -> int:
            if not subfamily:
                return self.ZERO
            if index == len(self.feature_order):
                return self.ONE if frozenset() in subfamily else self.ZERO
            feature = self.feature_order[index]
            absent = frozenset(s for s in subfamily if feature not in s)
            present = frozenset(frozenset(x for x in s if x != feature) for s in subfamily if feature in s)
            lo = rec(index + 1, absent)
            hi = rec(index + 1, present)
            return self.make_node(index, lo, hi)

        return rec(0, normalized)

    def contains(self, root: int, subset: frozenset[str]) -> bool:
        unknown = subset.difference(self.feature_index)
        if unknown:
            return False
        node_id = root
        cursor = 0
        while node_id not in (self.ZERO, self.ONE):
            node = self.nodes[node_id]
            skipped = self.feature_order[cursor : node.var_index]
            if any(feature in subset for feature in skipped):
                return False
            feature = self.feature_order[node.var_index]
            node_id = node.hi if feature in subset else node.lo
            cursor = node.var_index + 1
        if node_id == self.ZERO:
            return False
        return not any(feature in subset for feature in self.feature_order[cursor:])

    def node_count(self) -> int:
        return len(self.nodes) + 2


def scenario_features(scenario: Scenario) -> frozenset[str]:
    features: set[str] = set()

    if scenario.citation_status == "verified":
        features.add("citation_verified")
    elif scenario.citation_status == "unverifiable":
        features.add("citation_unverifiable")
    else:
        features.add("citation_course_or_local")

    endpoint_map = {
        "hard_patient_outcome": "endpoint_hard_outcome",
        "validated_surrogate": "endpoint_validated_surrogate",
        "surrogate": "endpoint_surrogate",
        "process_or_workflow": "endpoint_process",
        "local_case_or_error_correction": "endpoint_local_case",
        "none": "endpoint_none",
    }
    features.add(endpoint_map[scenario.endpoint_type])

    design_map = {
        "pragmatic_patient_level_rct": "design_pragmatic_rct",
        "rct": "design_rct",
        "prospective_validation": "design_validation",
        "observational": "design_observational",
        "case_or_local_review": "design_case",
        "unverifiable": "design_unverifiable",
    }
    features.add(design_map[scenario.study_design])

    population_map = {
        "target_population_match": "population_match",
        "plausible_but_not_confirmed": "population_plausible",
        "population_mismatch": "population_mismatch",
        "temporal_shift": "population_temporal_shift",
        "unknown": "population_unknown",
        "case_specific": "population_match",
    }
    features.add(population_map[scenario.target_population_fit])

    context_map = {
        "clinical_context_available": "context_available",
        "clinical_context_partial": "context_partial",
        "clinical_context_missing": "context_missing",
        "material_context_missing": "context_material_missing",
        "simulation_context_available": "context_simulation_available",
    }
    features.add(context_map[scenario.context_status])

    opportunity_map = {
        "addressed": "opportunity_addressed",
        "low": "opportunity_low",
        "unaddressed_high": "opportunity_unaddressed_high",
        "unknown": "opportunity_unknown",
    }
    features.add(opportunity_map[scenario.opportunity_cost_status])

    authority_map = {
        "clinician_retains_authority": "clinician_authority_retained",
        "clinician_filtering_possible": "clinician_filtering_possible",
        "clinician_handoff_boundary_missing": "clinician_handoff_missing",
        "public_health_authority_boundary_needed": "public_health_boundary_needed",
    }
    features.add(authority_map[scenario.clinician_authority])

    chain_map = {
        "terminal_outcome_claim": "chain_terminal_outcome",
        "terminal_surrogate_claim": "chain_terminal_surrogate",
        "terminal_process_claim": "chain_terminal_process",
        "terminal_local_claim": "chain_terminal_local",
        "deferred_no_terminal_outcome": "chain_deferred",
        "no_terminal_evidence": "chain_no_terminal",
    }
    features.add(chain_map[scenario.evidence_chain_status])
    return frozenset(features)


def hard_outcome_claim_family() -> set[frozenset[str]]:
    return {
        frozenset(
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
        )
    }


def narrow_surrogate_family() -> set[frozenset[str]]:
    return {
        frozenset(
            {
                "citation_verified",
                "endpoint_surrogate",
                "design_rct",
                "population_plausible",
                "context_partial",
                "opportunity_unknown",
                "clinician_authority_retained",
                "chain_terminal_surrogate",
            }
        ),
        frozenset(
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
        frozenset(
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
        frozenset(
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
        frozenset(
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
    }


def bounded_training_family() -> set[frozenset[str]]:
    return {
        frozenset(
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
        )
    }


def runtime_ordering_family() -> set[frozenset[str]]:
    return {
        frozenset(
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
        )
    }


def orthogonal_projection_family() -> set[frozenset[str]]:
    return {
        frozenset(
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
        )
    }


def consent_boundary_family() -> set[frozenset[str]]:
    return {
        frozenset(
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
        )
    }


def provenance_gap_family() -> set[frozenset[str]]:
    return {
        frozenset(
            {
                "citation_course_or_local",
                "endpoint_none",
                "design_case",
                "population_unknown",
                "context_missing",
                "opportunity_unknown",
                "clinician_authority_retained",
                "chain_no_terminal",
            }
        ),
        frozenset(
            {
                "citation_verified",
                "endpoint_none",
                "design_unverifiable",
                "population_unknown",
                "context_missing",
                "opportunity_unknown",
                "clinician_authority_retained",
                "chain_no_terminal",
            }
        ),
    }


def observed_stress_family() -> set[frozenset[str]]:
    return {scenario_features(s) for s in SCENARIOS}


def run() -> dict[str, object]:
    zdd = MiniZDD(FEATURE_ORDER)
    observed = observed_stress_family()
    observed_root = zdd.build(observed)
    observed_membership = {
        scenario.scenario_id: zdd.contains(observed_root, scenario_features(scenario))
        for scenario in SCENARIOS
    }

    hard_family = hard_outcome_claim_family()
    hard_zdd = MiniZDD(FEATURE_ORDER)
    hard_root = hard_zdd.build(hard_family)

    surrogate_family = narrow_surrogate_family()
    surrogate_zdd = MiniZDD(FEATURE_ORDER)
    surrogate_root = surrogate_zdd.build(surrogate_family)

    s02_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S02"))
    s03_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S03"))
    s13_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S13"))
    s14_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S14"))
    s15_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S15"))
    s16_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S16"))
    s17_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S17"))
    s18_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S18"))
    s19_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S19"))
    s21_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S21"))
    s22_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S22"))
    s23_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S23"))
    s24_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S24"))
    s25_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S25"))
    s26_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S26"))
    s27_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S27"))
    s28_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S28"))
    s29_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S29"))
    s30_features = scenario_features(next(s for s in SCENARIOS if s.scenario_id == "S30"))

    training_family = bounded_training_family()
    training_zdd = MiniZDD(FEATURE_ORDER)
    training_root = training_zdd.build(training_family)

    ordering_family = runtime_ordering_family()
    ordering_zdd = MiniZDD(FEATURE_ORDER)
    ordering_root = ordering_zdd.build(ordering_family)

    projection_family = orthogonal_projection_family()
    projection_zdd = MiniZDD(FEATURE_ORDER)
    projection_root = projection_zdd.build(projection_family)

    consent_family = consent_boundary_family()
    consent_zdd = MiniZDD(FEATURE_ORDER)
    consent_root = consent_zdd.build(consent_family)

    provenance_family = provenance_gap_family()
    provenance_zdd = MiniZDD(FEATURE_ORDER)
    provenance_root = provenance_zdd.build(provenance_family)

    summary = {
        "feature_universe_size": len(FEATURE_ORDER),
        "observed_family_size": len(observed),
        "observed_zdd_node_count": zdd.node_count(),
        "naive_observed_trie_upper_bound": len(observed) * len(FEATURE_ORDER) + 2,
        "observed_membership_all_true": all(observed_membership.values()),
        "observed_membership": observed_membership,
        "hard_outcome_family_size": len(hard_family),
        "hard_outcome_zdd_node_count": hard_zdd.node_count(),
        "s03_hard_outcome_allowed": hard_zdd.contains(hard_root, s03_features),
        "s02_hard_outcome_allowed": hard_zdd.contains(hard_root, s02_features),
        "surrogate_family_size": len(surrogate_family),
        "surrogate_zdd_node_count": surrogate_zdd.node_count(),
        "s02_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s02_features),
        "s13_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s13_features),
        "s14_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s14_features),
        "s16_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s16_features),
        "s22_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s22_features),
        "s24_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s24_features),
        "s27_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s27_features),
        "s29_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s29_features),
        "s17_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s17_features),
        "s19_surrogate_allowed": surrogate_zdd.contains(surrogate_root, s19_features),
        "bounded_training_family_size": len(training_family),
        "bounded_training_zdd_node_count": training_zdd.node_count(),
        "s15_bounded_training_allowed": training_zdd.contains(training_root, s15_features),
        "s14_bounded_training_allowed": training_zdd.contains(training_root, s14_features),
        "s18_bounded_training_allowed": training_zdd.contains(training_root, s18_features),
        "runtime_ordering_family_size": len(ordering_family),
        "runtime_ordering_zdd_node_count": ordering_zdd.node_count(),
        "s23_runtime_ordering_allowed": ordering_zdd.contains(ordering_root, s23_features),
        "s15_runtime_ordering_allowed": ordering_zdd.contains(ordering_root, s15_features),
        "orthogonal_projection_family_size": len(projection_family),
        "orthogonal_projection_zdd_node_count": projection_zdd.node_count(),
        "s25_orthogonal_projection_allowed": projection_zdd.contains(projection_root, s25_features),
        "s15_orthogonal_projection_allowed": projection_zdd.contains(projection_root, s15_features),
        "consent_boundary_family_size": len(consent_family),
        "consent_boundary_zdd_node_count": consent_zdd.node_count(),
        "s26_consent_boundary_allowed": consent_zdd.contains(consent_root, s26_features),
        "s15_consent_boundary_allowed": consent_zdd.contains(consent_root, s15_features),
        "provenance_gap_family_size": len(provenance_family),
        "provenance_gap_zdd_node_count": provenance_zdd.node_count(),
        "s21_provenance_gap_allowed": provenance_zdd.contains(provenance_root, s21_features),
        "s28_provenance_gap_allowed": provenance_zdd.contains(provenance_root, s28_features),
        "s30_provenance_gap_allowed": provenance_zdd.contains(provenance_root, s30_features),
        "event_ordering_policy": {
            "audit_log": "FIFO",
            "zdd_construction": "recursive LIFO/backtracking",
            "zdd_membership": "fixed variable order",
            "runtime_safety_decision": "priority-ordered boundary crossing",
        },
        "interpretation": (
            "A medical LLM response activates a sparse subset of evidence features. "
            "ZDD-style representations can compactly store allowed claim families and "
            "block unsafe promotions without enumerating the full power set."
        ),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "zdd_sparse_claim_family_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
