"""Finite tail/maximal-inequality probe for runtime assurance.

The Sheffield lecture motivates two useful distinctions for medical LLM
monitoring: tail properties are long-run/path properties, and maximal
inequalities bound the chance that a cumulative process crosses a boundary
before the terminal state is inspected.

This exact finite enumeration uses a 12-step mean-zero Rademacher process as a
toy runtime-drift signal. It is synthetic and nonclinical.
"""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def run() -> dict[str, object]:
    steps = 12
    threshold = 6
    paths = list(itertools.product((-1, 1), repeat=steps))
    total = len(paths)

    crossing_count = 0
    terminal_exceed_count = 0
    returned_inside_after_crossing_count = 0
    max_abs_values: dict[int, int] = {}

    for path in paths:
        partial = 0
        max_abs = 0
        crossed = False
        for increment in path:
            partial += increment
            max_abs = max(max_abs, abs(partial))
            if max_abs >= threshold:
                crossed = True
        terminal_exceeds = abs(partial) >= threshold
        crossing_count += int(crossed)
        terminal_exceed_count += int(terminal_exceeds)
        returned_inside_after_crossing_count += int(crossed and not terminal_exceeds)
        max_abs_values[max_abs] = max_abs_values.get(max_abs, 0) + 1

    crossing_probability = Fraction(crossing_count, total)
    terminal_exceed_probability = Fraction(terminal_exceed_count, total)
    returned_inside_probability = Fraction(returned_inside_after_crossing_count, total)
    total_variance = steps
    kolmogorov_bound = Fraction(total_variance, threshold * threshold)

    assert crossing_probability <= kolmogorov_bound
    assert crossing_probability > terminal_exceed_probability

    summary = {
        "experiment": "tail_maximal_inequality_runtime_probe",
        "clinical_status": "synthetic mathematical analogy only",
        "steps": steps,
        "path_count": total,
        "increment_model": "independent Rademacher +/-1",
        "mean_zero": True,
        "total_variance": total_variance,
        "threshold": threshold,
        "kolmogorov_bound": str(kolmogorov_bound),
        "kolmogorov_bound_float": float(kolmogorov_bound),
        "exact_crossing_probability": str(crossing_probability),
        "exact_crossing_probability_float": float(crossing_probability),
        "terminal_exceed_probability": str(terminal_exceed_probability),
        "terminal_exceed_probability_float": float(terminal_exceed_probability),
        "returned_inside_after_crossing_probability": str(returned_inside_probability),
        "returned_inside_after_crossing_probability_float": float(returned_inside_probability),
        "bound_holds": True,
        "crossing_exceeds_terminal_check": True,
        "tail_event_interpretation": "Long-run safety properties should be treated as path/tail-style events, not certified from one finite prefix.",
        "max_abs_histogram": {str(k): v for k, v in sorted(max_abs_values.items())},
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "tail_maximal_inequality_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
