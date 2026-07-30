"""Toy uniform-witness sampling experiment for evidence claims.

Bellare, Goldreich, and Petrank study uniform generation of NP-witnesses using
an NP oracle. This file uses only a tiny finite analogy: for a requested medical
claim relation, enumerate all admissible evidence witnesses and compare a
uniform witness distribution with a biased "strong-looking first" generator.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

ENDPOINTS = ("hard_outcome", "validated_surrogate", "surrogate", "process")
DESIGNS = ("pragmatic_rct", "rct", "validation", "observational", "case")
POPULATIONS = ("match", "plausible", "mismatch")
PROVENANCE = ("verified", "local_audit", "unverifiable")


def admissible_witness(witness: tuple[str, str, str, str]) -> bool:
    endpoint, design, population, provenance = witness
    if provenance == "unverifiable" or population == "mismatch":
        return False
    if endpoint == "hard_outcome":
        return design == "pragmatic_rct" and population == "match" and provenance == "verified"
    if endpoint == "validated_surrogate":
        return design in {"pragmatic_rct", "rct"} and provenance == "verified"
    if endpoint == "surrogate":
        return design in {"pragmatic_rct", "rct", "validation", "observational"}
    return design in {"validation", "case"}


def claim_strength(witness: tuple[str, str, str, str]) -> int:
    endpoint, design, population, provenance = witness
    return (
        {"hard_outcome": 4, "validated_surrogate": 3, "surrogate": 2, "process": 1}[endpoint]
        + {"pragmatic_rct": 3, "rct": 2, "validation": 1, "observational": 0, "case": 0}[design]
        + {"match": 1, "plausible": 0, "mismatch": -3}[population]
        + {"verified": 1, "local_audit": 0, "unverifiable": -5}[provenance]
    )


def total_variation(p: dict[tuple[str, str, str, str], float], q: dict[tuple[str, str, str, str], float]) -> float:
    keys = set(p).union(q)
    return 0.5 * sum(abs(p.get(key, 0.0) - q.get(key, 0.0)) for key in keys)


def run() -> dict[str, object]:
    universe = list(itertools.product(ENDPOINTS, DESIGNS, POPULATIONS, PROVENANCE))
    admissible = [w for w in universe if admissible_witness(w)]
    uniform = {w: 1.0 / len(admissible) for w in admissible}

    # A deliberately bad evaluator: only the top five strongest-looking
    # witnesses are repeatedly surfaced to reviewers.
    top_five = sorted(admissible, key=lambda w: (-claim_strength(w), w))[:5]
    biased = {w: 1.0 / len(top_five) for w in top_five}
    endpoint_counts = Counter(w[0] for w in admissible)
    top_endpoint_counts = Counter(w[0] for w in top_five)

    summary = {
        "source_pdf": "https://cseweb.ucsd.edu/~mihir/papers/ug.pdf",
        "universe_size": len(universe),
        "admissible_witness_count": len(admissible),
        "biased_top_witness_count": len(top_five),
        "uniform_endpoint_distribution": {
            endpoint: endpoint_counts[endpoint] / len(admissible) for endpoint in ENDPOINTS
        },
        "biased_endpoint_distribution": {
            endpoint: top_endpoint_counts[endpoint] / len(top_five) for endpoint in ENDPOINTS
        },
        "uniform_hard_outcome_fraction": endpoint_counts["hard_outcome"] / len(admissible),
        "biased_hard_outcome_fraction": top_endpoint_counts["hard_outcome"] / len(top_five),
        "variation_distance_from_uniform": total_variation(uniform, biased),
        "top_five_witnesses": [
            {"endpoint": w[0], "design": w[1], "population": w[2], "provenance": w[3]} for w in top_five
        ],
        "runtime_interpretation": (
            "Evidence evaluation should enumerate or sample admissible witnesses under an explicit relation; "
            "surfacing only strong-looking witnesses biases the perceived claim space."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "uniform_witness_sampling_experiment_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
