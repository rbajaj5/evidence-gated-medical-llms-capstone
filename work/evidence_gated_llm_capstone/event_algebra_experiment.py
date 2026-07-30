"""Finite event-algebra checks for runtime assurance.

In measure theory and probability, an event is a measurable subset of the
sample space. This file uses a finite sample space of synthetic runtime
histories, so every subset is measurable. A "plan" is then a rule that maps
events, such as unsafe promotion or privacy-budget exceedance, to runtime
actions.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

ENDPOINTS = ("hard_outcome", "surrogate", "process")
CITATIONS = ("verified", "unverifiable")
POPULATIONS = ("match", "mismatch")
PRIVACY = ("within_budget", "budget_exceeded")
CONSENT = ("boundary_preserved", "boundary_collapsed")
ACTIONS = ("hard_claim", "narrowed_claim", "audit_only")


def histories() -> list[dict[str, str]]:
    return [
        {
            "endpoint": endpoint,
            "citation": citation,
            "population": population,
            "privacy": privacy,
            "consent": consent,
            "action": action,
        }
        for endpoint, citation, population, privacy, consent, action in itertools.product(
            ENDPOINTS, CITATIONS, POPULATIONS, PRIVACY, CONSENT, ACTIONS
        )
    ]


def raw_weight(history: dict[str, str]) -> float:
    weight = 1.0
    if history["endpoint"] == "hard_outcome":
        weight *= 0.7
    if history["citation"] == "unverifiable":
        weight *= 0.35
    if history["population"] == "mismatch":
        weight *= 0.45
    if history["privacy"] == "budget_exceeded":
        weight *= 0.25
    if history["consent"] == "boundary_collapsed":
        weight *= 0.30
    if history["action"] == "hard_claim":
        weight *= 0.50
    return weight


def event(omega: list[dict[str, str]], predicate: Callable[[dict[str, str]], bool]) -> frozenset[int]:
    return frozenset(i for i, history in enumerate(omega) if predicate(history))


def probability(event_set: frozenset[int], masses: list[float]) -> float:
    return sum(masses[i] for i in event_set)


def run() -> dict[str, object]:
    omega = histories()
    weights = [raw_weight(history) for history in omega]
    total = sum(weights)
    masses = [weight / total for weight in weights]
    universe = frozenset(range(len(omega)))

    unsafe_promotion = event(
        omega,
        lambda h: h["action"] == "hard_claim"
        and (
            h["endpoint"] != "hard_outcome"
            or h["citation"] == "unverifiable"
            or h["population"] == "mismatch"
            or h["privacy"] == "budget_exceeded"
            or h["consent"] == "boundary_collapsed"
        ),
    )
    privacy_exceeded = event(omega, lambda h: h["privacy"] == "budget_exceeded")
    consent_collapsed = event(omega, lambda h: h["consent"] == "boundary_collapsed")
    audit_trigger = privacy_exceeded | consent_collapsed
    narrowed_or_audit = event(omega, lambda h: h["action"] in {"narrowed_claim", "audit_only"})
    safe_stop = audit_trigger & narrowed_or_audit

    union_identity_lhs = probability(privacy_exceeded | consent_collapsed, masses)
    union_identity_rhs = (
        probability(privacy_exceeded, masses)
        + probability(consent_collapsed, masses)
        - probability(privacy_exceeded & consent_collapsed, masses)
    )
    complement_identity = probability(unsafe_promotion, masses) + probability(universe - unsafe_promotion, masses)
    monotonicity_holds = probability(privacy_exceeded & consent_collapsed, masses) <= probability(
        audit_trigger, masses
    )

    summary = {
        "sample_space_size": len(omega),
        "probability_mass_total": sum(masses),
        "unsafe_promotion_event_size": len(unsafe_promotion),
        "privacy_exceeded_event_size": len(privacy_exceeded),
        "consent_collapsed_event_size": len(consent_collapsed),
        "audit_trigger_event_size": len(audit_trigger),
        "safe_stop_event_size": len(safe_stop),
        "unsafe_promotion_probability": probability(unsafe_promotion, masses),
        "audit_trigger_probability": probability(audit_trigger, masses),
        "safe_stop_probability": probability(safe_stop, masses),
        "union_identity_error": abs(union_identity_lhs - union_identity_rhs),
        "complement_identity_error": abs(complement_identity - 1.0),
        "monotonicity_holds": monotonicity_holds,
        "planning_rule": (
            "If the runtime history enters the audit-trigger event, the permitted plan is audit-only or "
            "narrowed output; if it enters unsafe-promotion, the hard claim is blocked."
        ),
        "interpretation": (
            "An event is a measurable set of histories. In this finite harness, every set is measurable, "
            "so runtime assurance can be phrased as event detection plus action selection."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "event_algebra_experiment_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
