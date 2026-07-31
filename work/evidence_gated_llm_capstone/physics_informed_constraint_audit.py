"""Physics-informed constraint audit for medical LLM assurance.

Inspired by PIKS (Bona-Pellissier et al., 2026), this synthetic experiment
separates empirical fit from structural consistency. In the capstone setting, a
model may fit observed medical text or measurements while violating a known
linear constraint, source-domain boundary, or misspecification warning.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SOURCE = "https://arxiv.org/abs/2607.27062"


@dataclass(frozen=True)
class ConstraintCase:
    case_id: str
    label: str
    empirical_fit: float
    constraint_residual: float
    linear_constraint: bool
    universal_kernel: bool
    misspecified_target: bool
    boundary_data_only: bool
    nonlinear_or_unmodeled_constraint: bool
    clinical_analogy: str


CASES = [
    ConstraintCase(
        case_id="P01",
        label="High-fit unconstrained text model",
        empirical_fit=0.94,
        constraint_residual=0.38,
        linear_constraint=False,
        universal_kernel=False,
        misspecified_target=True,
        boundary_data_only=False,
        nonlinear_or_unmodeled_constraint=False,
        clinical_analogy="A fluent LLM summary fits notes but violates a known physiologic invariant.",
    ),
    ConstraintCase(
        case_id="P02",
        label="Physics-informed model with large residual",
        empirical_fit=0.90,
        constraint_residual=0.21,
        linear_constraint=True,
        universal_kernel=False,
        misspecified_target=False,
        boundary_data_only=False,
        nonlinear_or_unmodeled_constraint=False,
        clinical_analogy="A physiology-aware predictor still leaves an unsafe conservation-law residual.",
    ),
    ConstraintCase(
        case_id="P03",
        label="PIKS-style linear constraint with universal kernel",
        empirical_fit=0.89,
        constraint_residual=0.03,
        linear_constraint=True,
        universal_kernel=True,
        misspecified_target=False,
        boundary_data_only=False,
        nonlinear_or_unmodeled_constraint=False,
        clinical_analogy="A method-level claim that linear constraints are being satisfied in a synthetic monitor.",
    ),
    ConstraintCase(
        case_id="P04",
        label="Misspecified rough target outside native RKHS",
        empirical_fit=0.84,
        constraint_residual=0.06,
        linear_constraint=True,
        universal_kernel=True,
        misspecified_target=True,
        boundary_data_only=False,
        nonlinear_or_unmodeled_constraint=False,
        clinical_analogy="A noisy or rough patient trajectory where universality does not remove rate uncertainty.",
    ),
    ConstraintCase(
        case_id="P05",
        label="Boundary measurements with interior differential constraint",
        empirical_fit=0.82,
        constraint_residual=0.04,
        linear_constraint=True,
        universal_kernel=True,
        misspecified_target=False,
        boundary_data_only=True,
        nonlinear_or_unmodeled_constraint=False,
        clinical_analogy="Boundary observations plus interior mechanistic constraints in a synthetic physiology model.",
    ),
    ConstraintCase(
        case_id="P06",
        label="Nonlinear or unmodeled medical mechanism",
        empirical_fit=0.88,
        constraint_residual=0.05,
        linear_constraint=False,
        universal_kernel=True,
        misspecified_target=True,
        boundary_data_only=False,
        nonlinear_or_unmodeled_constraint=True,
        clinical_analogy="A nonlinear disease mechanism is being forced into a linear-constraint audit.",
    ),
]


def audit_case(case: ConstraintCase) -> dict[str, object]:
    if case.nonlinear_or_unmodeled_constraint:
        action = "ABSTAIN_CONSTRAINT_SCOPE"
        reason = "PIKS-style guarantees for linear constraints do not cover the stated mechanism."
    elif not case.linear_constraint:
        action = "REQUIRE_STRUCTURAL_CONSTRAINT"
        reason = "High empirical fit is not enough when no auditable structural constraint is specified."
    elif case.constraint_residual > 0.10:
        action = "BLOCK_HIGH_RESIDUAL"
        reason = "The structural residual remains too large for an assurance claim."
    elif case.boundary_data_only:
        action = "ALLOW_METHOD_CLAIM_WITH_BOUNDARY_AUDIT"
        reason = "Boundary observations and interior constraints are method evidence, not clinical validation."
    elif case.misspecified_target:
        action = "ALLOW_WITH_MISSPECIFICATION_STRESS_TEST"
        reason = "Universal kernels can support consistency while rough targets still require rate/stress audits."
    elif case.universal_kernel:
        action = "ALLOW_CONSTRAINT_CONSISTENCY_CLAIM"
        reason = "The synthetic case supports a bounded structural-consistency claim."
    else:
        action = "REQUIRE_KERNEL_OR_THEORY_SUPPORT"
        reason = "A physics-informed term without theory support needs additional validation."

    return {
        **asdict(case),
        "fit_gap": round(1.0 - case.empirical_fit, 3),
        "residual_within_budget": case.constraint_residual <= 0.10,
        "action": action,
        "reason": reason,
    }


def run() -> dict[str, object]:
    rows = [audit_case(case) for case in CASES]
    action_counts: dict[str, int] = {}
    for row in rows:
        action_counts[row["action"]] = action_counts.get(row["action"], 0) + 1

    summary = {
        "source": SOURCE,
        "case_count": len(rows),
        "constraint_residual_budget": 0.10,
        "action_counts": action_counts,
        "rows": rows,
        "capstone_interpretation": (
            "Physics-informed evidence can support structural consistency claims, "
            "especially for auditable linear constraints, but it does not by itself "
            "authorize patient-outcome or treatment claims."
        ),
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "physics_informed_constraint_audit_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
