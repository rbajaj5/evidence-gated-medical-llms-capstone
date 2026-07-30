"""Kelly-style runtime-budget experiment for evidence exposure.

This is a synthetic, nonclinical check. It uses the Kelly criterion only as a
log-utility analogy for bounded exposure to uncertain evidence signals. In the
capstone, the "stake" is not money; it is claim strength, clinician attention,
provenance budget, or action authority that should be spent proportionally and
with caps rather than all at once.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def kelly_fraction(p: float) -> float:
    """Even-money Kelly fraction."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be a probability")
    return max(0.0, 2.0 * p - 1.0)


def capped_kelly_fraction(p: float, cap: float = 0.25) -> float:
    if not 0.0 < cap <= 1.0:
        raise ValueError("cap must lie in (0, 1]")
    return min(cap, kelly_fraction(p))


def log_growth(p: float, fraction: float) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be a probability")
    if not 0.0 <= fraction < 1.0:
        raise ValueError("fraction must lie in [0, 1)")
    return p * math.log(1.0 + fraction) + (1.0 - p) * math.log(1.0 - fraction)


def all_in_expected_factor(p: float, rounds: int) -> float:
    return (2.0 * p) ** rounds


def all_in_ruin_probability(p: float, rounds: int) -> float:
    return 1.0 - p**rounds


def run() -> dict[str, object]:
    p = 2.0 / 3.0
    rounds = 20
    reliability_estimates = [0.49, 0.55, 0.67, 0.80, 0.92]
    uncapped = [kelly_fraction(x) for x in reliability_estimates]
    capped = [capped_kelly_fraction(x) for x in reliability_estimates]
    summary = {
        "source_pdf": "https://www.math.ucla.edu/~tom/stat596/Kelly.pdf",
        "ferguson_example_probability": p,
        "ferguson_example_rounds": rounds,
        "all_in_expected_factor": all_in_expected_factor(p, rounds),
        "all_in_ruin_probability": all_in_ruin_probability(p, rounds),
        "kelly_fraction_for_two_thirds": kelly_fraction(p),
        "kelly_log_growth_for_two_thirds": log_growth(p, kelly_fraction(p)),
        "reliability_estimates": reliability_estimates,
        "uncapped_kelly_exposures": uncapped,
        "capped_kelly_exposures": capped,
        "cap": 0.25,
        "zero_exposure_for_unfavorable_or_uncertain_signal": uncapped[0] == 0.0,
        "capped_policy_limits_high_confidence_signal": capped[-1] < uncapped[-1],
        "runtime_interpretation": (
            "A runtime monitor should not maximize expected helpfulness by going all-in on a "
            "favorable-looking signal. It should expose claim strength proportionally, and cap "
            "that exposure until verification, endpoint, provenance, and authority gates clear."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "kelly_runtime_budget_experiment_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
