"""Exact counterexample probe for a simulation-supported matrix conjecture.

This is a bounded mathematical analogy for the capstone: simulations can miss
small adversarial counterexamples, so runtime assurance should include exact
stress cases where possible. It does not make a clinical claim.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

Matrix = tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]


def mat_add(*mats: Matrix) -> Matrix:
    return tuple(
        tuple(sum(mat[i][j] for mat in mats) for j in range(2)) for i in range(2)
    )  # type: ignore[return-value]


def mat_mul(a: Matrix, b: Matrix) -> Matrix:
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)) for i in range(2)
    )  # type: ignore[return-value]


def scalar_mul(c: Fraction, a: Matrix) -> Matrix:
    return tuple(tuple(c * a[i][j] for j in range(2)) for i in range(2))  # type: ignore[return-value]


def add_identity(a: Matrix, eps: Fraction) -> Matrix:
    return (
        (a[0][0] + eps, a[0][1]),
        (a[1][0], a[1][1] + eps),
    )


def as_strings(a: Matrix) -> list[list[str]]:
    return [[str(x) for x in row] for row in a]


I: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
A: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)))
B: Matrix = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(1)))
C: Matrix = (
    (Fraction(1, 2), Fraction(-1, 2)),
    (Fraction(-1, 2), Fraction(1, 2)),
)
D: Matrix = (
    (Fraction(1, 2), Fraction(1, 2)),
    (Fraction(1, 2), Fraction(1, 2)),
)


def conjecture_left_matrix(a: Matrix, b: Matrix, c: Matrix, d: Matrix) -> Matrix:
    bc_plus_cb = mat_add(mat_mul(b, c), mat_mul(c, b))
    return mat_add(mat_mul(mat_mul(a, bc_plus_cb), d), mat_mul(mat_mul(d, bc_plus_cb), a))


def run() -> dict[str, object]:
    x = conjecture_left_matrix(A, B, C, D)
    expected_x: Matrix = (
        (Fraction(-1, 2), Fraction(-1, 4)),
        (Fraction(-1, 4), Fraction(0)),
    )
    assert x == expected_x

    s = mat_add(A, B, C, D)
    assert s == scalar_mul(Fraction(2), I)
    rhs = Fraction(1, 4)
    # X has eigenvalues (-1 +/- sqrt(2)) / 4, so the spectral norm is
    # (1 + sqrt(2)) / 4 and the violation factor is 1 + sqrt(2).
    lhs_float = (1 + math.sqrt(2)) / 4
    violation_factor = 1 + math.sqrt(2)
    assert lhs_float > float(rhs)

    eps = Fraction(1, 10)
    Ap = add_identity(A, eps)
    Bp = add_identity(B, eps)
    Cp = add_identity(C, eps)
    Dp = add_identity(D, eps)
    xp = conjecture_left_matrix(Ap, Bp, Cp, Dp)
    expected_xp: Matrix = (
        (Fraction(-627, 1250), Fraction(-3, 10)),
        (Fraction(-3, 10), Fraction(123, 1250)),
    )
    assert xp == expected_xp
    sp = mat_add(Ap, Bp, Cp, Dp)
    assert sp == scalar_mul(Fraction(12, 5), I)
    pd_rhs = Fraction(324, 625)
    pd_margin_float = 3 * math.sqrt(2) / 10 - Fraction(198, 625)
    assert pd_margin_float > 0

    summary = {
        "experiment": "noncommutative_amgm_counterexample",
        "clinical_status": "mathematical analogy only",
        "purpose": "Exact adversarial stress test showing why simulation-supported conjectures still need counterexample search.",
        "dimension": 2,
        "rank_one_projectors": True,
        "dimension_one_scalar_case_satisfies_bound": True,
        "original_left_matrix": as_strings(x),
        "original_rhs": str(rhs),
        "original_lhs_exact": "(1 + sqrt(2)) / 4",
        "violation_factor_exact": "1 + sqrt(2)",
        "violation_factor_float": violation_factor,
        "positive_definite_epsilon": str(eps),
        "positive_definite_left_matrix": as_strings(xp),
        "positive_definite_rhs": str(pd_rhs),
        "positive_definite_lhs_exact": "126/625 + 3*sqrt(2)/10",
        "positive_definite_margin_exact": "3*sqrt(2)/10 - 198/625",
        "positive_definite_margin_float": float(pd_margin_float),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "noncommutative_amgm_counterexample_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
