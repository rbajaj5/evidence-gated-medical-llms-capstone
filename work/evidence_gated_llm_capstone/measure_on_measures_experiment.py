"""Finite measure-on-measures toy experiment.

A hospital, population, family, or evidence source can induce a probability
measure over runtime histories. A meta-measure over those source measures then
represents uncertainty about which source distribution an LLM-assisted workflow
is drawing from.
"""

from __future__ import annotations

import json
from pathlib import Path

from event_algebra_experiment import event, histories


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

SOURCE_MEASURES = {
    "us_ehr_like": {
        "surrogate_multiplier": 1.30,
        "mismatch_multiplier": 0.70,
        "privacy_exceeded_multiplier": 0.45,
        "consent_collapsed_multiplier": 0.50,
    },
    "genomeindia_like": {
        "surrogate_multiplier": 1.00,
        "mismatch_multiplier": 1.20,
        "privacy_exceeded_multiplier": 0.55,
        "consent_collapsed_multiplier": 0.80,
    },
    "latin_america_admixed_like": {
        "surrogate_multiplier": 1.10,
        "mismatch_multiplier": 1.35,
        "privacy_exceeded_multiplier": 0.60,
        "consent_collapsed_multiplier": 0.65,
    },
    "israel_biobank_like": {
        "surrogate_multiplier": 0.90,
        "mismatch_multiplier": 0.75,
        "privacy_exceeded_multiplier": 0.35,
        "consent_collapsed_multiplier": 0.45,
    },
}

META_MEASURE = {
    "us_ehr_like": 0.35,
    "genomeindia_like": 0.30,
    "latin_america_admixed_like": 0.20,
    "israel_biobank_like": 0.15,
}


def source_weight(history: dict[str, str], source: dict[str, float]) -> float:
    weight = 1.0
    if history["endpoint"] == "surrogate":
        weight *= source["surrogate_multiplier"]
    if history["population"] == "mismatch":
        weight *= source["mismatch_multiplier"]
    if history["privacy"] == "budget_exceeded":
        weight *= source["privacy_exceeded_multiplier"]
    if history["consent"] == "boundary_collapsed":
        weight *= source["consent_collapsed_multiplier"]
    if history["citation"] == "unverifiable":
        weight *= 0.40
    if history["action"] == "hard_claim":
        weight *= 0.55
    return weight


def normalize(weights: list[float]) -> list[float]:
    total = sum(weights)
    return [w / total for w in weights]


def probability(event_set: frozenset[int], masses: list[float]) -> float:
    return sum(masses[i] for i in event_set)


def total_variation(p: list[float], q: list[float]) -> float:
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q, strict=True))


def run() -> dict[str, object]:
    omega = histories()
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

    source_distributions: dict[str, list[float]] = {}
    source_summaries: dict[str, dict[str, float]] = {}
    for name, params in SOURCE_MEASURES.items():
        masses = normalize([source_weight(history, params) for history in omega])
        source_distributions[name] = masses
        source_summaries[name] = {
            "unsafe_promotion_probability": probability(unsafe_promotion, masses),
            "audit_trigger_probability": probability(audit_trigger, masses),
            "total_mass": probability(universe, masses),
        }

    mixture = [
        sum(META_MEASURE[name] * source_distributions[name][i] for name in SOURCE_MEASURES)
        for i in range(len(omega))
    ]
    mixture_summary = {
        "unsafe_promotion_probability": probability(unsafe_promotion, mixture),
        "audit_trigger_probability": probability(audit_trigger, mixture),
        "total_mass": probability(universe, mixture),
    }
    tv_to_mixture = {
        name: total_variation(masses, mixture)
        for name, masses in source_distributions.items()
    }

    summary = {
        "history_space_size": len(omega),
        "source_measure_count": len(SOURCE_MEASURES),
        "meta_measure_total_mass": sum(META_MEASURE.values()),
        "source_summaries": source_summaries,
        "mixture_summary": mixture_summary,
        "total_variation_to_mixture": tv_to_mixture,
        "max_source_tv_to_mixture": max(tv_to_mixture.values()),
        "source_with_highest_audit_probability": max(
            source_summaries,
            key=lambda name: source_summaries[name]["audit_trigger_probability"],
        ),
        "interpretation": (
            "A measure over measures represents source-distribution uncertainty. The assurance policy should be "
            "tested on each source measure and on the meta-measure mixture, because a safe-looking aggregate can "
            "still hide a high-risk source distribution."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "measure_on_measures_experiment_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
