"""Synthetic residual-depletion ordering experiment for runtime budgets.

This module adapts the local PDF "Sequential Depletion Ordering with
Residual-Fraction Costs" into capstone tests. It is not clinical evidence. It
checks whether a medical LLM runtime monitor should treat event ordering as a
budgeted safety variable when clinician attention, audit time, compute, and
provenance checks are depleted sequentially.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def residual_fraction_cost(loads: tuple[float, ...], order: tuple[int, ...], reserve: float = 0.0) -> float:
    total = sum(loads)
    cost = 0.0
    processed = 0.0
    for index in order:
        residual = reserve + total - processed
        cost += loads[index] / residual
        processed += loads[index]
    return cost


def log_depletion_vector(loads: tuple[float, ...], order: tuple[int, ...], reserve: float) -> tuple[float, ...]:
    total = sum(loads)
    processed = 0.0
    out = []
    for index in order:
        before = reserve + total - processed
        after = before - loads[index]
        out.append(math.log(before / after))
        processed += loads[index]
    return tuple(out)


def convex_log_risk(loads: tuple[float, ...], order: tuple[int, ...], reserve: float, power: float = 2.0) -> float:
    return sum(d**power for d in log_depletion_vector(loads, order, reserve))


def network_depletion_delta(
    a: tuple[float, ...],
    b: tuple[float, ...],
    tail: tuple[float, ...],
    weights: tuple[float, ...],
) -> float:
    """Return cost(a,b)-cost(b,a) for a heterogeneous multi-resource pair."""
    delta = 0.0
    for ar, br, tr, wr in zip(a, b, tail, weights):
        denominator = (tr + ar + br) * (tr + ar) * (tr + br)
        delta += wr * ar * br * (ar - br) / denominator
    return delta


def run() -> dict[str, object]:
    # Synthetic action loads: tiny provenance check, small citation check,
    # medium endpoint classification, large clinician-attention review.
    loads = (1.0, 2.0, 5.0, 8.0)
    reserve = 3.0
    permutations = tuple(itertools.permutations(range(len(loads))))
    costs = {
        order: residual_fraction_cost(loads, order, reserve)
        for order in permutations
    }
    convex_risks = {
        order: convex_log_risk(loads, order, reserve)
        for order in permutations
    }
    increasing = tuple(sorted(range(len(loads)), key=loads.__getitem__))
    decreasing = tuple(reversed(increasing))

    best_raw = min(costs, key=costs.get)
    worst_raw = max(costs, key=costs.get)
    best_convex = min(convex_risks, key=convex_risks.get)
    worst_convex = max(convex_risks, key=convex_risks.get)

    # The example values mirror the PDF's multi-resource context-reversal
    # pattern: the same two vectors prefer opposite order in two tail states.
    a = (4.0, 1.0)
    b = (1.0, 3.0)
    weights = (1.0, 1.0)
    low_tail_delta = network_depletion_delta(a, b, (1.0, 1.0), weights)
    mixed_tail_delta = network_depletion_delta(a, b, (10.0, 1.0), weights)

    summary = {
        "source_pdf": "C:/Users/anaxe/Downloads/sequential_depletion_ordering.pdf",
        "loads": loads,
        "reserve": reserve,
        "permutation_count": len(permutations),
        "increasing_order": increasing,
        "decreasing_order": decreasing,
        "best_raw_order": best_raw,
        "worst_raw_order": worst_raw,
        "best_raw_cost": costs[best_raw],
        "worst_raw_cost": costs[worst_raw],
        "increasing_minimizes_raw_cost": best_raw == increasing,
        "decreasing_maximizes_raw_cost": worst_raw == decreasing,
        "best_convex_log_order": best_convex,
        "worst_convex_log_order": worst_convex,
        "best_convex_log_risk": convex_risks[best_convex],
        "worst_convex_log_risk": convex_risks[worst_convex],
        "decreasing_minimizes_convex_log_risk": best_convex == decreasing,
        "increasing_maximizes_convex_log_risk": worst_convex == increasing,
        "multi_resource_pair_a": a,
        "multi_resource_pair_b": b,
        "low_tail_delta_cost_a_then_b_minus_b_then_a": low_tail_delta,
        "mixed_tail_delta_cost_a_then_b_minus_b_then_a": mixed_tail_delta,
        "context_reversal_observed": low_tail_delta > 0 and mixed_tail_delta < 0,
        "runtime_interpretation": (
            "FIFO is useful for audit replay, but runtime budget decisions should be "
            "priority- and state-aware when clinician attention, audit time, compute, "
            "and provenance checks are depleted sequentially."
        ),
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "depletion_ordering_experiment_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
