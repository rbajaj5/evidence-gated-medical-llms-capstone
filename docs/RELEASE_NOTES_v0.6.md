# Release Notes: v0.6 Proxy/Mass Counterexample Audit

Adds a synthetic proxy-governance audit inspired by:

Li, L., & Xia, M. (2026). *A counterexample to the zero-mass conjecture*. https://arxiv.org/abs/2607.26549

## Added

- `proxy_mass_counterexample_audit.py`
- `test_proxy_mass_counterexample_audit.py`
- `proxy_mass_counterexample_audit_summary.json`

## Interpretation

The audit separates:

- local proxy strength,
- residual mass or residual risk,
- isolated-event concentration,
- added regularity or governance structure,
- directional witness evidence,
- and monotone-limit/collapse behavior.

The capstone implication is narrow: absence of a local proxy signal should not be converted into a no-risk medical claim unless the residual-risk channel has been independently audited.

## Validation

Local validation before push:

```text
139 passed
```

## Boundary

No clinical behavior changed. This is a synthetic proxy-governance audit and does not introduce patient data, diagnosis, treatment recommendation, or clinical-effectiveness claims.
