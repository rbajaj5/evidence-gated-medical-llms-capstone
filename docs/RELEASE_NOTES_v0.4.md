# Release Notes: v0.4 Oracle Consistency Audit

Adds a synthetic oracle-consistency audit inspired by:

Kong, B., Ram, T., & Yu, T. Y. (2026). *AlphaZero in Sparsely Rewarded Games: Limits and Auxiliary Supervision*. https://arxiv.org/abs/2607.08984

## Added

- `oracle_consistency_audit.py`
- `test_oracle_consistency_audit.py`
- `oracle_consistency_audit_summary.json`

## Interpretation

The audit separates:

- strong aggregate performance,
- exact full-trace oracle consistency,
- sampled-state oracle consistency,
- representation-only context expansion,
- and auxiliary oracle-derived supervision.

The capstone implication is narrow and useful: a medical LLM can score well overall while still making non-oracle reasoning moves along a claim trajectory. Runtime assurance should therefore monitor claim steps, not only final answer quality.

## Validation

Local validation before push:

```text
126 passed
```

## Boundary

No clinical behavior changed. This is a synthetic assurance audit and does not introduce patient data, diagnosis, treatment recommendation, or clinical-effectiveness claims.
