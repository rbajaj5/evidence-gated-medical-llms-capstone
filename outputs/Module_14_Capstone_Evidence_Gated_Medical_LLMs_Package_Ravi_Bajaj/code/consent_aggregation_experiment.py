"""Synthetic genomic-consent aggregation checks.

This is a nonclinical toy model. It tests an assurance claim: ranked choices
from relatives should not be collapsed into a single family authorization when
pairwise preferences cycle. The safe runtime output preserves individual
permissions, vetoes, and partial-use constraints.
"""

from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

OPTIONS = (
    "full_raw_genome_reuse",
    "trait_specific_partial_inclusion",
    "audit_only_no_reuse",
)

RANKINGS = {
    "relative_1": (
        "full_raw_genome_reuse",
        "trait_specific_partial_inclusion",
        "audit_only_no_reuse",
    ),
    "relative_2": (
        "trait_specific_partial_inclusion",
        "audit_only_no_reuse",
        "full_raw_genome_reuse",
    ),
    "relative_3": (
        "audit_only_no_reuse",
        "full_raw_genome_reuse",
        "trait_specific_partial_inclusion",
    ),
}

CONSENT_CAPS = {
    "relative_1": {"full_raw_genome_reuse", "trait_specific_partial_inclusion", "audit_only_no_reuse"},
    "relative_2": {"trait_specific_partial_inclusion", "audit_only_no_reuse"},
    "relative_3": {"trait_specific_partial_inclusion", "audit_only_no_reuse"},
}

DISTRIBUTION_POTENTIAL = {
    "full_raw_genome_reuse": 0.90,
    "trait_specific_partial_inclusion": 0.74,
    "audit_only_no_reuse": 0.55,
}

PRIVACY_COSTS = {
    "full_raw_genome_reuse": {"epsilon": 6.0, "delta": 1e-5},
    "trait_specific_partial_inclusion": {"epsilon": 0.8, "delta": 1e-7},
    "audit_only_no_reuse": {"epsilon": 0.05, "delta": 0.0},
}

RUNTIME_BUDGET = {"epsilon": 1.0, "delta": 1e-6}


def prefers(ranking: tuple[str, ...], a: str, b: str) -> bool:
    return ranking.index(a) < ranking.index(b)


def pairwise_majorities() -> dict[str, object]:
    out: dict[str, object] = {}
    for a, b in combinations(OPTIONS, 2):
        a_votes = sum(prefers(ranking, a, b) for ranking in RANKINGS.values())
        b_votes = len(RANKINGS) - a_votes
        winner = a if a_votes > b_votes else b
        loser = b if winner == a else a
        out[f"{a}__vs__{b}"] = {
            "winner": winner,
            "loser": loser,
            "margin": abs(a_votes - b_votes),
            "votes_for_a": a_votes,
            "votes_for_b": b_votes,
        }
    return out


def has_condorcet_cycle(majorities: dict[str, object]) -> bool:
    beats = {(item["winner"], item["loser"]) for item in majorities.values()}
    return (
        ("full_raw_genome_reuse", "trait_specific_partial_inclusion") in beats
        and ("trait_specific_partial_inclusion", "audit_only_no_reuse") in beats
        and ("audit_only_no_reuse", "full_raw_genome_reuse") in beats
    )


def feasible_under_all_individual_caps(option: str) -> bool:
    return all(option in caps for caps in CONSENT_CAPS.values())


def softmax_allocation(beta: float) -> dict[str, float]:
    weights = {
        option: math.exp(beta * DISTRIBUTION_POTENTIAL[option])
        for option in OPTIONS
        if feasible_under_all_individual_caps(option)
    }
    total = sum(weights.values())
    return {option: value / total for option, value in weights.items()}


def entropy(probs: dict[str, float]) -> float:
    return -sum(p * math.log(p) for p in probs.values() if p > 0)


def within_runtime_privacy_budget(option: str) -> bool:
    cost = PRIVACY_COSTS[option]
    return cost["epsilon"] <= RUNTIME_BUDGET["epsilon"] and cost["delta"] <= RUNTIME_BUDGET["delta"]


def composed_privacy_loss(options: tuple[str, ...]) -> dict[str, float]:
    return {
        "epsilon": sum(PRIVACY_COSTS[option]["epsilon"] for option in options),
        "delta": sum(PRIVACY_COSTS[option]["delta"] for option in options),
    }


def group_privacy_upper_bound(option: str, group_size: int) -> dict[str, float]:
    cost = PRIVACY_COSTS[option]
    return {
        "epsilon": group_size * cost["epsilon"],
        "delta_linear_upper_bound": group_size * cost["delta"],
    }


def run() -> dict[str, object]:
    majorities = pairwise_majorities()
    cycle = has_condorcet_cycle(majorities)
    feasible = {option: feasible_under_all_individual_caps(option) for option in OPTIONS}
    within_budget = {option: within_runtime_privacy_budget(option) for option in OPTIONS}
    runtime_safe = {
        option: feasible[option] and within_budget[option]
        for option in OPTIONS
    }
    beta_rows = []
    for beta in (0.0, 1.0, 4.0):
        probs = softmax_allocation(beta)
        beta_rows.append(
            {
                "beta": beta,
                "allocation": probs,
                "entropy": entropy(probs),
                "support_size": len(probs),
            }
        )

    summary = {
        "source": "Arrow social-choice stress case plus Boltzmann/softmax allocation audit",
        "option_count": len(OPTIONS),
        "relative_count": len(RANKINGS),
        "pairwise_majorities": majorities,
        "condorcet_cycle_detected": cycle,
        "feasible_under_all_individual_caps": feasible,
        "within_runtime_privacy_budget": within_budget,
        "runtime_safe_options": runtime_safe,
        "runtime_budget": RUNTIME_BUDGET,
        "privacy_costs": PRIVACY_COSTS,
        "partial_plus_audit_composed_loss": composed_privacy_loss(
            ("trait_specific_partial_inclusion", "audit_only_no_reuse")
        ),
        "group_privacy_bound_for_partial_three_relatives": group_privacy_upper_bound(
            "trait_specific_partial_inclusion", len(RANKINGS)
        ),
        "full_raw_release_allowed": feasible["full_raw_genome_reuse"],
        "partial_inclusion_allowed": feasible["trait_specific_partial_inclusion"],
        "audit_only_allowed": feasible["audit_only_no_reuse"],
        "full_raw_release_runtime_safe": runtime_safe["full_raw_genome_reuse"],
        "partial_inclusion_runtime_safe": runtime_safe["trait_specific_partial_inclusion"],
        "audit_only_runtime_safe": runtime_safe["audit_only_no_reuse"],
        "safe_runtime_action": "PRESERVE_CONSENT_BOUNDARY",
        "boltzmann_beta_rows": beta_rows,
        "entropy_decreases_with_beta": beta_rows[0]["entropy"] >= beta_rows[-1]["entropy"],
        "interpretation": (
            "A ranked family profile can cycle, and individual consent caps can make full raw release infeasible. "
            "The safe monitor preserves per-relative constraints and allows only options that are both consent-feasible "
            "and inside the runtime privacy budget; softmax/Boltzmann allocation is an auditable budget policy inside "
            "the feasible set, not a substitute for consent."
        ),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "consent_aggregation_experiment_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
