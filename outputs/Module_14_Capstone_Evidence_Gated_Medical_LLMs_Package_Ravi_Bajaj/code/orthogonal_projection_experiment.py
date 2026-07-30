"""Synthetic orthogonal-projection experiment for nuisance/confounding control.

This is not a clinical model. It checks a runtime-assurance pattern inspired by
restricted regression/spatial-confounding discussions: before a latent component
is interpreted as independent signal, remove the part lying in the design
matrix's column space.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*matrix, strict=True)]


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(a * b for a, b in zip(row, vector, strict=True)) for row in matrix]


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def norm(vector: list[float]) -> float:
    return math.sqrt(dot(vector, vector))


def solve_2x2(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    (a, b), (c, d) = matrix
    det = a * d - b * c
    if abs(det) < 1e-12:
        raise ValueError("singular 2x2 system")
    return [(d * rhs[0] - b * rhs[1]) / det, (-c * rhs[0] + a * rhs[1]) / det]


def project_onto_design(design: list[list[float]], vector: list[float]) -> tuple[list[float], list[float]]:
    xt = transpose(design)
    xtx = [[dot(col_i, col_j) for col_j in xt] for col_i in xt]
    xty = [dot(col, vector) for col in xt]
    coef = solve_2x2(xtx, xty)
    fitted = matvec(design, coef)
    residual = [y - yhat for y, yhat in zip(vector, fitted, strict=True)]
    return fitted, residual


def max_abs_design_correlation(design: list[list[float]], vector: list[float]) -> float:
    return max(abs(dot(col, vector)) for col in transpose(design))


def run() -> dict[str, object]:
    rng = random.Random(20260728)
    n = 48
    x = [((i - (n - 1) / 2) / n) for i in range(n)]
    design = [[1.0, xi] for xi in x]

    # A latent component with a confounded trend plus independent oscillation.
    alpha = [
        0.8 + 1.7 * xi + 0.35 * math.sin(2 * math.pi * 3 * (i / n)) + 0.03 * rng.uniform(-1, 1)
        for i, xi in enumerate(x)
    ]
    fitted, alpha_perp = project_onto_design(design, alpha)

    before = max_abs_design_correlation(design, alpha)
    after = max_abs_design_correlation(design, alpha_perp)
    summary = {
        "sample_count": n,
        "design_columns": 2,
        "alpha_norm_before_projection": norm(alpha),
        "projected_component_norm": norm(fitted),
        "alpha_norm_after_projection": norm(alpha_perp),
        "max_abs_design_inner_product_before": before,
        "max_abs_design_inner_product_after": after,
        "orthogonality_passed": after < 1e-10,
        "projection_removed_design_signal": norm(fitted) > 0.5,
        "runtime_interpretation": (
            "A latent or residual model component should not be interpreted as independent clinical signal "
            "until its projection onto known design covariates has been removed or audited."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "orthogonal_projection_experiment_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
