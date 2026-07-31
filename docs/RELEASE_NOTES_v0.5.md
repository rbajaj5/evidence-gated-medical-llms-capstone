# Release Notes: v0.5 Physics-Informed Constraint Audit

Adds a synthetic structural-consistency audit inspired by:

Bona-Pellissier, J., Meanti, G., Santacesaria, M., & Rosasco, L. (2026). *PIKS: Universal Physics-Informed Kernel Methods*. https://arxiv.org/abs/2607.27062

## Added

- `physics_informed_constraint_audit.py`
- `test_physics_informed_constraint_audit.py`
- `physics_informed_constraint_audit_summary.json`

## Interpretation

The audit separates:

- empirical fit,
- linear structural constraints,
- constraint residuals,
- universal-kernel support,
- misspecified or rough targets,
- boundary-only measurements with interior constraints,
- and nonlinear or unmodeled mechanisms outside the stated guarantee.

The capstone implication is narrow: physics-informed evidence can support bounded structural-consistency claims, but it does not by itself authorize patient-outcome, diagnosis, or treatment claims.

## Validation

Local validation before push:

```text
133 passed
```

## Boundary

No clinical behavior changed. This is a synthetic method-governance audit and does not introduce patient data, diagnosis, treatment recommendation, or clinical-effectiveness claims.
